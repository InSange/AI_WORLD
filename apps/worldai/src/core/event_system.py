"""
WorldAI Event System
=====================
세계에서 자율적으로 발생하는 사건들을 처리한다.

처리하는 이벤트:
  1. 인구 과밀 → 영역 확장 or 기근/역병
  2. 종족 간 습격 (aggression 기반)
  3. 몬스터 토벌 (공동 이벤트 → 협력 기회)
  4. 전투 결과 → 인구 감소 + 외교 하락
"""
from __future__ import annotations

import random
from typing import Callable
from .models import RaceState, EventLog

# 몬스터 유형 테이블
_MONSTER_TYPES = [
    ("드래곤 군락의 습격", 0.08,  "mythic"),
    ("오거 무리의 난동",   0.06,  "common"),
    ("트롤 떼의 마을 공격", 0.04, "common"),
    ("언데드 물결",        0.07,  "undead"),
    ("마왕의 선봉대",      0.12,  "mythic"),
    ("고블린 대습격",      0.05,  "common"),
    ("격화된 정령 폭주",   0.05,  "elemental"),
]

# 역병 면역 종족
_PLAGUE_IMMUNE = {"undead", "golem"}


class EventSystem:
    """
    월드 틱마다 호출되는 세계 이벤트 발생기.
    외부 의존: RaceState dict + diplomacy.adjust callable
    """

    def __init__(self) -> None:
        self._raid_cooldown: dict[str, int] = {}       # race_id → 마지막 습격 틱
        self._investigation_log: dict[str, str] = {}   # victim_id → attacker_id

    def tick(
        self,
        races: dict[str, RaceState],
        diplomacy_adjust: Callable,   # (from_id, to_id, delta, reason, tick) → EventLog|None
        tick: int,
    ) -> list[EventLog]:
        events: list[EventLog] = []

        # 1. 인구 과밀 처리
        #    1틱=1시간이므로 일 단위(24틱)마다 체크에 필요
        if tick % 24 == 0:  # 하루 1회
            for race in list(races.values()):
                if not race.is_alive:
                    continue
                evts = self._population_overflow(race, tick)
                events.extend(evts)

        # 2. 습격 이벤트 (72틱 = 3일마다)
        if tick % 72 == 0:
            evts = self._check_raids(races, diplomacy_adjust, tick)
            events.extend(evts)

        # 3. 몬스터 토벌 이벤트 (240틱 = 10일마다, 20% 확률)
        if tick % 240 == 0 and random.random() < 0.20:
            evts = self._monster_raid(races, diplomacy_adjust, tick)
            events.extend(evts)

        # 4. 역병 (720틱 = 30일마다, 10% 확률)
        if tick % 720 == 0 and random.random() < 0.10:
            evts = self._plague(races, tick)
            events.extend(evts)

        return events

    # ── 1. 인구 과밀 ────────────────────────────────────

    def _population_overflow(self, race: RaceState, tick: int) -> list[EventLog]:
        """인구 과밀 처리. 하루 1회(24틱마다) 호출 최적화."""
        cap_ratio = race.population / race.max_population
        events: list[EventLog] = []

        if cap_ratio < 0.85:
            return events   # 여유 있음

        # 85~94%: 영역 확장 시도 (5% 확률 / 하루 1회 체크 기준)
        if cap_ratio < 0.95:
            if random.random() < 0.05:
                if race.territory_count < 20:
                    old_max = race.max_population
                    race.territory_count += 1
                    race.max_population = int(race.max_population * 1.10)
                    events.append(EventLog(
                        tick=tick,
                        event_type="TERRITORY_EXPAND",
                        title=f"[확장] {race.name}: 영역 확장 (영역 {race.territory_count})",
                        description=(
                            f"인구 증가로 새 영역 개척. "
                            f"최대 인구 {old_max:,} → {race.max_population:,}으로 확장."
                        ),
                        affected_races=[race.id],
                    ))
                else:
                    # 영역 최대: 과잉 인구 → 타 종족 습격 성향 상승 (simmering tension)
                    race.aggression = min(1.0, race.aggression + 0.02)

        # 95%+: 기근 (10% 확률 / 하루 1회 체크 기준)
        elif random.random() < 0.10:
            lost = race.population * random.uniform(0.08, 0.20)
            race.population = max(1.0, race.population - lost)
            race.morale = max(0.4, race.morale - 0.15)
            events.append(EventLog(
                tick=tick,
                event_type="FAMINE",
                title=f"[재앙] 대기근: {race.name}",
                description=(
                    f"인구 과잉으로 식량 부족. {int(lost):,}명 사망. 사기 하락. "
                    f"남은 인구: {int(race.population):,}명"
                ),
                affected_races=[race.id],
            ))

        return events

    # ── 2. 습격 이벤트 ──────────────────────────────────

    def _check_raids(
        self,
        races: dict[str, RaceState],
        diplomacy_adjust: Callable,
        tick: int,
    ) -> list[EventLog]:
        events: list[EventLog] = []

        for aggressor in races.values():
            if not aggressor.is_alive:
                continue
            if aggressor.aggression < 0.55:
                continue
            # 쿨다운 확인 (같은 종족이 연속 습격 방지: 30틱 간격)
            last = self._raid_cooldown.get(aggressor.id, 0)
            if tick - last < 30:
                continue
            # 발생 확률: aggression에 비례
            if random.random() > aggressor.aggression * 0.15:
                continue

            # 가장 적대적인 대상 파악 (직접 호스트일 타겟 리스트 생성)
            # candidates 가져오는 더 안전한 방법: 클로저 기반
            # (diplomacy_adjust signature: (a, b, delta, reason, tick) → EventLog|None)
            # 여기서는 races에서 직접 필터링

            hostile_targets = [
                r for r in races.values()
                if r.id != aggressor.id and r.is_alive
                and aggressor.aggression > 0.5
            ]
            if not hostile_targets:
                continue

            target = random.choice(hostile_targets)
            evt = self._resolve_combat(aggressor, target, diplomacy_adjust, tick, reason="raid")
            if evt:
                events.append(evt)
                self._raid_cooldown[aggressor.id] = tick

        return events

    def _resolve_combat(
        self,
        attacker: RaceState,
        target: RaceState,
        diplomacy_adjust: Callable,
        tick: int,
        reason: str = "raid",
    ) -> EventLog | None:
        """전투 결과 계산 → 인구 감소 + 외교 하락"""
        if target.population < 50:
            return None

        # 전투력 = 군사력 × 인구 규모 보정 × 사기
        attacker_power = attacker.military_strength * (attacker.population / 500) ** 0.5 * attacker.morale
        defender_power = target.military_strength * (target.population / 500) ** 0.5 * target.morale * 1.15

        if attacker_power > defender_power:
            # 공격 성공
            loss_pct = random.uniform(0.04, 0.12)
            lost = target.population * loss_pct
            target.population = max(1.0, target.population - lost)
            target.morale = max(0.3, target.morale - 0.10)
            attacker.morale = min(1.0, attacker.morale + 0.05)  # 승리 사기 상승

            # 피해 종족 → 공격 종족 친밀도 급락 (원인 파악)
            diplomacy_adjust(target.id, attacker.id, -20.0, f"{reason}_retaliation", tick)
            diplomacy_adjust(attacker.id, target.id, -5.0,  f"{reason}_act",          tick)

            # 조사 기록
            self._investigation_log[target.id] = attacker.id

            return EventLog(
                tick=tick,
                event_type="RAID_SUCCESS",
                title=f"⚔️ 습격 성공: {attacker.name} → {target.name}",
                description=(
                    f"{attacker.name}이(가) {target.name}을(를) 공격. "
                    f"{int(lost):,}명 피해. {target.name}의 사기 하락. "
                    f"{target.name}은 범인을 파악하고 원한을 품었다."
                ),
                affected_races=[attacker.id, target.id],
                affinity_changes={f"{target.id}→{attacker.id}": -20.0},
            )
        else:
            # 공격 실패
            loss_pct = random.uniform(0.02, 0.07)
            lost = attacker.population * loss_pct
            attacker.population = max(1.0, attacker.population - lost)
            attacker.morale = max(0.3, attacker.morale - 0.10)
            target.morale = min(1.0, target.morale + 0.05)

            return EventLog(
                tick=tick,
                event_type="RAID_REPELLED",
                title=f"🛡️ 습격 격퇴: {target.name}이 {attacker.name} 격퇴",
                description=(
                    f"{target.name}이(가) {attacker.name}의 공격을 막아냈다. "
                    f"공격자 {int(lost):,}명 손실."
                ),
                affected_races=[attacker.id, target.id],
            )

    # ── 3. 몬스터 토벌 ──────────────────────────────────

    def _monster_raid(
        self,
        races: dict[str, RaceState],
        diplomacy_adjust: Callable,
        tick: int,
    ) -> list[EventLog]:
        events: list[EventLog] = []
        alive = [r for r in races.values() if r.is_alive]
        if not alive:
            return events

        monster_name, loss_pct, mtype = random.choice(_MONSTER_TYPES)

        # 피해 대상 선택 (1~3 종족)
        immune = {"undead", "dragon"} if mtype == "undead" else {"dragon"} if mtype == "mythic" else set()
        targets = [r for r in alive if r.id not in immune]
        affected_count = random.randint(1, min(3, len(targets)))
        if not targets:
            return events

        affected = random.sample(targets, affected_count)
        affected_ids = [r.id for r in affected]
        total_loss = 0.0

        for race in affected:
            loss = race.population * loss_pct * random.uniform(0.5, 1.5)
            race.population = max(1.0, race.population - loss)
            total_loss += loss

        events.append(EventLog(
            tick=tick,
            event_type="MONSTER_RAID",
            title=f"👹 몬스터 출현: {monster_name}",
            description=(
                f"{monster_name}이(가) 대륙을 휩쓸었다. "
                f"피해 종족: {', '.join(affected_ids)}. 총 피해: {int(total_loss):,}명."
            ),
            affected_races=affected_ids,
        ))

        # 공동 피해 → 친밀도 상승 (공동의 적 효과)
        if len(affected_ids) >= 2:
            for i in range(len(affected_ids)):
                for j in range(i + 1, len(affected_ids)):
                    a, b = affected_ids[i], affected_ids[j]
                    evt_a = diplomacy_adjust(a, b, +8.0, "monster_common_enemy", tick)
                    evt_b = diplomacy_adjust(b, a, +8.0, "monster_common_enemy", tick)
                    if evt_a:
                        events.append(evt_a)
                    if evt_b:
                        events.append(evt_b)

        return events

    # ── 4. 역병 ─────────────────────────────────────────

    def _plague(
        self,
        races: dict[str, RaceState],
        tick: int,
    ) -> list[EventLog]:
        events: list[EventLog] = []
        target_race = random.choice([
            r for r in races.values()
            if r.is_alive and r.id not in _PLAGUE_IMMUNE
        ] or [])

        if not target_race:
            return events

        loss = target_race.population * random.uniform(0.10, 0.25)
        target_race.population = max(1.0, target_race.population - loss)
        target_race.morale = max(0.3, target_race.morale - 0.20)

        events.append(EventLog(
            tick=tick,
            event_type="PLAGUE",
            title=f"☠️ 역병: {target_race.name}",
            description=(
                f"{target_race.name} 영토에 역병이 돌았다. "
                f"{int(loss):,}명 사망. 사기 급락."
            ),
            affected_races=[target_race.id],
        ))
        return events
