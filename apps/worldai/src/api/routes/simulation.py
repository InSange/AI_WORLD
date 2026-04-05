"""
시뮬레이션 제어 라우터
- POST /simulation/tick       : 1틱 진행
- POST /simulation/run        : N틱 자동 실행
- GET  /simulation/status     : 현재 상태 요약
- POST /simulation/reset      : 시뮬레이션 초기화
"""
from __future__ import annotations

from fastapi import APIRouter, Request, HTTPException, Query
from src.api.schemas import SimulationStatusSchema, TickResultSchema, EventSchema, MessageResponse
from src.core.models import AffinityLevel

router = APIRouter()


def _world(req: Request):
    return req.app.state.world


def _fm(req: Request):
    return req.app.state.fm


# ── GET /simulation/status ────────────────────────────

@router.get("/status", response_model=SimulationStatusSchema, summary="현재 시뮬레이션 상태")
async def get_status(req: Request):
    """틱, 연도, 계절, 총 인구, 종족 수를 반환한다."""
    world = _world(req)
    active = world.active_races
    return SimulationStatusSchema(
        tick=world.tick,
        year=world.year,
        season=world.season.value,
        season_display=world.season.display(),
        total_population=sum(int(r.population) for r in active),
        active_races=len(active),
        total_events=len(world.event_log),
    )


# ── POST /simulation/tick ─────────────────────────────

@router.post("/tick", response_model=TickResultSchema, summary="1틱 진행")
async def tick_once(req: Request):
    """
    시뮬레이션을 1틱 진행한다.
    종족 인구 변화, 외교 조정, 행동 실행 결과를 반환한다.
    """
    world = _world(req)
    fm = _fm(req)

    # 월드 틱
    result = world.tick_world()

    # 파벌 매니저 틱
    race_growths = {r.id: r.growth_rate for r in world.races.values()}
    from src.core.world import SEASON_POP_MODIFIER
    season_mod = SEASON_POP_MODIFIER[world.season]
    faction_events = fm.tick(
        get_race_growth=lambda rid: race_growths.get(rid, 1.005),
        season_pop_mod=season_mod,
        tick=world.tick,
        world_map=world.map,
    )
    result.events.extend(faction_events)

    return TickResultSchema(
        tick=result.tick,
        year=result.year,
        season=result.season.value,
        season_display=result.season.display(),
        population_changes={k: round(v, 2) for k, v in result.population_changes.items()},
        events=[
            EventSchema(
                tick=e.tick,
                event_type=e.event_type,
                title=e.title,
                description=e.description,
                affected_races=e.affected_races,
                affinity_changes=e.affinity_changes,
            )
            for e in result.events
        ],
    )


# ── POST /simulation/run ──────────────────────────────

@router.post("/run", summary="N틱 자동 실행")
async def run_ticks(
    req: Request,
    ticks: int = Query(default=10, ge=1, le=1000, description="실행할 틱 수 (1 ~ 1000)"),
):
    """
    지정된 틱 수만큼 시뮬레이션을 연속 실행한다.
    완료 후 요약 결과를 반환한다 (최대 1000틱).
    """
    if ticks > 1000:
        raise HTTPException(400, "한 번에 최대 1000틱까지 실행 가능합니다.")

    world = _world(req)
    fm = _fm(req)
    race_growths = {r.id: r.growth_rate for r in world.races.values()}

    collected_events: list[dict] = []
    pop_snapshots: dict[str, int] = {}

    from src.core.world import SEASON_POP_MODIFIER
    for _ in range(ticks):
        result = world.tick_world()
        season_mod = SEASON_POP_MODIFIER[world.season]
        faction_events = fm.tick(
            get_race_growth=lambda rid: race_growths.get(rid, 1.005),
            season_pop_mod=season_mod,
            tick=world.tick,
            world_map=world.map,
        )
        all_events = result.events + faction_events
        for e in all_events:
            if e.event_type not in ("SEASON_CHANGE",):  # 계절 변화는 요약에서 제외
                collected_events.append(e.to_dict())

    for race in world.active_races:
        pop_snapshots[race.id] = int(race.population)

    return {
        "ran_ticks": ticks,
        "current_tick": world.tick,
        "current_year": world.year,
        "current_season": world.season.display(),
        "populations": pop_snapshots,
        "notable_events": collected_events[-50:],  # 최근 50개
        "total_notable_events": len(collected_events),
    }


# ── POST /simulation/reset ────────────────────────────

@router.post("/reset", response_model=MessageResponse, summary="시뮬레이션 리셋")
async def reset_simulation(req: Request):
    """
    시뮬레이션을 초기 상태로 리셋한다.
    World와 FactionManager를 새로 생성한다.
    """
    from src.core.world import World
    from src.core.faction_manager import FactionManager
    from src.core.models import AffiliationType

    world = World.from_config("asteria")
    fm = FactionManager()

    # main.py의 setup 함수 재사용
    from src.api.main import _setup_default_factions
    _setup_default_factions(world, fm)

    req.app.state.world = world
    req.app.state.fm = fm

    return MessageResponse(message="시뮬레이션이 초기화됐습니다.", detail={"tick": 0})
