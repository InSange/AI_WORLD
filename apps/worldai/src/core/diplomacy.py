"""
WorldAI Diplomacy System
=========================
종족 간 친밀도(-100 ~ +100) 관리.
- 비대칭: A→B와 B→A 독립 관리
- 자연 감쇠: 시간이 지나면 중립(0)으로 수렴
- 임계값 이벤트: 특정 수치 돌파 시 자동 이벤트 발생
"""
from __future__ import annotations

from .models import AffinityLevel, AffinityRecord, EventLog

# (임계값, 상승 시 이벤트, 하락 시 이벤트)
_THRESHOLDS: list[tuple[float, str, str]] = [
    (+80.0, "BLOOD_PACT_FORMED",   "BOND_BROKEN"),
    (+50.0, "ALLIANCE_PROPOSED",   "ALLIANCE_BROKEN"),
    (+20.0, "TRADE_ROUTE_OPEN",    "TRADE_ROUTE_CLOSED"),
    (-10.0, "DIPLOMATIC_TENSION",  "TENSION_EASED"),
    (-30.0, "TRADE_EMBARGO",       "EMBARGO_LIFTED"),
    (-60.0, "WAR_DECLARED",        "WAR_ENDED"),
]

# 관계 단계 경계값 (오름차순). _THRESHOLDS 를 뒤집은 것.
_LEVEL_BOUNDS: list[tuple[float, str, str]] = list(reversed(_THRESHOLDS))

# 경계 근처에서 친밀도가 미세하게 흔들려도 단계가 오가지 않도록 두는 여유폭.
# 이 값이 없으면 자연 감쇠와 상승이 반복되며 같은 이벤트가 계속 발화한다.
_LEVEL_HYSTERESIS = 3.0

_THRESHOLD_DESCRIPTIONS: dict[str, str] = {
    "BLOOD_PACT_FORMED":   "두 종족이 혈맹을 맺었다. 자원 공유, 공동 전쟁 의무 발생.",
    "BOND_BROKEN":         "혈맹이 파기됐다.",
    "ALLIANCE_PROPOSED":   "동맹 조약이 체결됐다. 군사 협력과 교역 우대가 시작된다.",
    "ALLIANCE_BROKEN":     "동맹이 결렬됐다.",
    "TRADE_ROUTE_OPEN":    "교역로가 개설됐다. 자원 교환이 시작된다.",
    "TRADE_ROUTE_CLOSED":  "교역이 중단됐다.",
    "DIPLOMATIC_TENSION":  "외교 마찰이 발생했다. 냉전 상태에 돌입.",
    "TENSION_EASED":       "긴장이 완화됐다.",
    "TRADE_EMBARGO":       "교역 금지령이 내려졌다. 적대 관계 돌입.",
    "EMBARGO_LIFTED":      "교역 금지가 해제됐다.",
    "WAR_DECLARED":        "선전포고! 두 종족 사이에 전쟁이 시작됐다.",
    "WAR_ENDED":           "전쟁이 종결됐다.",
}


