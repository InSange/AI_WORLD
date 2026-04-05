"""
WorldAI World Engine
=====================
시뮬레이션의 중심 엔진. tick_world()가 호출될 때마다 1틱을 진행한다.

틱 처리 순서:
  1. 시간 진행 (계절 / 연도 체크)
  2. 인구 변화 (계절 보정 포함)
  3. 외교 자연 감쇠
  4. 종족 행동 결정 (RaceAgent)
  5. 행동 실행 → 외교 수치 변화
  6. 기술 성장 처리
  7. 이벤트 기록
"""
from __future__ import annotations

import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

# 프로젝트 루트를 sys.path에 추가
_APP_ROOT = Path(__file__).parent.parent.parent          # apps/worldai/
_PROJECT_ROOT = _APP_ROOT.parent.parent                  # WorldAI/
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))

from src.core.models import (
    Season, RaceState, AffinityLevel, Action, ActionType,
    EventLog, TickResult, DayPhase, TimeConfig,
)
from src.core.diplomacy import DiplomacySystem
from src.core.race_agent import RaceAgent, execute_action
from src.core.event_system import EventSystem


# ── 계절 설정 ───────────────────────────────

SEASONS = [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]

# ── 기본 TimeConfig (world YAML에서 오버라이드 가능) ─
_DEFAULT_TIME = TimeConfig()  # 1틱=1시간, 1계절=2160틱

# 계절별 낮 시간 범위 (시작시각, 종료시각)
_DAY_HOURS: dict[Season, tuple[int, int]] = {
    Season.SPRING: (6,  18),   # 12시간 낮
    Season.SUMMER: (4,  20),   # 16시간 낮
    Season.AUTUMN: (6,  18),   # 12시간 낮
    Season.WINTER: (8,  16),   #  8시간 낮
}

# 계절별 인구 성장 배수
SEASON_POP_MODIFIER: dict[Season, float] = {
    Season.SPRING: 1.10,
    Season.SUMMER: 1.00,
    Season.AUTUMN: 0.98,
    Season.WINTER: 0.80,
}

# 계절별 기술 연구 배수
SEASON_TECH_MODIFIER: dict[Season, float] = {
    Season.SPRING: 1.00,
    Season.SUMMER: 0.95,
    Season.AUTUMN: 1.05,
    Season.WINTER: 1.15,
}

# 종족별 시간대 활성도 배율 (전투력·이벤트 확률에 곱해짐)
# 값 없으면 1.0 (중립)
RACE_PHASE_MODIFIER: dict[str, dict[DayPhase, float]] = {
    "human":     {DayPhase.DEEP_NIGHT: 0.5, DayPhase.DAWN: 0.8, DayPhase.DAY: 1.0, DayPhase.DUSK: 0.9,  DayPhase.NIGHT: 0.6},
    "elf":       {DayPhase.DEEP_NIGHT: 0.6, DayPhase.DAWN: 1.2, DayPhase.DAY: 0.8, DayPhase.DUSK: 1.2,  DayPhase.NIGHT: 1.0},
    "dwarf":     {DayPhase.DEEP_NIGHT: 0.7, DayPhase.DAWN: 0.9, DayPhase.DAY: 1.0, DayPhase.DUSK: 0.9,  DayPhase.NIGHT: 0.8},
    "orc":       {DayPhase.DEEP_NIGHT: 1.0, DayPhase.DAWN: 0.7, DayPhase.DAY: 0.8, DayPhase.DUSK: 1.1,  DayPhase.NIGHT: 1.3},
    "halfling":  {DayPhase.DEEP_NIGHT: 0.4, DayPhase.DAWN: 0.9, DayPhase.DAY: 1.0, DayPhase.DUSK: 1.0,  DayPhase.NIGHT: 0.7},
    "beastman":  {DayPhase.DEEP_NIGHT: 0.9, DayPhase.DAWN: 1.1, DayPhase.DAY: 0.9, DayPhase.DUSK: 1.1,  DayPhase.NIGHT: 1.0},
    "fairy":     {DayPhase.DEEP_NIGHT: 0.8, DayPhase.DAWN: 1.0, DayPhase.DAY: 0.7, DayPhase.DUSK: 1.0,  DayPhase.NIGHT: 1.3},
    "dragon":    {DayPhase.DEEP_NIGHT: 0.8, DayPhase.DAWN: 1.3, DayPhase.DAY: 0.7, DayPhase.DUSK: 1.3,  DayPhase.NIGHT: 1.0},
    "undead":    {DayPhase.DEEP_NIGHT: 2.0, DayPhase.DAWN: 0.3, DayPhase.DAY: 0.2, DayPhase.DUSK: 0.8,  DayPhase.NIGHT: 1.5},
    "elemental": {DayPhase.DEEP_NIGHT: 1.0, DayPhase.DAWN: 1.0, DayPhase.DAY: 1.0, DayPhase.DUSK: 1.0,  DayPhase.NIGHT: 1.0},
    "golem":     {DayPhase.DEEP_NIGHT: 1.0, DayPhase.DAWN: 1.0, DayPhase.DAY: 1.0, DayPhase.DUSK: 1.0,  DayPhase.NIGHT: 1.0},
    "angel_demon":{DayPhase.DEEP_NIGHT: 0.3, DayPhase.DAWN: 1.4, DayPhase.DAY: 1.2, DayPhase.DUSK: 1.1, DayPhase.NIGHT: 0.5},
}


