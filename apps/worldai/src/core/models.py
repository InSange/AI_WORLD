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
# 파벌·종교·초월 관련 Enum
# ─────────────────────────────────

class SettlementScale(str, Enum):
    """파벌 군집 규모"""
    OUTPOST = "outpost"    # 전초기지·요새 (50 이하)
    VILLAGE = "village"   # 마을 (51 ~ 500)
    TOWN    = "town"      # 읍·소도시 (501 ~ 2000)
    CITY    = "city"      # 도시 (2001 ~ 5000)
    KINGDOM = "kingdom"   # 왕국 (5001 ~ 15000)
    EMPIRE  = "empire"    # 제국 (15001+)

    def display(self) -> str:
        labels = {
            "outpost": "요새", "village": "마을", "town": "읍",
            "city": "도시", "kingdom": "왕국", "empire": "제국",
        }
        return labels[self.value]

    @staticmethod
    def from_population(pop: float) -> "SettlementScale":
        if pop <= 50:   return SettlementScale.OUTPOST
        if pop <= 500:  return SettlementScale.VILLAGE
        if pop <= 2000: return SettlementScale.TOWN
        if pop <= 5000: return SettlementScale.CITY
        if pop <= 15000: return SettlementScale.KINGDOM
        return SettlementScale.EMPIRE


class AffiliationType(str, Enum):
    """파벌 소속 유형"""
    INDEPENDENT = "independent"  # 독립 파벌
    COLONY      = "colony"       # 상위 직할 종속
    VASSAL      = "vassal"       # 봉신 (자체 지도자, 세금+군사 의무)
    ALLIED      = "allied"       # 동맹 연합 (소속 아님)


class DeityType(str, Enum):
    """숭배 대상 유형"""
    DRAGON   = "dragon_cult"    # 드래곤 숭배
    ANGEL    = "angel_faith"    # 천사/천신
    DEMON    = "demon_cult"     # 악마 교단
    NATURE   = "nature_faith"   # 대정령/자연
    ANCESTOR = "ancestor_faith" # 조상신
    UNDEAD   = "undead_cult"    # 언데드 군주


class TitleType(str, Enum):
    """직위 획득 방식"""
    HEREDITARY = "hereditary"  # 혈통 계승
    APPOINTED  = "appointed"   # 상위 임명
    ELECTED    = "elected"     # 선출
    CONQUEST   = "conquest"    # 무력 정복
    MERIT      = "merit"       # 능력 인정 (오크 방식)


class TranscendentType(str, Enum):
    """초월 유형"""
    DRAGONBORN     = "dragonborn"      # 용인
    DIVINE_CHOSEN  = "divine_chosen"   # 신의 사자
    VAMPIRE_LORD   = "vampire_lord"    # 고위 뱀파이어
    ELEMENTAL_ONE  = "elemental_one"   # 원소 합일
    DEMON_CONTRACT = "demon_contract"  # 마계 계약자
    RELIC_BEARER   = "relic_bearer"    # 신물 보유자


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


# ─────────────────────────────────
# 초월자 정보
# ─────────────────────────────────

@dataclass
class TranscendentInfo:
    """초월자의 초월 상태 정보"""
    transcendent_type: TranscendentType
    stage: int = 1                         # 1, 2, 3
    source: str = ""                       # "드래곤 그리말 처치" 등
    level_cap_bonus: int = 0               # 레벨 상한 확장량
    extra_trait_ids: list[str] = field(default_factory=list)
    affinity_overrides: dict[str, float] = field(default_factory=dict)  # race/religion_id → delta


# ─────────────────────────────────
# 캐릭터 (지도자·영웅)
# ─────────────────────────────────

@dataclass
class Character:
    """파벌의 지도자 또는 세계에 영향을 주는 개인"""
    id: str
    name: str
    race: str
    faction_id: str

    # 직위
    title: str
    title_type: TitleType = TitleType.HEREDITARY

    # 등급 & 레벨
    grade: str = "병사"                    # 등급 문자열 (종족별 정의)
    level: int = 10
    age_ticks: int = 0
    base_level_cap: int = 99              # 종족 기본 레벨 상한

    # 성격 (0.0 ~ 1.0)
    loyalty: float = 0.7                  # 상위 충성도
    ambition: float = 0.3                 # 야망 (높으면 반란 가능)
    wisdom: float = 0.5                   # 외교 판단 보정
    courage: float = 0.6                  # 전투 참여 의지

    trait_ids: list[str] = field(default_factory=list)

    # 초월자 여부
    transcendent: TranscendentInfo | None = None

    @property
    def is_transcendent(self) -> bool:
        return self.transcendent is not None

    @property
    def effective_level_cap(self) -> int:
        bonus = self.transcendent.level_cap_bonus if self.transcendent else 0
        return self.base_level_cap + bonus

    def __str__(self) -> str:
        t = " [초월자]" if self.is_transcendent else ""
        return f"{self.name} (Lv.{self.level} {self.grade} / {self.title}){t}"


# ─────────────────────────────────
# 종교 (Religion)
# ─────────────────────────────────

@dataclass
class Religion:
    """교단 정보"""
    id: str
    name: str
    deity_type: DeityType
    deity_id: str                          # 연결된 종족/신격 ID
    description: str = ""

    # 타 종교와 기본 친밀도
    base_affinity: dict[str, float] = field(default_factory=dict)  # religion_id → affinity

    # 파벌 효과 (키: 효과명, 값: 배수 or 절댓값)
    faction_effects: dict[str, float] = field(default_factory=dict)

    spread_rate: float = 0.05              # 틱당 교세 전파율
    conflict_threshold: float = 30.0       # 갈등 발생 기준 교세(%)


# ─────────────────────────────────
# 파벌 (Faction)
# ─────────────────────────────────

@dataclass
class Faction:
    """
    하나의 파벌 = 특정 종족의 특정 집단.
    지역·규모·소속·종교를 모두 가진 독립적 행위 주체.
    """
    id: str
    name: str
    race: str                              # 주 종족 ID
    region: str                            # 거주 지역

    # 규모 (인구에 따라 자동 갱신)
    scale: SettlementScale = SettlementScale.VILLAGE
    population: float = 200.0

    # 소속
    affiliation_type: AffiliationType = AffiliationType.INDEPENDENT
    parent_faction_id: str | None = None
    child_faction_ids: list[str] = field(default_factory=list)

    # 위치 (타일 좌표)
    location_x: int = 50
    location_y: int = 40
    territory_tiles: int = 1

    # 지도자
    leader: Character | None = None

    # 전투
    military_strength: float = 30.0
    is_alive: bool = True

    # 종교 구성 (religion_id → 교세 0~100)
    religion_influence: dict[str, float] = field(default_factory=dict)

    # 특성
    specialty: list[str] = field(default_factory=list)

    # 파벌 간 외교 (target_faction_id → affinity)
    faction_affinity: dict[str, float] = field(default_factory=dict)

    def update_scale(self) -> None:
        """인구에 따라 규모 자동 갱신"""
        self.scale = SettlementScale.from_population(self.population)

    @property
    def dominant_religion(self) -> str | None:
        """가장 높은 교세의 종교 ID"""
        if not self.religion_influence:
            return None
        return max(self.religion_influence, key=lambda k: self.religion_influence[k])

    def __str__(self) -> str:
        leader_str = str(self.leader) if self.leader else "지도자 없음"
        return (f"[{self.scale.display()}] {self.name} "
                f"(pop={int(self.population)}, {self.region}) "
                f"| {leader_str}")
