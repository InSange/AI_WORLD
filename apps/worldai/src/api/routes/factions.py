"""
파벌 관련 라우터
- GET  /factions                   : 전체 파벌 목록
- GET  /factions/{id}              : 특정 파벌 상세
- GET  /factions/by-region/{region}: 지역별 파벌
- GET  /factions/by-race/{race}    : 종족별 파벌
- GET  /factions/religions         : 등록된 교단 목록
- POST /factions/{id}/transcendent : 파벌 지도자 초월자 이벤트 발생
"""
from __future__ import annotations

from fastapi import APIRouter, Request, HTTPException, Query
from src.api.schemas import (
    FactionSchema, FactionListSchema, LeaderSchema,
    ReligionSchema, TranscendentTriggerRequest, MessageResponse,
    PopulationSegmentSchema,
)
from src.core.models import TranscendentType

router = APIRouter()


def _fm(req: Request):
    return req.app.state.fm


def _faction_to_schema(faction) -> FactionSchema:
    leader_schema = None
    if faction.leader:
        ldr = faction.leader
        leader_schema = LeaderSchema(
            id=ldr.id, name=ldr.name, race=ldr.race,
            title=ldr.title, title_type=ldr.title_type.value,
            grade=ldr.grade, level=ldr.level,
            is_transcendent=ldr.is_transcendent,
            transcendent_type=(
                ldr.transcendent.transcendent_type.value if ldr.transcendent else None
            ),
            loyalty=round(ldr.loyalty, 2),
            ambition=round(ldr.ambition, 2),
        )
    return FactionSchema(
        id=faction.id,
        name=faction.name,
        race=faction.race,
        region=faction.region,
        scale=faction.scale.value,
        scale_display=faction.scale.display(),
        population=int(faction.population),
        population_segments=[
            PopulationSegmentSchema(
                pop_type=s.pop_type.value,
                pop_display=s.pop_type.display(),
                count=int(s.count),
                can_travel=s.can_travel,
            )
            for s in faction.population_segments
        ],
        military_strength=round(faction.military_strength, 1),
        affiliation_type=faction.affiliation_type.value,
        parent_faction_id=faction.parent_faction_id,
        child_count=len(faction.child_faction_ids),
        leader=leader_schema,
        dominant_religion=faction.dominant_religion,
        religion_influence={k: round(v, 1) for k, v in faction.religion_influence.items()},
        specialty=faction.specialty,
        location={"x": faction.location_x, "y": faction.location_y},
    )


# ── GET /factions ─────────────────────────────────────

@router.get("", response_model=FactionListSchema, summary="전체 파벌 목록")
async def list_factions(
    req: Request,
    scale: str | None = Query(default=None, enum=["outpost", "village", "town", "city", "kingdom", "empire"]),
    top_level_only: bool = Query(default=False, description="최상위(독립) 파벌만 조회"),
):
    """등록된 모든 파벌을 반환한다. 규모별 필터링 가능."""
    fm = _fm(req)
    factions = fm.top_level_factions() if top_level_only else fm.all_factions()

    if scale:
        factions = [f for f in factions if f.scale.value == scale]

    return FactionListSchema(
        total=len(factions),
        factions=[_faction_to_schema(f) for f in factions],
    )


# ── GET /factions/religions ───────────────────────────

@router.get("/religions", response_model=list[ReligionSchema], summary="등록된 교단 목록")
async def list_religions(req: Request):
    """시뮬레이션에 등록된 모든 교단 정보를 반환한다."""
    fm = _fm(req)
    return [
        ReligionSchema(
            id=r.id, name=r.name,
            deity_type=r.deity_type.value, deity_id=r.deity_id,
            description=r.description,
            spread_rate=r.spread_rate,
            conflict_threshold=r.conflict_threshold,
            faction_effects=r.faction_effects,
        )
        for r in fm._religions.values()
    ]


# ── GET /factions/by-region/{region} ─────────────────

@router.get("/by-region/{region}", response_model=FactionListSchema, summary="지역별 파벌")
async def factions_by_region(req: Request, region: str):
    """특정 지역에 위치한 파벌들을 반환한다."""
    fm = _fm(req)
    factions = fm.by_region(region)
    return FactionListSchema(
        total=len(factions),
        factions=[_faction_to_schema(f) for f in sorted(factions, key=lambda f: -f.population)],
    )


# ── GET /factions/by-race/{race_id} ──────────────────

@router.get("/by-race/{race_id}", response_model=FactionListSchema, summary="종족별 파벌")
async def factions_by_race(req: Request, race_id: str):
    """특정 종족에 속한 파벌들을 반환한다."""
    fm = _fm(req)
    factions = fm.by_race(race_id)
    return FactionListSchema(
        total=len(factions),
        factions=[_faction_to_schema(f) for f in sorted(factions, key=lambda f: -f.population)],
    )


# ── GET /factions/{faction_id} ────────────────────────

@router.get("/{faction_id}", response_model=FactionSchema, summary="파벌 상세 조회")
async def get_faction(req: Request, faction_id: str):
    """지정한 파벌의 상세 정보를 반환한다."""
    fm = _fm(req)
    faction = fm.get(faction_id)
    if faction is None:
        raise HTTPException(404, f"파벌 '{faction_id}'를 찾을 수 없습니다.")
    return _faction_to_schema(faction)


# ── POST /factions/{faction_id}/transcendent ──────────

@router.post("/{faction_id}/transcendent", response_model=MessageResponse, summary="초월자 이벤트 발생")
async def trigger_transcendent(
    req: Request,
    faction_id: str,
    body: TranscendentTriggerRequest,
):
    """
    지정한 파벌의 지도자에게 초월자 이벤트를 발생시킨다.

    초월 유형:
    - `dragonborn` — 드래곤 처치 후 용인 진화
    - `divine_chosen` — 신의 사자 선택
    - `demon_contract` — 마계와의 계약
    - `vampire_lord` — 고위 뱀파이어 전환
    - `elemental_one` — 대정령과 합일
    - `relic_bearer` — 세계 신물 획득
    """
    fm = _fm(req)
    faction = fm.get(faction_id)
    if faction is None:
        raise HTTPException(404, f"파벌 '{faction_id}'를 찾을 수 없습니다.")
    if faction.leader is None:
        raise HTTPException(400, f"파벌 '{faction_id}'에 지도자가 없습니다.")
    if faction.leader.is_transcendent:
        raise HTTPException(409, f"이미 초월자입니다: {faction.leader.name}")

    try:
        t_type = TranscendentType(body.transcendent_type)
    except ValueError:
        raise HTTPException(400, f"올바르지 않은 초월 유형: {body.transcendent_type}")

    world = req.app.state.world
    evt = fm.trigger_transcendent_event(
        character=faction.leader,
        transcendent_type=t_type,
        source=body.source,
        tick=world.tick,
    )
    world.event_log.append(evt)

    return MessageResponse(
        message=f"초월자 탄생: {faction.leader.name}",
        detail={
            "leader": str(faction.leader),
            "event": evt.title,
            "level_cap": faction.leader.effective_level_cap,
            "extra_traits": faction.leader.transcendent.extra_trait_ids,
        },
    )
