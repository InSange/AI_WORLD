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
        """
        rec = self._get_or_create(from_id, to_id)
        old_val = rec.value
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

    def _check_threshold(
        self,
        from_id: str,
        to_id: str,
        old: float,
        new: float,
        tick: int,
    ) -> EventLog | None:
        """임계값 통과 여부 확인 → EventLog 반환"""
        for threshold, up_event, down_event in _THRESHOLDS:
            crossed_up   = old <= threshold < new  # 상승해서 통과
            crossed_down = old > threshold >= new  # 하락해서 통과

            if crossed_up or crossed_down:
                event_type = up_event if crossed_up else down_event
                desc = _THRESHOLD_DESCRIPTIONS.get(event_type, event_type)
                return EventLog(
                    tick=tick,
                    event_type=event_type,
                    title=f"[외교] {from_id} → {to_id}: {event_type}",
                    description=desc,
                    affected_races=[from_id, to_id],
                    affinity_changes={f"{from_id}→{to_id}": round(new - old, 2)},
                )
        return None

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
