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
    """기본 세계 시작 파벌 생성"""
    # ── 인간 파벌
    fm.create_faction(
        "central_empire", "아스테리아 중앙 제국", "human", "central_plains",
        population=25000, affiliation=AffiliationType.INDEPENDENT,
        religion_id="angel_faith", location=(50, 40),
    )
    fm.create_faction(
        "north_wall_guard", "북벽 수비대", "human", "northern_tundra",
        population=120, affiliation=AffiliationType.COLONY,
        parent_id="central_empire", location=(40, 5),
        specialty=["border_defense", "cold_resistance"],
    )
    fm.create_faction(
        "river_kingdom", "강변 왕국 리베르", "human", "river_coast",
        population=8500, affiliation=AffiliationType.VASSAL,
        parent_id="central_empire", religion_id="angel_faith", location=(35, 55),
        specialty=["trade", "navy"],
    )
    fm.create_faction(
        "plains_village_a", "황금 밀밭 마을", "human", "central_plains",
        population=230, affiliation=AffiliationType.INDEPENDENT,
        location=(48, 35), specialty=["agriculture"],
    )

    # ── 엘프 파벌
    fm.create_faction(
        "ancient_forest_realm", "고대 숲의 성역", "elf", "western_forest",
        population=800, affiliation=AffiliationType.INDEPENDENT,
        religion_id="nature_faith", location=(10, 30),
        specialty=["magic_research", "forest_defense"],
    )

    # ── 드워프 파벌
    fm.create_faction(
        "ironpeak_kingdom", "철봉 지하왕국", "dwarf", "eastern_mountain",
        population=4500, affiliation=AffiliationType.INDEPENDENT,
        religion_id="ancestor_faith", location=(90, 30),
        specialty=["mining", "crafting"],
    )
    fm.create_faction(
        "goblin_mine_outpost", "고블린 광산 전초기지 (드워프 대항)", "dwarf", "eastern_mountain",
        population=45, affiliation=AffiliationType.COLONY,
        parent_id="ironpeak_kingdom", location=(85, 20), specialty=["mining"],
    )

    # ── 오크 파벌
    fm.create_faction(
        "plains_horde", "대평원 오크 무리", "orc", "central_plains",
        population=1500, affiliation=AffiliationType.INDEPENDENT,
        location=(70, 45), specialty=["raiding"],
    )

    # ── 수인
    fm.create_faction(
        "iron_claw_tribe", "철발톱 부족 (견족)", "beastman", "northern_tundra",
        population=280, affiliation=AffiliationType.INDEPENDENT,
        religion_id="nature_faith", location=(30, 8), specialty=["hunting"],
    )

    # ── 드래곤
    fm.create_faction(
        "peak_dragon_grimm", "설봉의 노룡 그리말", "dragon", "northern_tundra",
        population=1, affiliation=AffiliationType.INDEPENDENT,
        location=(50, 3), specialty=["apex_predator"],
    )

    # ── 언데드
    fm.create_faction(
        "southern_undead_domain", "남부 언데드 영지", "undead", "southern_wasteland",
        population=300, affiliation=AffiliationType.INDEPENDENT,
        religion_id="demon_cult", location=(60, 72), specialty=["death_harvest"],
    )

    print(f"✅ 기본 파벌 {len(fm.all_factions())}개 생성 완료")


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

시간이 지나면서 15개 종족이 자율적으로 행동하고 성장·전쟁·동맹을 맺는 세계 시뮬레이션.

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
