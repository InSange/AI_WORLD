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
from src.api.websocket_manager import manager

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
        season=world.season.display(),
        season_display=world.season.display(),
        hour=world.hour_of_day,
        day_phase=world.day_phase.value,
        is_daytime=world.is_daytime,
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

    # ── [Snapshot-after-Commit] ────────────────────────────────────────
    # 틱 처리 전 과정(월드 → 파벌 → 영토)을 완전히 완료한 뒤에만 브로드캐스트.
    # WebSocket 구독자는 항상 완결된 상태 스냅샷만 수신하며,
    # 처리 중간 상태(외교 수치 변경 후 영토 미반영 등)가 노출되지 않는다.
    # ──────────────────────────────────────────────────────────────────

    # 1. 월드 틱 (시간·인구·외교·행동·이벤트)
    result = world.tick_world()

    # 2. 파벌 매니저 틱 — 인구 성장·이동·종교 전파
    race_growths = {r.id: r.growth_rate for r in world.races.values()}
    from src.core.world import SEASON_POP_MODIFIER
    season_mod = SEASON_POP_MODIFIER[world.season]

    # 인구 변화 발생 파벌 추적 (Dirty Region 계산용)
    pop_before = {f.id: f.population for f in fm.all_factions()}
    faction_events = fm.tick(
        get_race_growth=lambda rid: race_growths.get(rid, 1.005),
        season_pop_mod=season_mod,
        tick=world.tick,
        world_map=world.map,
    )
    result.events.extend(faction_events)

    # 3. [Dirty Region] 인구 변화가 있는 파벌만 영토 재계산
    changed_ids = {
        fid for fid, prev_pop in pop_before.items()
        if abs(fm.get(fid).population - prev_pop) > 1.0
    } if hasattr(fm, "_territory_cache") else set()

    territory_delta: list[dict] = []
    if changed_ids and hasattr(world.map, "get_territory_delta"):
        prev_cache = getattr(fm, "_territory_cache", None)
        if prev_cache is not None:
            updated, territory_delta = world.map.get_territory_delta(
                factions=fm.all_factions(),
                changed_faction_ids=changed_ids,
                prev_territories=prev_cache,
            )
            fm._territory_cache = updated  # type: ignore[attr-defined]

    # ── 전 처리 완료 후 단일 스냅샷 브로드캐스트 (Snapshot-after-Commit)
    await manager.broadcast({
        "type": "UPDATE",
        "tick": result.tick,
        "year": result.year,
        "season": result.season.display(),
        "hour": world.hour_of_day,
        "day_phase": world.day_phase.value,
        "is_daytime": world.is_daytime,
        "events": [e.to_dict() for e in result.events],
        # 변경된 타일만 포함 — 클라이언트는 이 delta로 로컬 캐시 패치
        "territory_delta": territory_delta,
    })

    return TickResultSchema(
        tick=result.tick,
        year=result.year,
        season=result.season.value,
        season_display=result.season.display(),
        hour=world.hour_of_day,
        day_phase=world.day_phase.value,
        is_daytime=world.is_daytime,
        population_changes={k: round(v, 2) for k, v in result.population_changes.items()},
        events=[
            EventSchema(
                tick=e.tick,
                event_type=e.event_type,
                title=e.title,
                description=e.description,
                affected_races=e.affected_races,
                affected_factions=e.affected_factions,
                affinity_changes=e.affinity_changes,
                faction_affinity_changes=e.faction_affinity_changes,
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

    # 최근 요약 데이터 전송
    await manager.broadcast({
        "type": "SUMMARY",
        "ran_ticks": ticks,
        "current_tick": world.tick,
        "current_year": world.year,
        "current_season": world.season.display(),
        "current_hour": world.hour_of_day,
        "current_phase": world.day_phase.display(),
        "populations": pop_snapshots,
    })

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

    world = World.from_config("asteria")
    fm = FactionManager()

    # main.py의 setup 함수 재사용
    from src.api.main import _setup_default_factions
    _setup_default_factions(world, fm)

    # 영토 캐시 재초기화 (Dirty Region 정합성 유지)
    fm._territory_cache = world.map.get_territory_data(fm.all_factions())  # type: ignore[attr-defined]

    req.app.state.world = world
    req.app.state.fm = fm

    return MessageResponse(message="시뮬레이션이 초기화됐습니다.", detail={"tick": 0})
