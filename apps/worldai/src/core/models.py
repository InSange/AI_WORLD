"""
WorldAI Core Models
====================
시뮬레이션 전체에서 공유하는 데이터 타입 정의.
모든 시스템은 이 모듈의 타입을 사용한다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ─────────────────────────────────
# Enums
# ─────────────────────────────────

class Season(str, Enum):
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"

    def display(self) -> str:
        names = {"spring": "봄", "summer": "여름", "autumn": "가을", "winter": "겨울"}
        return names[self.value]


class AffinityLevel(str, Enum):
    """친밀도 단계 (-100 ~ +100)"""
    WAR     = "WAR"      # -100 ~ -61
    HOSTILE = "HOSTILE"  # -60  ~ -31
    COLD    = "COLD"     # -30  ~ -11
    NEUTRAL = "NEUTRAL"  #  -10 ~  +19
    FRIEND  = "FRIEND"   #  +20 ~  +49
    ALLIED  = "ALLIED"   #  +50 ~  +79
    BOND    = "BOND"     #  +80 ~ +100

    def display(self) -> str:
        labels = {
            "WAR": "전쟁", "HOSTILE": "적대", "COLD": "냉전",
            "NEUTRAL": "중립", "FRIEND": "우호", "ALLIED": "동맹", "BOND": "혈맹",
        }
        return labels[self.value]

    @staticmethod
    def from_value(v: float) -> "AffinityLevel":
        if v <= -61: return AffinityLevel.WAR
        if v <= -31: return AffinityLevel.HOSTILE
        if v <= -11: return AffinityLevel.COLD
        if v <=  19: return AffinityLevel.NEUTRAL
        if v <=  49: return AffinityLevel.FRIEND
        if v <=  79: return AffinityLevel.ALLIED
        return AffinityLevel.BOND


class ActionType(str, Enum):
    IDLE      = "IDLE"       # 대기
    EXPAND    = "EXPAND"     # 영토 확장
    TRADE     = "TRADE"      # 교역
    ATTACK    = "ATTACK"     # 공격
    NEGOTIATE = "NEGOTIATE"  # 외교 협상
    RESEARCH  = "RESEARCH"   # 기술 연구
    ALLY      = "ALLY"       # 동맹 제안


# ─────────────────────────────────
# Race State (실시간 시뮬레이션 상태)
# ─────────────────────────────────

@dataclass
class RaceState:
    """시뮬레이션 중 종족의 실시간 상태 (YAML 설정에서 초기화 후 매 틱 변화)"""

    # 식별
    id: str
    name: str
    category: str
    tier: int

    # 동적 상태 (매 틱 변화)
    population: float
    military_strength: float
    magic_affinity: float
    technology_level: float
    morale: float = 1.0          # 0.0 ~ 1.0 (사기)

    # 상한 / 성장 한계 (YAML에서 로드)
    max_population: int = 10000
    growth_rate: float = 1.005

    # 행동 성향 (YAML behavior에서 로드)
    aggression: float = 0.5
    expansion_drive: float = 0.5
    alliance_tendency: float = 0.5
    trade_focus: float = 0.5
    isolationism: float = 0.2

    # 특수 능력 ID 목록 (코드에서 참조용)
    trait_ids: list[str] = field(default_factory=list)

    # 자원
    food: float = 1000.0
    iron: float = 200.0
    magic_stone: float = 50.0

    # 영역
    territory_count: int = 1

    # 상태 플래그
    is_alive: bool = True

    def __str__(self) -> str:
        return f"{self.name}(pop={int(self.population)}, tier={self.tier})"


# ─────────────────────────────────
# Affinity Record
# ─────────────────────────────────

@dataclass
class AffinityRecord:
    """두 종족 간 단방향 친밀도 레코드 (A→B / B→A 독립)"""
    from_id: str
    to_id: str
    value: float = 0.0  # -100.0 ~ +100.0

    @property
    def level(self) -> AffinityLevel:
        return AffinityLevel.from_value(self.value)

    def __str__(self) -> str:
        return f"{self.from_id}→{self.to_id}: {self.value:+.1f} ({self.level.display()})"


# ─────────────────────────────────
# Events
# ─────────────────────────────────

@dataclass
class EventLog:
    """발생된 이벤트 기록"""
    tick: int
    event_type: str
    title: str
    description: str
    affected_races: list[str]
    affinity_changes: dict[str, float] = field(default_factory=dict)
    # 예: {"human→elf": +5.0, "elf→human": +2.0}

    def to_dict(self) -> dict[str, Any]:
        return {
            "tick": self.tick,
            "type": self.event_type,
            "title": self.title,
            "description": self.description,
            "affected": self.affected_races,
            "affinity_changes": self.affinity_changes,
        }


# ─────────────────────────────────
# Actions
# ─────────────────────────────────

@dataclass
class Action:
    """종족이 한 틱에 결정한 행동"""
    race_id: str
    action_type: ActionType
    target_race_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# ─────────────────────────────────
# Tick Result
# ─────────────────────────────────

@dataclass
class TickResult:
    """tick_world() 호출 결과 요약"""
    tick: int
    season: Season
    year: int
    events: list[EventLog]
    population_changes: dict[str, float]   # race_id → 변화량
    affinity_changes: list[dict[str, Any]] # 이번 틱 외교 수치 변화 목록

    def summary(self) -> str:
        lines = [f"[Tick {self.tick}] Year {self.year} / {self.season.display()}"]
        for rid, delta in self.population_changes.items():
            if abs(delta) > 0.5:
                lines.append(f"  {rid}: 인구 {delta:+.1f}")
        for e in self.events:
            lines.append(f"  🔔 {e.title}")
        return "\n".join(lines)
