"""
WorldAI API Response Schemas
==============================
FastAPI 엔드포인트의 요청/응답 Pydantic 모델.
타입 안전하고 자동 문서화(OpenAPI)가 지원된다.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any


# ── 종족 상태 ─────────────────────────────────

class RaceStatusSchema(BaseModel):
    id: str
    name: str
    tier: int
    category: str
    population: int
    military_strength: float
    technology_level: float
    magic_affinity: float
    morale: float
    territory_count: int
    trait_ids: list[str]


# ── 외교 관계 ─────────────────────────────────

class DiplomacyRelationSchema(BaseModel):
    from_id: str
    to_id: str
    value: float
    level: str           # WAR / HOSTILE / COLD / NEUTRAL / FRIEND / ALLIED / BOND
    display: str         # 전쟁 / 적대 / 냉전 / 중립 / 우호 / 동맹 / 혈맹


# ── 이벤트 ────────────────────────────────────

class EventSchema(BaseModel):
    tick: int
    event_type: str
    title: str
    description: str
    affected_races: list[str]
    affinity_changes: dict[str, float] = Field(default_factory=dict)


# ── 시뮬레이션 상태 ───────────────────────────

class SimulationStatusSchema(BaseModel):
    tick: int
    year: int
    season: str
    season_display: str
    total_population: int
    active_races: int
    total_events: int


# ── 세계 전체 상태 ────────────────────────────

class WorldStateSchema(BaseModel):
    tick: int
    year: int
    season: str
    season_display: str
    races: dict[str, RaceStatusSchema]
    diplomacy: dict[str, DiplomacyRelationSchema]
    recent_events: list[EventSchema]


# ── 틱 결과 ───────────────────────────────────

class TickResultSchema(BaseModel):
    tick: int
    year: int
    season: str
    season_display: str
    population_changes: dict[str, float]
    events: list[EventSchema]


# ── 파벌 ──────────────────────────────────────

class LeaderSchema(BaseModel):
    id: str
    name: str
    race: str
    title: str
    title_type: str
    grade: str
    level: int
    is_transcendent: bool
    transcendent_type: str | None = None
    loyalty: float
    ambition: float


class FactionSchema(BaseModel):
    id: str
    name: str
    race: str
    region: str
    scale: str
    scale_display: str
    population: int
    military_strength: float
    affiliation_type: str
    parent_faction_id: str | None
    child_count: int
    leader: LeaderSchema | None
    dominant_religion: str | None
    religion_influence: dict[str, float]
    specialty: list[str]
    location: dict[str, int]


# ── 종족별 파벌 목록 ──────────────────────────

class FactionListSchema(BaseModel):
    total: int
    factions: list[FactionSchema]


# ── 종교 ──────────────────────────────────────

class ReligionSchema(BaseModel):
    id: str
    name: str
    deity_type: str
    deity_id: str
    description: str
    spread_rate: float
    conflict_threshold: float
    faction_effects: dict[str, float]


# ── 초월자 이벤트 요청 ────────────────────────

class TranscendentTriggerRequest(BaseModel):
    faction_id: str
    transcendent_type: str   # dragonborn / divine_chosen / demon_contract 등
    source: str              # "북방 드래곤 처치" 등 설명


# ── 일반 응답 ─────────────────────────────────

class MessageResponse(BaseModel):
    message: str
    detail: Any | None = None
