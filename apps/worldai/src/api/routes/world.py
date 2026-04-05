"""
세계 상태 조회 라우터
- GET /world              : 전체 세계 상태 스냅샷
- GET /world/races        : 모든 종족 상태
- GET /world/races/{id}   : 특정 종족 상세
- GET /world/diplomacy    : 외교 관계 전체
- GET /world/events       : 최근 이벤트 목록
"""
from __future__ import annotations

from fastapi import APIRouter, Request, HTTPException, Query
from src.api.schemas import (
    WorldStateSchema, RaceStatusSchema,
    DiplomacyRelationSchema, EventSchema,
)
from src.core.models import AffinityLevel

router = APIRouter()


def _world(req: Request):
    return req.app.state.world


# ── GET /world ────────────────────────────────────────

@router.get("", response_model=WorldStateSchema, summary="전체 세계 상태")
async def get_world(req: Request):
    """현재 세계의 종족 상태, 외교 관계, 최근 이벤트를 모두 반환한다."""
    world = _world(req)

    races = {
        r.id: RaceStatusSchema(
            id=r.id, name=r.name, tier=r.tier, category=r.category,
            population=int(r.population),
            military_strength=round(r.military_strength, 1),
            technology_level=round(r.technology_level, 1),
            magic_affinity=round(r.magic_affinity, 1),
            morale=round(r.morale, 2),
            territory_count=r.territory_count,
            trait_ids=r.trait_ids,
        )
        for r in world.active_races
    }

    diplomacy = {
        f"{a}→{b}": DiplomacyRelationSchema(
            from_id=a, to_id=b,
            value=round(v, 1),
            level=AffinityLevel.from_value(v).value,
            display=AffinityLevel.from_value(v).display(),
        )
        for (a, b), v in world.diplomacy.get_all().items()
        if abs(v) > 0.5  # 의미 있는 관계만 반환
    }

    events = [
        EventSchema(
            tick=e.tick, event_type=e.event_type,
            title=e.title, description=e.description,
            affected_races=e.affected_races,
            affinity_changes=e.affinity_changes,
        )
        for e in world.event_log[-30:]
    ]

    return WorldStateSchema(
        tick=world.tick, year=world.year,
        season=world.season.value,
        season_display=world.season.display(),
        races=races, diplomacy=diplomacy, recent_events=events,
    )


# ── GET /world/races ──────────────────────────────────

@router.get("/races", response_model=list[RaceStatusSchema], summary="모든 종족 목록")
async def get_races(
    req: Request,
    sort_by: str = Query(default="population", enum=["population", "military_strength", "technology_level"]),
):
    """활성 종족 목록을 지정 기준으로 정렬해 반환한다."""
    world = _world(req)
    races = sorted(
        world.active_races,
        key=lambda r: getattr(r, sort_by),
        reverse=True,
    )
    return [
        RaceStatusSchema(
            id=r.id, name=r.name, tier=r.tier, category=r.category,
            population=int(r.population),
            military_strength=round(r.military_strength, 1),
            technology_level=round(r.technology_level, 1),
            magic_affinity=round(r.magic_affinity, 1),
            morale=round(r.morale, 2),
            territory_count=r.territory_count,
            trait_ids=r.trait_ids,
        )
        for r in races
    ]


# ── GET /world/races/{race_id} ────────────────────────

@router.get("/races/{race_id}", response_model=RaceStatusSchema, summary="특정 종족 상세")
async def get_race(req: Request, race_id: str):
    """지정한 종족의 현재 상태를 반환한다."""
    world = _world(req)
    race = world.races.get(race_id)
    if race is None or not race.is_alive:
        raise HTTPException(404, f"종족 '{race_id}'를 찾을 수 없습니다.")
    return RaceStatusSchema(
        id=race.id, name=race.name, tier=race.tier, category=race.category,
        population=int(race.population),
        military_strength=round(race.military_strength, 1),
        technology_level=round(race.technology_level, 1),
        magic_affinity=round(race.magic_affinity, 1),
        morale=round(race.morale, 2),
        territory_count=race.territory_count,
        trait_ids=race.trait_ids,
    )


# ── GET /world/diplomacy ──────────────────────────────

@router.get("/diplomacy", summary="전체 외교 관계")
async def get_diplomacy(
    req: Request,
    min_abs: float = Query(default=10.0, description="최소 절댓값 필터 (낮으면 더 많은 관계 표시)"),
    level: str | None = Query(default=None, enum=["WAR", "HOSTILE", "COLD", "NEUTRAL", "FRIEND", "ALLIED", "BOND"]),
):
    """
    종족 간 외교 친밀도 전체를 반환한다.
    - min_abs: 이 절댓값 이상인 관계만 반환
    - level: 특정 단계만 필터링
    """
    world = _world(req)
    result = []
    for (a, b), v in sorted(world.diplomacy.get_all().items(), key=lambda x: x[1]):
        if abs(v) < min_abs:
            continue
        lv = AffinityLevel.from_value(v)
        if level and lv.value != level:
            continue
        result.append({
            "from": a, "to": b,
            "value": round(v, 1),
            "level": lv.value,
            "display": lv.display(),
        })
    return {"total": len(result), "relations": result}


# ── GET /world/events ─────────────────────────────────

@router.get("/events", summary="이벤트 로그")
async def get_events(
    req: Request,
    limit: int = Query(default=20, ge=1, le=200),
    event_type: str | None = Query(default=None, description="이벤트 타입 필터"),
):
    """
    발생한 이벤트 로그를 반환한다.
    최신 순으로 정렬된다.
    """
    world = _world(req)
    events = list(reversed(world.event_log))
    if event_type:
        events = [e for e in events if e.event_type == event_type]
    events = events[:limit]
    return {
        "total_logged": len(world.event_log),
        "returned": len(events),
        "events": [e.to_dict() for e in events],
    }


# ── GET /world/leaderboard ────────────────────────────

@router.get("/leaderboard", summary="종족 순위표")
async def get_leaderboard(req: Request):
    """
    인구·기술·군사력 기준 종족 순위를 반환한다.
    """
    world = _world(req)
    races = world.active_races

    def rank(lst, key, label):
        sorted_lst = sorted(lst, key=lambda r: getattr(r, key), reverse=True)
        return [{"rank": i+1, "id": r.id, "name": r.name, label: round(getattr(r, key), 1)}
                for i, r in enumerate(sorted_lst)]

    return {
        "by_population":         rank(races, "population", "population"),
        "by_military_strength":  rank(races, "military_strength", "military_strength"),
        "by_technology_level":   rank(races, "technology_level", "technology_level"),
        "by_magic_affinity":     rank(races, "magic_affinity", "magic_affinity"),
    }
