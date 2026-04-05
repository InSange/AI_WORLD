"""
WorldAI Faction Manager
========================
파벌(Faction)의 생성·관리·틱 처리를 담당한다.

주요 기능:
 - 파벌 등록 및 부모-자식 관계 관리
 - 인구 성장에 따른 규모(scale) 자동 갱신
 - 독립 파벌 자동 생성 (정착 조건 충족 시)
 - 종교 교세 전파 및 갈등 처리
 - 파벌 간 외교 (종족 단위와 별개)
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable

from .models import (
    Faction, Character, Religion, EventLog,
    AffiliationType, SettlementScale, DeityType,
    TitleType, TranscendentInfo, TranscendentType,
)

# ── 기본 종교 데이터 ───────────────────────────────────

DEFAULT_RELIGIONS: dict[str, Religion] = {
    "angel_faith": Religion(
        id="angel_faith", name="천계의 빛 교단",
        deity_type=DeityType.ANGEL, deity_id="angel_demon",
        description="빛과 질서를 추구하는 신앙. 어둠을 정화하려 한다.",
        base_affinity={"demon_cult": -90, "undead_cult": -70, "dragon_cult": -40, "nature_faith": -20},
        faction_effects={"morale": 0.10, "combat_vs_undead": 0.15, "combat_vs_demon": 0.15},
        spread_rate=0.05,
    ),
    "demon_cult": Religion(
        id="demon_cult", name="심연의 교단",
        deity_type=DeityType.DEMON, deity_id="angel_demon",
        description="금지된 힘을 추구하는 비밀 신앙.",
        base_affinity={"angel_faith": -90, "nature_faith": -50, "undead_cult": +30},
        faction_effects={"military_strength": 0.10, "morale": -0.05},
        spread_rate=0.04,
    ),
    "dragon_cult": Religion(
        id="dragon_cult", name="용의 심장 교단",
        deity_type=DeityType.DRAGON, deity_id="dragon",
        description="드래곤의 힘과 지혜를 숭배한다.",
        base_affinity={"angel_faith": -40, "demon_cult": 0, "nature_faith": +10},
        faction_effects={"technology_level": 0.05, "dragon_affinity": 20.0},
        spread_rate=0.03,
    ),
    "nature_faith": Religion(
        id="nature_faith", name="대정령 신앙",
        deity_type=DeityType.NATURE, deity_id="elemental",
        description="자연과 대정령을 숭배. 엘프·수인 선호.",
        base_affinity={"demon_cult": -50, "undead_cult": -80, "angel_faith": -20},
        faction_effects={"food": 0.15, "magic_affinity": 0.10},
        spread_rate=0.06,
    ),
    "ancestor_faith": Religion(
        id="ancestor_faith", name="조상의 길",
        deity_type=DeityType.ANCESTOR, deity_id="",
        description="선조와의 연결. 가문·부족 중시.",
        base_affinity={},  # 타 종교 간섭 없음
        faction_effects={"military_strength": 0.10, "morale": 0.05},
        spread_rate=0.02,
    ),
}

# ── 종족별 기본 지도자 칭호 및 레벨 상한 ──────────────

_RACE_LEADER_TITLE: dict[str, dict[str, str]] = {
    "human":   {"outpost": "대장", "village": "촌장", "town": "영주", "city": "영주", "kingdom": "왕", "empire": "황제"},
    "elf":     {"outpost": "수호자", "village": "장로", "town": "장로", "city": "장로 평의회", "kingdom": "숲의 왕", "empire": "숲의 왕"},
    "dwarf":   {"outpost": "감독관", "village": "터전주", "town": "영지주", "city": "영지주", "kingdom": "왕(드왈린)", "empire": "왕"},
    "orc":     {"outpost": "부족장", "village": "부족장", "town": "추장", "city": "전쟁추장", "kingdom": "오크로드", "empire": "오크로드"},
    "halfling":{"outpost": "경비대장", "village": "촌장", "town": "영주", "city": "영주", "kingdom": "왕", "empire": "왕"},
    "beastman":{"outpost": "전사장", "village": "부족장", "town": "대부족장", "city": "대부족장", "kingdom": "대부족장", "empire": "대부족장"},
    "dragon":  {"outpost": "단독", "village": "군락장", "town": "군락장", "city": "군락장", "kingdom": "용왕", "empire": "용왕"},
    "undead":  {"outpost": "뱀파이어", "village": "뱀파이어 영주", "town": "리치", "city": "리치", "kingdom": "죽음의 군주", "empire": "죽음의 황제"},
}

_RACE_LEVEL_CAP: dict[str, int] = {
    "human": 99, "elf": 350, "dwarf": 200, "orc": 60,
    "halfling": 150, "beastman": 80, "dragon": 999,
    "undead": 500, "angel_demon": 999, "elemental": 400, "golem": 150,
}


class FactionManager:
    """
    모든 파벌의 등록, 관리, 틱 처리를 담당하는 매니저.
    """

    def __init__(self) -> None:
        self._factions: dict[str, Faction] = {}
        self._religions: dict[str, Religion] = dict(DEFAULT_RELIGIONS)

    # ── 조회 ─────────────────────────────────────

    def get(self, faction_id: str) -> Faction | None:
        return self._factions.get(faction_id)

    def all_factions(self) -> list[Faction]:
        return [f for f in self._factions.values() if f.is_alive]

    def by_race(self, race_id: str) -> list[Faction]:
        return [f for f in self.all_factions() if f.race == race_id]

    def by_region(self, region: str) -> list[Faction]:
        return [f for f in self.all_factions() if f.region == region]

    def top_level_factions(self) -> list[Faction]:
        """부모 파벌이 없는 독립/최상위 파벌"""
        return [f for f in self.all_factions() if f.parent_faction_id is None]

    def get_religion(self, religion_id: str) -> Religion | None:
        return self._religions.get(religion_id)

    # ── 등록 ─────────────────────────────────────

    def add_faction(self, faction: Faction) -> None:
        """파벌 등록"""
        self._factions[faction.id] = faction
        faction.update_scale()
        if faction.leader is None:
            faction.leader = self._generate_leader(faction)

    def add_religion(self, religion: Religion) -> None:
        self._religions[religion.id] = religion

    # ── 파벌 생성 헬퍼 ───────────────────────────

    def create_faction(
        self,
        faction_id: str,
        name: str,
        race: str,
        region: str,
        population: float,
        affiliation: AffiliationType = AffiliationType.INDEPENDENT,
        parent_id: str | None = None,
        specialty: list[str] | None = None,
        location: tuple[int, int] = (50, 40),
        religion_id: str | None = None,
    ) -> Faction:
        """파벌 생성 + 자동 초기화"""
        faction = Faction(
            id=faction_id,
            name=name,
            race=race,
            region=region,
            population=population,
            affiliation_type=affiliation,
            parent_faction_id=parent_id,
            location_x=location[0],
            location_y=location[1],
            specialty=specialty or [],
        )
        faction.update_scale()

        # 종교 초기 교세 적용
        if religion_id and religion_id in self._religions:
            faction.religion_influence[religion_id] = random.uniform(30.0, 70.0)

        # 부모-자식 연결
        if parent_id and parent_id in self._factions:
            parent = self._factions[parent_id]
            if faction_id not in parent.child_faction_ids:
                parent.child_faction_ids.append(faction_id)

        self.add_faction(faction)
        return faction

    # ── 초월자 이벤트 ─────────────────────────────

    def trigger_transcendent_event(
        self,
        character: Character,
        transcendent_type: TranscendentType,
        source: str,
        tick: int,
    ) -> EventLog:
        """
        초월자 탄생 이벤트 처리.
        캐릭터에 TranscendentInfo를 부여하고 월드 이벤트를 반환.
        """
        level_cap_bonus = {
            TranscendentType.DRAGONBORN:     151,
            TranscendentType.DIVINE_CHOSEN:  200,
            TranscendentType.VAMPIRE_LORD:   200,
            TranscendentType.ELEMENTAL_ONE:  150,
            TranscendentType.DEMON_CONTRACT: 150,
            TranscendentType.RELIC_BEARER:   100,
        }.get(transcendent_type, 100)

        extra_traits = {
            TranscendentType.DRAGONBORN:     ["dragon_breath_weak", "dragon_tongue", "scaled_skin"],
            TranscendentType.DIVINE_CHOSEN:  ["divine_aura", "holy_smite"],
            TranscendentType.DEMON_CONTRACT: ["shadow_step", "mana_surge"],
        }.get(transcendent_type, [])

        character.transcendent = TranscendentInfo(
            transcendent_type=transcendent_type,
            stage=1,
            source=source,
            level_cap_bonus=level_cap_bonus,
            extra_trait_ids=extra_traits,
        )

        type_names = {
            TranscendentType.DRAGONBORN: "용인(龍人)",
            TranscendentType.DIVINE_CHOSEN: "신의 사자",
            TranscendentType.DEMON_CONTRACT: "마계 계약자",
            TranscendentType.VAMPIRE_LORD: "고위 뱀파이어",
            TranscendentType.RELIC_BEARER: "신물 보유자",
        }
        type_display = type_names.get(transcendent_type, str(transcendent_type))

        return EventLog(
            tick=tick,
            event_type="TRANSCENDENT_BORN",
            title=f"⚡ 초월자 탄생: {character.name} — {type_display}",
            description=f"{character.name}이(가) {source}을(를) 통해 초월했다. "
                        f"레벨 상한이 {character.base_level_cap} → {character.effective_level_cap}으로 확장됐다.",
            affected_races=[character.race],
            affinity_changes={},
        )

    # ── 틱 처리 ──────────────────────────────────

    def tick(
        self,
        get_race_growth: Callable[[str], float],  # race_id → growth_rate
        season_pop_mod: float,
        tick: int,
    ) -> list[EventLog]:
        """매 틱 파벌 상태 갱신"""
        events: list[EventLog] = []

        for faction in list(self.all_factions()):
            # 1. 인구 성장
            growth = get_race_growth(faction.race)
            effective = 1.0 + (growth - 1.0) * season_pop_mod
            faction.population = min(
                float(faction.scale.value == "empire" and 999999 or
                      {"outpost": 50, "village": 500, "town": 2000, "city": 5000,
                       "kingdom": 15000, "empire": 999999}.get(faction.scale.value, 9999)),
                faction.population * effective,
            )
            old_scale = faction.scale
            faction.update_scale()

            # 규모 상승 이벤트
            if faction.scale != old_scale:
                events.append(EventLog(
                    tick=tick,
                    event_type="FACTION_SCALE_UP",
                    title=f"[성장] {faction.name}: {old_scale.display()} → {faction.scale.display()}",
                    description=f"{faction.name}의 규모가 커졌다. 새 지도자 칭호: "
                                f"{self._get_leader_title(faction.race, faction.scale.value)}",
                    affected_races=[faction.race],
                ))
                # 지도자 칭호 갱신
                if faction.leader:
                    faction.leader.title = self._get_leader_title(faction.race, faction.scale.value)

            # 2. 종교 교세 전파 (30틱마다)
            if tick % 30 == 0:
                evt = self._spread_religion(faction, tick)
                if evt:
                    events.append(evt)

            # 3. 자원 상납 (종속 파벌)
            if faction.affiliation_type in (AffiliationType.COLONY, AffiliationType.VASSAL):
                self._pay_tribute(faction)

        # 4. 독립 파벌 자동 생성 체크 (100틱마다)
        if tick % 100 == 0:
            events.extend(self._check_auto_spawn(tick))

        return events

    # ── 내부 유틸 ─────────────────────────────────

    def _generate_leader(self, faction: Faction) -> Character:
        """파벌에 맞는 기본 지도자 자동 생성"""
        title = self._get_leader_title(faction.race, faction.scale.value)
        level_cap = _RACE_LEVEL_CAP.get(faction.race, 99)
        level = max(5, int(level_cap * random.uniform(0.10, 0.35)))

        return Character(
            id=f"{faction.id}_leader",
            name=f"{faction.name}의 {title}",
            race=faction.race,
            faction_id=faction.id,
            title=title,
            title_type=TitleType.HEREDITARY if faction.race in ("human", "elf", "dwarf") else TitleType.MERIT,
            grade="이름 있는 전사" if level > 40 else "병사",
            level=level,
            base_level_cap=level_cap,
            loyalty=random.uniform(0.5, 0.9),
            ambition=random.uniform(0.1, 0.7),
            wisdom=random.uniform(0.3, 0.8),
            courage=random.uniform(0.4, 0.9),
        )

    def _get_leader_title(self, race: str, scale: str) -> str:
        race_titles = _RACE_LEADER_TITLE.get(race, {})
        return race_titles.get(scale, "지도자")

    def _spread_religion(self, faction: Faction, tick: int) -> EventLog | None:
        """교세 전파 및 갈등 체크"""
        if not faction.religion_influence:
            return None

        dom_religion_id = faction.dominant_religion
        if not dom_religion_id:
            return None

        religion = self._religions.get(dom_religion_id)
        if not religion:
            return None

        # 교세 강화
        current = faction.religion_influence.get(dom_religion_id, 0.0)
        faction.religion_influence[dom_religion_id] = min(100.0, current + religion.spread_rate * 100)

        # 갈등: 타 교단이 threshold 이상 교세면 충돌 이벤트
        for r_id, influence in faction.religion_influence.items():
            if r_id == dom_religion_id:
                continue
            if influence >= religion.conflict_threshold:
                base_aff = religion.base_affinity.get(r_id, 0.0)
                if base_aff <= -50:
                    return EventLog(
                        tick=tick,
                        event_type="RELIGIOUS_CONFLICT",
                        title=f"⚔️ 종교 갈등: {faction.name} ({dom_religion_id} vs {r_id})",
                        description=f"{faction.name} 내부에서 종교 갈등이 폭발했다. "
                                    f"{dom_religion_id}와 {r_id}의 신자들이 충돌.",
                        affected_races=[faction.race],
                    )
        return None

    def _pay_tribute(self, faction: Faction) -> None:
        """상납 처리 (간략화: 인구 성장 페널티로 표현)"""
        rate = 0.25 if faction.affiliation_type == AffiliationType.COLONY else 0.15
        # 실제 구현에서는 parent의 자원에 더하고 자신은 차감
        # 지금은 성장률 페널티로만 표현
        faction.population = max(1.0, faction.population * (1 - rate * 0.001))

    def _check_auto_spawn(self, tick: int) -> list[EventLog]:
        """이주/탐험으로 새 마을 자동 생성 시뮬레이션 (낮은 확률)"""
        events: list[EventLog] = []
        for faction in self.all_factions():
            # 큰 파벌(kingdom 이상)에서 이주민 파생 가능
            if faction.scale in (SettlementScale.KINGDOM, SettlementScale.EMPIRE):
                if random.random() < 0.02:  # 2% 확률
                    new_id = f"{faction.id}_settlement_{tick}"
                    pop = random.uniform(60, 150)
                    new_faction = self.create_faction(
                        faction_id=new_id,
                        name=f"{faction.name} 개척지",
                        race=faction.race,
                        region=faction.region,
                        population=pop,
                        affiliation=AffiliationType.COLONY,
                        parent_id=faction.id,
                        location=(
                            faction.location_x + random.randint(-10, 10),
                            faction.location_y + random.randint(-10, 10),
                        ),
                    )
                    events.append(EventLog(
                        tick=tick,
                        event_type="FACTION_SPAWN",
                        title=f"🏘️ 신규 정착지: {new_faction.name}",
                        description=f"{faction.name}에서 이주민 {int(pop)}명이 갈라져 새 정착지를 세웠다.",
                        affected_races=[faction.race],
                    ))
        return events

    # ── 디버그 출력 ───────────────────────────────

    def print_summary(self) -> None:
        """모든 파벌 현황 출력"""
        print(f"\n{'='*60}")
        print(f" 파벌 현황 ({len(self.all_factions())}개)")
        print(f"{'='*60}")
        for scale in SettlementScale:
            factions = [f for f in self.all_factions() if f.scale == scale]
            if not factions:
                continue
            print(f"\n  [{scale.display()}]")
            for f in factions:
                parent = f" ← {f.parent_faction_id}" if f.parent_faction_id else ""
                leader = f.leader.name if f.leader else "?"
                religion = f.dominant_religion or "무신"
                print(f"    {f.name:20} pop={int(f.population):>6} | "
                      f"지도자: {leader:15} | 종교: {religion}{parent}")
