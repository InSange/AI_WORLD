"""
WorldAI Race Agent
===================
종족의 자율 행동 AI.
매 틱 각 종족의 상태와 세계 상황을 분석해 행동을 결정한다.

행동 우선순위:
  1. 위협 대응 (적대 세력이 인접 시 방어/반격)
  2. 영토 확장 (expansion_drive 기반)
  3. 교역 (trade_focus 기반)
  4. 외교 협상 (alliance_tendency 기반)
  5. 기술 연구 (기본 행동)
  6. 대기 (아무것도 할 게 없을 때)
"""
from __future__ import annotations

import random
from typing import Callable
from .models import Action, ActionType, RaceState, AffinityLevel, EventLog

# 행동 발생 기본 확률 (틱당)
_BASE_TRADE_CHANCE    = 0.15
_BASE_EXPAND_CHANCE   = 0.10
_BASE_ATTACK_CHANCE   = 0.08
_BASE_NEGOTIATE_CHANCE = 0.12
_BASE_RESEARCH_CHANCE  = 0.20


class RaceAgent:
    """
    종족 하나의 행동 AI.
    decide_action()을 매 틱 호출해 Action을 받아 세계에 적용한다.
    """

    def __init__(self, race_id: str) -> None:
        self.race_id = race_id

    def decide_action(
        self,
        race: RaceState,
        all_races: dict[str, RaceState],
        get_affinity: Callable,   # (from_id, to_id) → float
    ) -> Action:
        """
        종족의 현재 상태 + 세계 상황 → 이번 틱의 행동 결정.

        Args:
            race: 이 종족의 현재 상태
            all_races: 모든 종족 상태 dict
            get_affinity: (from_id, to_id) → float 친밀도 조회 함수
        """
        if not race.is_alive:
            return Action(race.id, ActionType.IDLE)

        others = {rid: r for rid, r in all_races.items()
                  if rid != race.id and r.is_alive}

        # ── 1. 위협 체크: 적대 세력이 있으면 대응 ──
        threat = self._find_biggest_threat(race, others, get_affinity)
        if threat:
            affinity = get_affinity(race.id, threat.id)
            level = AffinityLevel.from_value(affinity)
            if level == AffinityLevel.WAR:
                # 전쟁 중이면 공격
                if random.random() < race.aggression:
                    return Action(race.id, ActionType.ATTACK,
                                  target_race_id=threat.id,
                                  metadata={"reason": "war_response"})
            elif level == AffinityLevel.HOSTILE:
                # 적대적이면 협상 or 공격
                if random.random() < race.alliance_tendency * 0.5:
                    return Action(race.id, ActionType.NEGOTIATE,
                                  target_race_id=threat.id,
                                  metadata={"reason": "de-escalate"})
                if random.random() < race.aggression * 0.7:
                    return Action(race.id, ActionType.ATTACK,
                                  target_race_id=threat.id,
                                  metadata={"reason": "aggression"})

        # ── 2. 영토 확장 ──
        if random.random() < race.expansion_drive * _BASE_EXPAND_CHANCE:
            return Action(race.id, ActionType.EXPAND,
                          metadata={"reason": "expansion_drive"})

        # ── 3. 교역 ──
        trade_target = self._find_trade_partner(race, others, get_affinity)
        if trade_target and random.random() < race.trade_focus * _BASE_TRADE_CHANCE:
            return Action(race.id, ActionType.TRADE,
                          target_race_id=trade_target.id,
                          metadata={"reason": "trade_opportunity"})

        # ── 4. 외교 협상 ──
        neg_target = self._find_negotiate_target(race, others, get_affinity)
        if neg_target and random.random() < race.alliance_tendency * _BASE_NEGOTIATE_CHANCE:
            if random.random() > race.isolationism:
                return Action(race.id, ActionType.NEGOTIATE,
                              target_race_id=neg_target.id,
                              metadata={"reason": "alliance_building"})

        # ── 5. 기술 연구 ──
        if random.random() < _BASE_RESEARCH_CHANCE:
            return Action(race.id, ActionType.RESEARCH,
                          metadata={"reason": "default_research"})

        # ── 6. 대기 ──
        return Action(race.id, ActionType.IDLE)

    # ── 내부 헬퍼 ────────────────────────

    def _find_biggest_threat(
        self,
        race: RaceState,
        others: dict[str, RaceState],
        get_affinity: Callable,
    ) -> RaceState | None:
        """가장 위협적인 적대 종족 반환 (없으면 None)"""
        threats = []
        for other in others.values():
            aff = get_affinity(race.id, other.id)
            if aff <= -30:  # HOSTILE 이하
                # 위협도 = 상대 전투력 × 적대 정도
                threat_score = other.military_strength * abs(aff) / 100
                threats.append((threat_score, other))
        if not threats:
            return None
        threats.sort(key=lambda x: x[0], reverse=True)
        return threats[0][1]

    def _find_trade_partner(
        self,
        race: RaceState,
        others: dict[str, RaceState],
        get_affinity: Callable,
    ) -> RaceState | None:
        """교역 파트너 후보 반환 (친밀도 +20 이상, 고립성 낮은 상대)"""
        candidates = []
        for other in others.values():
            aff = get_affinity(race.id, other.id)
            if aff >= 20 and other.isolationism < 0.7:
                score = aff + other.trade_focus * 50
                candidates.append((score, other))
        if not candidates:
            return None
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    def _find_negotiate_target(
        self,
        race: RaceState,
        others: dict[str, RaceState],
        get_affinity: Callable,
    ) -> RaceState | None:
        """협상 대상 반환 (친밀도 -30 ~ +50 범위에서 동맹 가능성 있는 상대)"""
        candidates = []
        for other in others.values():
            aff = get_affinity(race.id, other.id)
            # 냉전~우호 범위 (관계 개선 여지가 있음)
            if -30 <= aff <= 50 and other.isolationism < 0.75:
                score = other.alliance_tendency * 100 - abs(aff)
                candidates.append((score, other))
        if not candidates:
            return None
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]