def get_race_phase_modifier(race_id: str, phase: DayPhase) -> float:
    """종족 + 시간대 활성도 배율 반환 (없으면 1.0)"""
    return RACE_PHASE_MODIFIER.get(race_id, {}).get(phase, 1.0)


# ── World Engine ─────────────────────────────

@dataclass
class World:
    """
    시뮬레이션 세계 상태.
    - tick_world() 로 1틱씩 진행
    - from_config() 클래스 메서드로 YAML 설정에서 생성
    """

    id: str
    name: str
    description: str = ""
    tick: int = 0
    year: int = 1
    _season_idx: int = field(default=0, repr=False)

    # 시간 설정 (YAML에서 로드, 기본: 1틱=1시간)
    time_config: TimeConfig = field(default_factory=TimeConfig)

    races: dict[str, RaceState] = field(default_factory=dict)
    diplomacy: DiplomacySystem = field(default_factory=DiplomacySystem)
    event_log: list[EventLog] = field(default_factory=list)

    # 종족별 AI 에이전트 (race_id → RaceAgent)
    _agents: dict[str, RaceAgent] = field(default_factory=dict, repr=False)

    # 세계 이벤트 시스템
    _event_system: EventSystem = field(default_factory=EventSystem, repr=False)

    # ── 프로퍼티 ─────────────────────

    @property
    def season(self) -> Season:
        return SEASONS[self._season_idx % 4]

    @property
    def hour_of_day(self) -> int:
        """현재 게임 내 시각 (0~23). 1틱=1시간 기준."""
        return self.tick % self.time_config.ticks_per_day

    @property
    def day_phase(self) -> DayPhase:
        """현재 시간대 (DEEP_NIGHT / DAWN / DAY / DUSK / NIGHT)"""
        return DayPhase.from_hour(self.hour_of_day)

    @property
    def is_daytime(self) -> bool:
        """현재 낮인지 (계절별 일조 시간 기준)"""
        start, end = _DAY_HOURS[self.season]
        return start <= self.hour_of_day < end

    @property
    def active_races(self) -> list[RaceState]:
        return [r for r in self.races.values() if r.is_alive]

    # ── 생성자 ───────────────────────

    @classmethod
    def from_config(cls, world_id: str = "asteria") -> "World":
        """YAML 설정에서 World 생성"""
        from src.config.loader import load_world, load_all_races

        world_cfg = load_world(world_id)
        world = cls(
            id=world_cfg.id,
            name=world_cfg.name,
            description=world_cfg.description,
        )

        all_races = load_all_races()
        starting = world_cfg.raw.get("starting_races", [])

        for start in starting:
            race_id = start.get("id", "")
            if race_id not in all_races:
                print(f"  ⚠️  종족 '{race_id}' 설정 파일 없음, 건너뜀")
                continue

            cfg = all_races[race_id]
            state = RaceState(
                id=race_id,
                name=cfg.name,
                category=cfg.category,
                tier=cfg.tier,
                population=float(start.get("population", cfg.stats.max_population * 0.1)),
                military_strength=float(cfg.stats.military_strength),
                magic_affinity=float(cfg.stats.magic_affinity),
                technology_level=float(start.get("tech_level", cfg.stats.technology_level)),
                max_population=cfg.stats.max_population,
                growth_rate=cfg.stats.growth_rate,
                aggression=cfg.behavior.aggression,
                expansion_drive=cfg.behavior.expansion_drive,
                alliance_tendency=cfg.behavior.alliance_tendency,
                trade_focus=cfg.behavior.trade_focus,
                isolationism=cfg.behavior.isolationism,
                trait_ids=[t.id for t in cfg.special_traits],
            )
            world.races[race_id] = state
            world._agents[race_id] = RaceAgent(race_id)

            # 외교 초기값 로드
            world.diplomacy.load_defaults(race_id, [
                {"target": d.target, "affinity": d.affinity}
                for d in cfg.diplomacy_defaults
            ])

        print(f"✅ World '{world.name}' 생성 완료: {len(world.races)}개 종족")
        return world

    # ── 메인 틱 루프 ─────────────────

    def tick_world(self) -> TickResult:
        """1틱 진행. 모든 시스템을 순서대로 실행한다."""
        self.tick += 1
        events: list[EventLog] = []
        pop_changes: dict[str, float] = {}
        affinity_changes: list[dict] = []

        ticks_per_season = self.time_config.ticks_per_season

        # 1. 시간 진행 ─────────────────────────────
        if self.tick % ticks_per_season == 0:
            self._season_idx = (self._season_idx + 1) % 4
            if self._season_idx == 0:
                self.year += 1
            season_event = EventLog(
                tick=self.tick,
                event_type="SEASON_CHANGE",
                title=f"[계절] {self.season.display()} 시작 (Year {self.year})",
                description=f"새 계절이 시작됩니다. 계절 효과가 적용됩니다.",
                affected_races=[r.id for r in self.active_races],
            )
            events.append(season_event)

        # 낮/밤 페이즈 로깅 (하루 시작 = 00시)
        if self.hour_of_day == 0:
            events.append(EventLog(
                tick=self.tick,
                event_type="DAY_START",
                title=f"[시각] 새벽 00시 (Year {self.year} {self.season.display()})",
                description=f"낮/밤 사이클: {'낮' if self.is_daytime else '밤'} ({self.day_phase.display()})",
                affected_races=[],
            ))

        pop_mod  = SEASON_POP_MODIFIER[self.season]
        tech_mod = SEASON_TECH_MODIFIER[self.season]

        # 2. 인구 변화 ─────────────────────────────
        for race in self.active_races:
            old_pop = race.population
            effective_growth = 1.0 + (race.growth_rate - 1.0) * pop_mod
            # 언데드: 자연 번식 없음
            if race.growth_rate <= 1.0:
                effective_growth = 1.0
            # soft cap: max_population을 살짝 넘어갈 수 있음 (overflow 이벤트가 처리)
            raw_pop = race.population * effective_growth
            race.population = min(float(race.max_population) * 1.02, raw_pop)
            pop_changes[race.id] = race.population - old_pop

        # 2b. 세계 이벤트 (인구 과밀·습격·몬스터·역병) ─
        world_events = self._event_system.tick(
            races=self.races,
            diplomacy_adjust=self.diplomacy.adjust,
            tick=self.tick,
        )
        events.extend(world_events)

        # 3. 외교 자연 감쇠 ────────────────────────
        self.diplomacy.decay_all(decay_rate=0.001)

        # 4 & 5. 종족 행동 결정 + 실행 ─────────────
        phase = self.day_phase
        actions: list[Action] = []
        for race in self.active_races:
            agent = self._agents.get(race.id)
            if agent is None:
                continue
            # 시간대 활성도 배율 적용 → 낮에 활동적인 종족은 밤에 행동 안 함
            phase_mod = get_race_phase_modifier(race.id, phase)
            if phase_mod < 0.4:
                continue  # 활성도 너무 낮으면 이번 틱 행동 스킵
            action = agent.decide_action(
                race=race,
                all_races=self.races,
                get_affinity=self.diplomacy.get,
            )
            actions.append(action)

        for action in actions:
            evt = execute_action(
                action=action,
                races=self.races,
                diplomacy_adjust=self.diplomacy.adjust,
                tick=self.tick,
            )
            if evt:
                events.append(evt)
                affinity_changes.append(evt.affinity_changes)

        # 6. 기술 성장 (계절 보정) ─────────────────
        for race in self.active_races:
            if race.technology_level < 100:
                # 기본 성장 + 계절 보정 (실제 연구 action과 별개로 소폭 자연 성장)
                race.technology_level = min(
                    100.0,
                    race.technology_level + 0.002 * tech_mod,
                )

        # 7. 이벤트 기록 ───────────────────────────
        self.event_log.extend(events)

        return TickResult(
            tick=self.tick,
            season=self.season,
            year=self.year,
            events=events,
            population_changes=pop_changes,
            affinity_changes=affinity_changes,
        )

    # ── 상태 조회 ────────────────────

    def get_state_summary(self) -> dict[str, Any]:
        """현재 전체 세계 상태를 dict로 반환 (API / 대시보드용)"""
        relations: dict[str, dict] = {}
        for (a, b), val in self.diplomacy.get_all().items():
            relations[f"{a}→{b}"] = {
                "value": round(val, 1),
                "level": AffinityLevel.from_value(val).value,
                "display": AffinityLevel.from_value(val).display(),
            }

        return {
            "tick": self.tick,
            "year": self.year,
            "season": self.season.value,
            "season_display": self.season.display(),
            "races": {
                r.id: {
                    "name": r.name,
                    "tier": r.tier,
                    "category": r.category,
                    "population": round(r.population),
                    "military_strength": round(r.military_strength, 1),
                    "technology_level": round(r.technology_level, 1),
                    "magic_affinity": round(r.magic_affinity, 1),
                    "morale": round(r.morale, 2),
                    "territory_count": r.territory_count,
                }
                for r in self.active_races
            },
            "diplomacy": relations,
            "recent_events": [
                e.to_dict() for e in self.event_log[-20:]
            ],
        }

    def print_status(self) -> None:
        """콘솔 출력용 현황 요약"""
        print(f"\n{'='*55}")
        print(f" Tick {self.tick:>5} | Year {self.year} | {self.season.display()}")
        print(f"{'='*55}")
        for r in sorted(self.active_races, key=lambda x: -x.population):
            bar = "█" * int(r.population / r.max_population * 20)
            print(f"  {r.name:12} pop={int(r.population):>6} | "
                  f"tech={r.technology_level:5.1f} | {bar}")
        print()
        # 주요 외교 관계 출력
        notable = [
            (k, v)
            for k, v in self.diplomacy.get_all().items()
            if abs(v) >= 30
        ]
        if notable:
            print("  [외교 현황]")
            for (a, b), val in sorted(notable, key=lambda x: x[1]):
                level = AffinityLevel.from_value(val).display()
                print(f"    {a:12} → {b:12}: {val:+6.1f} ({level})")