class DiplomacySystem:
    """
    종족 간 친밀도(-100 ~ +100)를 관리하는 시스템.
    비대칭 설계: A→B와 B→A는 독립적으로 관리된다.
    """

    def __init__(self) -> None:
        self._relations: dict[tuple[str, str], AffinityRecord] = {}
        # 임계값 이벤트 쿨다운: (from, to, threshold) → 마지막 발화 틱
        self._threshold_cooldown: dict[tuple[str, str, float], int] = {}
        # 관계 단계 기억: (from, to) → 단계 인덱스
        # 단계가 실제로 바뀔 때만 이벤트를 낸다.
        self._relation_level: dict[tuple[str, str], int] = {}

    # ── 조회 ──────────────────────────

    def get(self, from_id: str, to_id: str) -> float:
        """A→B 친밀도 반환. 기록 없으면 0.0"""
        key = (from_id, to_id)
        return self._relations[key].value if key in self._relations else 0.0

    def get_level(self, from_id: str, to_id: str) -> AffinityLevel:
        return AffinityLevel.from_value(self.get(from_id, to_id))

    def get_record(self, from_id: str, to_id: str) -> AffinityRecord:
        return self._get_or_create(from_id, to_id)

    def get_all(self) -> dict[tuple[str, str], float]:
        return {k: r.value for k, r in self._relations.items()}

    # ── 변경 ──────────────────────────

    def set(self, from_id: str, to_id: str, value: float) -> None:
        """친밀도 직접 설정 (클램핑 적용)"""
        rec = self._get_or_create(from_id, to_id)
        rec.value = max(-100.0, min(100.0, value))

    def adjust(
        self,
        from_id: str,
        to_id: str,
        delta: float,
        reason: str,
        tick: int,
    ) -> EventLog | None:
        """
        친밀도 delta 조정.
        임계값 통과 시 EventLog 반환, 아니면 None.

        포화 방지:
          - 이미 BOND(80+) 상태에서 양수 delta는 50% 감쇠
          - 이미 WAR(-60-) 상태에서 음수 delta는 50% 감쇠
        """
        rec = self._get_or_create(from_id, to_id)
        old_val = rec.value

        # 포화 감쇠: 이미 극단에 가까우면 같은 방향 delta 축소
        if old_val >= 80.0 and delta > 0:
            delta *= 0.20   # BOND 이상에서 긍정 효과 80% 감쇠
        elif old_val <= -60.0 and delta < 0:
            delta *= 0.20   # WAR 이상에서 부정 효과 80% 감쇠

        new_val = max(-100.0, min(100.0, old_val + delta))
        rec.value = new_val
        return self._check_threshold(from_id, to_id, old_val, new_val, tick)

    def decay_all(self, decay_rate: float = 0.001) -> None:
        """
        모든 관계를 중립(0)으로 서서히 수렴.
        매 틱 호출. decay_rate = 절댓값의 몇 % 복원할지.
        """
        for rec in self._relations.values():
            if rec.value > 0.0:
                rec.value = max(0.0, rec.value - abs(rec.value) * decay_rate)
            elif rec.value < 0.0:
                rec.value = min(0.0, rec.value + abs(rec.value) * decay_rate)

    # ── 초기화 ────────────────────────

    def load_defaults(self, race_id: str, defaults: list[dict]) -> None:
        """
        YAML diplomacy_defaults 초기값 설정.
        이미 설정된 값이 있으면 덮어쓰지 않는다 (선점 우선).
        """
        for d in defaults:
            target = d.get("target", "")
            if not target:
                continue
            affinity = float(d.get("affinity", 0.0))
            key = (race_id, target)
            if key not in self._relations:
                self._relations[key] = AffinityRecord(race_id, target, affinity)

    # ── 내부 유틸 ─────────────────────

    def _get_or_create(self, from_id: str, to_id: str) -> AffinityRecord:
        key = (from_id, to_id)
        if key not in self._relations:
            self._relations[key] = AffinityRecord(from_id, to_id, 0.0)
        return self._relations[key]

    def _level_of(self, value: float, previous: int | None) -> int:
        """친밀도가 속한 관계 단계를 구한다.

        이미 어떤 단계에 있으면 내려올 때 여유폭만큼 더 떨어져야 하고,
        아래에 있으면 올라갈 때 여유폭만큼 더 올라야 단계가 바뀐다.
        """
        level = 0
        for i, (bound, _, _) in enumerate(_LEVEL_BOUNDS):
            already_above = previous is not None and previous > i
            margin = -_LEVEL_HYSTERESIS if already_above else _LEVEL_HYSTERESIS
            if value > bound + margin:
                level = i + 1
        return level

    def _check_threshold(
        self,
        from_id: str,
        to_id: str,
        old: float,
        new: float,
        tick: int,
        cooldown_ticks: int = 60,
    ) -> EventLog | None:
        """관계 단계가 바뀌었는지 확인 → EventLog 반환.

        예전에는 임계값을 지나칠 때마다 발화해서, 친밀도가 경계에서
        진동하면 같은 쌍이 "혈맹을 맺었다"를 수십 번 반복했다.
        지금은 단계를 기억해 두고 실제로 달라졌을 때만 이벤트를 낸다.
        """
        key = (from_id, to_id)
        previous = self._relation_level.get(key)

        if previous is None:
            # 첫 관측은 기준점만 잡고 이벤트를 내지 않는다.
            self._relation_level[key] = self._level_of(new, None)
            return None

        level = self._level_of(new, previous)
        if level == previous:
            return None

        going_up = level > previous
        # 새로 넘어선(또는 떨어져 나온) 경계
        bound_idx = level - 1 if going_up else previous - 1
        bound, up_event, down_event = _LEVEL_BOUNDS[bound_idx]

        # 쿨다운: 같은 경계가 짧은 간격으로 다시 발화하지 않도록 한다.
        cd_key = (from_id, to_id, bound)
        last_fired = self._threshold_cooldown.get(cd_key, -9999)
        if tick - last_fired < cooldown_ticks:
            self._relation_level[key] = level
            return None

        self._threshold_cooldown[cd_key] = tick
        self._relation_level[key] = level

        event_type = up_event if going_up else down_event
        desc = _THRESHOLD_DESCRIPTIONS.get(event_type, event_type)
        return EventLog(
            tick=tick,
            event_type=event_type,
            title=f"[외교] {from_id} → {to_id}: {event_type}",
            description=desc,
            affected_races=[from_id, to_id],
            affinity_changes={f"{from_id}→{to_id}": round(new - old, 2)},
        )

    # ── 디버그 ────────────────────────

    def debug_summary(self, race_ids: list[str]) -> str:
        """지정 종족들 간 친밀도 표 출력"""
        lines = []
        for a in race_ids:
            for b in race_ids:
                if a == b:
                    continue
                val = self.get(a, b)
                level = AffinityLevel.from_value(val).display()
                if abs(val) > 0.1:
                    lines.append(f"  {a:12} → {b:12}: {val:+6.1f} ({level})")
        return "\n".join(lines) if lines else "  (외교 기록 없음)"