# ── 행동 실행기 (Action → 세계 변화) ─────

def execute_action(
    action: Action,
    races: dict[str, RaceState],
    diplomacy_adjust: Callable,  # (from_id, to_id, delta, reason, tick) → EventLog|None
    tick: int,
) -> EventLog | None:
    """
    결정된 Action을 세계에 적용하고 발생한 이벤트(있으면)를 반환.
    실제 전투 계산은 combat_system에서 따로 처리 (Phase 3.2 이후).
    """
    actor = races.get(action.race_id)
    if actor is None:
        return None

    match action.action_type:

        case ActionType.TRADE:
            target = races.get(action.target_race_id or "")
            if target is None:
                return None
            delta_a = _trade_affinity_delta(actor, target)
            delta_b = _trade_affinity_delta(target, actor) * 0.6  # 상대는 조금 덜
            actor.food += 50
            target.food += 50
            evt_a = diplomacy_adjust(actor.id, target.id, delta_a, "trade_success", tick)
            evt_b = diplomacy_adjust(target.id, actor.id, delta_b, "trade_success", tick)
            return evt_a or evt_b

        case ActionType.NEGOTIATE:
            target = races.get(action.target_race_id or "")
            if target is None:
                return None
            # 협상 성공률: 양측 alliance_tendency의 평균
            success_rate = (actor.alliance_tendency + target.alliance_tendency) / 2
            success_rate *= (1 - target.isolationism)  # 폐쇄적일수록 실패
            import random
            if random.random() < success_rate:
                delta = random.uniform(3, 10)
                evt_a = diplomacy_adjust(actor.id, target.id, +delta, "negotiate_success", tick)
                evt_b = diplomacy_adjust(target.id, actor.id, +delta * 0.5, "negotiate_success", tick)
                return evt_a or evt_b
            return None

        case ActionType.EXPAND:
            # 단순 영토 확장 (충돌 없음)
            actor.territory_count = min(actor.territory_count + 1, 20)
            return None

        case ActionType.RESEARCH:
            # 기술 연구: 인간의 집단 지성 특성 반영
            bonus = _calc_research_bonus(actor)
            actor.technology_level = min(100, actor.technology_level + bonus)
            return None

        case ActionType.ATTACK:
            # 전투는 event_system에서 처리 — 여기선 사기(morale) 긴장 예고만
            target = races.get(action.target_race_id or "")
            if target is None:
                return None
            diplomacy_adjust(actor.id, target.id, -5.0, "attack_declaration", tick)
            return None

        case _:
            return None


def _trade_affinity_delta(actor: RaceState, target: RaceState) -> float:
    """교역 성공 시 친밀도 상승 계산"""
    base = 2.0 + actor.trade_focus * 3.0
    return round(base, 2)


def _calc_research_bonus(race: RaceState) -> float:
    """기술 연구 1틱 진행 효율 계산 (집단 지성 등 특성 반영)"""
    base = 0.05
    # 인간 집단 지성
    if "collective_intelligence" in race.trait_ids:
        if race.population >= 2000:
            base *= 1.30
        elif race.population >= 1000:
            base *= 1.20
        elif race.population >= 500:
            base *= 1.10
        elif race.population <= 100:
            base *= 0.90
    # 엘프 혼자 연구
    if "isolationist" in race.trait_ids and race.territory_count == 1:
        base *= 1.20
    return round(base, 4)
