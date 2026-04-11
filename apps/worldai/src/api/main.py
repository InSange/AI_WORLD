"""
WorldAI FastAPI Application
=============================
WorldAI 시뮬레이션 엔진의 REST API 서버.

실행 방법:
  cd apps/worldai
  uvicorn src.api.main:app --reload --port 8000

Swagger UI: http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
"""
from __future__ import annotations

import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.api.websocket_manager import manager

# 앱 루트를 sys.path에 추가
_APP_ROOT = Path(__file__).parent.parent.parent  # apps/worldai/
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))

from src.core.world import World
from src.core.faction_manager import FactionManager
from src.core.models import AffiliationType


# ── 기본 파벌 초기화 ──────────────────────────────────

def _setup_default_factions(world: World, fm: FactionManager) -> None:
    """선호 지형 기반 파벌 동적 배치"""
    occupied_spots = []
    
    def spawn(f_id, name, race_id, pop, affil=AffiliationType.INDEPENDENT, parent=None, rel=None, specs=None):
        race = world.races.get(race_id)
        prefs = race.preferred_biomes if race else ["plains"]
        loc = world.map.find_suitable_location(prefs, occupied_spots, min_dist=15.0)
        occupied_spots.append(loc)
        # 구 지역(region)명은 하드코딩 대신 찾은 타일의 생물군계를 한글로 변환
        tile = world.map.get_tile(loc[0], loc[1])
        region = tile.tile_type.display() if tile else "미개척지"
        
        fm.create_faction(
            f_id, name, race_id, region,
            population=pop, affiliation=affil, parent_id=parent, religion_id=rel,
            location=loc, specialty=specs or []
        )

    # ── 제국 및 산하
    spawn("central_empire", "아스테리아 중앙 제국", "human", 32000, rel="angel_faith")
    spawn("river_kingdom", "강변 왕국 리베르", "human", 12000, AffiliationType.VASSAL, parent="central_empire", rel="angel_faith", specs=["trade", "navy"])
    
    # 북부 요새들
    spawn("northern_fortress_1", "제1북벽 철성 요새", "human", 150, AffiliationType.COLONY, parent="central_empire", specs=["border_defense"])
    spawn("northern_fortress_2", "왕국 전초기지", "human", 80, AffiliationType.COLONY, parent="river_kingdom")
    spawn("northern_fortress_3", "관측소", "human", 50, AffiliationType.COLONY, parent="central_empire")

    # ── 드래곤 교단 (산맥)
    spawn("dragon_cult_alpha", "첫번째 발톱 마을", "human", 450, rel="dragon_cult", specs=["dragon_kin"])
    spawn("dragon_cult_beta", "솟은 봉우리 신도회", "human", 300, rel="dragon_cult")

    # ── 이종족 독립 파벌들
    spawn("ancient_forest_realm", "고대 숲의 성역", "elf", 1200, rel="nature_faith", specs=["magic_research", "forest_defense"])
    spawn("ironpeak_kingdom", "철봉 지하왕국", "dwarf", 6000, rel="ancestor_faith", specs=["mining", "crafting"])
    spawn("southern_undead_domain", "언데드 사멸의 영지", "undead", 2000, rel="demon_cult", specs=["death_harvest"])
    spawn("orc_war_camp", "불타는 도끼 부족", "orc", 4500, rel="demon_cult", specs=["raiding", "war_camp"])

    # ── 초월자
    spawn("peak_dragon_grimm", "고대룡 그리말", "dragon", 1, specs=["apex_predator"])

    print(f"✅ 동적 지형 탐색 기반 파벌 {len(fm.all_factions())}개 생성 완료")


# ── App Lifespan (시작/종료) ────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──
    print("🌍 WorldAI 서버 시작 중...")
    world = World.from_config("asteria")
    faction_manager = FactionManager()
    _setup_default_factions(world, faction_manager)

    app.state.world = world
    app.state.fm = faction_manager
    app.state.auto_running = False

    # ── [Dirty Region] 영토 캐시 초기화 ─────────────────
    # 첫 틱부터 get_territory_delta()가 동작하려면
    # 전체 계산(get_territory_data) 결과를 캐시에 세팅해야 한다.
    all_factions = faction_manager.all_factions()
    faction_manager._territory_cache = world.map.get_territory_data(all_factions)  # type: ignore[attr-defined]
    print(f"🗺️  영토 캐시 초기화 완료 ({len(faction_manager._territory_cache)} 타일)")

    print("✅ 시뮬레이션 초기화 완료\n")

    yield

    # ── Shutdown ──
    app.state.auto_running = False
    print("🔴 WorldAI 서버 종료")


# ── FastAPI 앱 ────────────────────────────────────────

app = FastAPI(
    title="WorldAI Simulation API",
    description="""
## WorldAI — 판타지 세계관 시뮬레이션 엔진

시간이 지나면서 13개 종족이 자율적으로 행동하고 성장·전쟁·동맹을 맺는 세계 시뮬레이션.

### 주요 기능
- **시뮬레이션 제어**: 틱 단위로 세계를 진행
- **세계 상태 조회**: 종족 인구, 기술력, 외교 관계 실시간 조회
- **파벌 시스템**: 제국~마을까지 계층적 파벌과 종교 교단
- **초월자 이벤트**: 드래곤 처치 → 용인 진화 등 특수 이벤트
    """,
    version="0.3.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS (대시보드/Unity 연동 대비)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 라우터 등록 ──────────────────────────────────────

from src.api.routes import simulation, world, factions  # noqa: E402

app.include_router(simulation.router, prefix="/simulation", tags=["Simulation"])
app.include_router(world.router,      prefix="/world",      tags=["World"])
app.include_router(factions.router,   prefix="/factions",   tags=["Factions"])


# ── WebSocket ────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    실시간 상태 브로드캐스트를 위한 WebSocket 엔드포인트.
    접속 시 현재 세계 상태 요약을 전송한다.
    """
    await manager.connect(websocket)
    
    # ── 초기 데이터 전송 (Snapshot)
    try:
        from src.api.routes.world import get_world
        # Request 객체가 없으므로 직접 호출하거나 스키마로 변환
        # 여기서는 단순화하여 틱 정보만 우선 전송
        world = websocket.app.state.world
        await websocket.send_json({
            "type": "INIT",
            "tick": world.tick,
            "year": world.year,
            "season": world.season.display(),
            "message": "Connected to WorldAI Simulation"
        })

        # ── 수신 대기 루프 (연결 유지)
        while True:
            # 클라이언트로부터의 메시지는 현재 무시하지만 연결 유지를 위해 필요
            data = await websocket.receive_text()
            print(f"📩 WS Received: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"⚠️ WS Error: {e}")
        manager.disconnect(websocket)


# ── 루트 엔드포인트 ──────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    """WorldAI API 상태 확인"""
    return {
        "service": "WorldAI Simulation API",
        "version": "0.3.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "simulation": "/simulation/status",
            "world":      "/world",
            "factions":   "/factions",
        },
    }


@app.get("/health", tags=["Root"])
async def health():
    """헬스 체크"""
    return {"status": "ok"}
