# WorldAI — 로드맵 (Roadmap)

> 최종 수정: 2026-04-14 | 현재 Phase: Phase 5.5 완료

---

## 마일스톤 개요

| Phase | 이름 | 목표 | 상태 |
|-------|------|------|------|
| Phase 0 | 하네스 골격 | 프로젝트 구조 + 문서 시스템 | ✅ 완료 |
| Phase 1 | 기획 문서 | 세계관·종족·시스템 설계 문서화 | ✅ 완료 |
| Phase 2 | YAML 데이터 | 13종족 설정 파일 + 설정 로더 | ✅ 완료 |
| Phase 3 | 시뮬레이션 코어 | Python 시뮬레이션 엔진 구현 | ✅ 완료 |
| Phase 3.5 | 파벌·종교·초월자 시스템 | Faction/Religion/Transcendent 구현 | ✅ 완료 |
| Phase 4 | API 서버 | FastAPI REST 서버 구현 | ✅ 완료 |
| Phase 4.5 | 밸런스 수정 | 이벤트 시스템 재조정 | ✅ 완료 |
| Phase 4.6 | 시간 시스템 | 낮/밤 사이클·유동인구 모델 | ✅ 완료 |
| Phase 4.7 | 그리드 시스템 | 200x200 영토 기반 인구 & 맵 | ✅ 완료 |
| Phase 5 | 웹 대시보드 | React + TypeScript 실시간 시각화 | ✅ 완료 |
| Phase 5.5 | 성능 최적화 | Snapshot-after-Commit·Dirty Region·Delta Payload | ✅ 완료 |
| Phase 6 | CI/CD | GitHub Actions 자동화 및 정적 분석, 도커라이징 | ✅ 완료 |
| Phase 7 | Plugin SDK | Python·C# SDK 구현 | ✅ 완료 |

---

## Phase 2 — YAML 종족 데이터 ✅

### 목표
docs/race_specs.md의 내용을 실제 YAML 파일로 변환한다.
Python 설정 로더로 자동 탐색·로드한다.

### 작업 목록
- [x] `configs/races/humanoids/human.yaml`
- [x] `configs/races/humanoids/elf.yaml`
- [x] `configs/races/humanoids/dwarf.yaml`
- [x] `configs/races/humanoids/orc.yaml`
- [x] `configs/races/humanoids/halfling.yaml`
- [x] `configs/races/beastmen/beastman.yaml`
- [x] `configs/races/beastmen/half_beast.yaml`
- [x] `configs/races/beastmen/fairy.yaml`
- [x] `configs/races/mythic/dragon.yaml`
- [x] `configs/races/mythic/undead.yaml`
- [x] `configs/races/mythic/angel_demon.yaml`
- [x] `configs/races/others/elemental.yaml`
- [x] `configs/races/others/golem.yaml`
- [x] `configs/worlds/default_world.yaml`
- [x] `src/config/race_loader.py`
- [x] `src/config/world_loader.py`
- [x] `tests/test_config/test_loaders.py`

---

## Phase 3 — 시뮬레이션 코어 ✅

### 목표
YAML로 정의된 종족들이 실제로 시뮬레이션에서 행동하게 한다.

### 작업 목록
- [x] `src/core/world.py` — World 클래스, tick() 메인 루프
- [x] `src/core/race_agent.py` — 종족 AI 행동 결정
- [x] `src/core/diplomacy.py` — 친밀도 시스템
- [x] `src/core/event_system.py` — 이벤트 발생·처리
- [x] `src/core/models.py` — 전역 데이터 타입 (RaceState, Faction 등)
- [x] `src/core/faction_manager.py` — 파벌 CRUD + 종교 교세 + 초월자
- [x] `src/core/map.py` — 200x200 그리드 맵 (Hub 기반 지형 생성)

---

## Phase 4 — FastAPI REST 서버 ✅

### 목표
시뮬레이션을 HTTP API로 외부에서 제어 가능하게 한다.

### 작업 목록
- [x] `src/api/main.py` — FastAPI 앱 진입점 (lifespan, CORS)
- [x] `src/api/schemas.py` — Pydantic 응답 스키마
- [x] `src/api/routes/simulation.py` — POST /tick, /run, /reset
- [x] `src/api/routes/world.py` — GET /world, /races, /diplomacy, /events, /leaderboard
- [x] `src/api/routes/factions.py` — GET /factions, POST /{id}/transcendent
- [x] `src/api/websocket_manager.py` — WebSocket 실시간 브로드캐스트

---

## Phase 5 — 웹 대시보드 ✅

### 목표
실시간으로 세계 현황을 브라우저에서 한눈에 확인한다.

### 구현 내용
- **MapCanvas**: Canvas API 기반 200x200 그리드 렌더링 (40,000 타일)
- **Hub 기반 방사형 지형 생성**: 5대 거점 기반 클러스터링 알고리즘
- **영토 시각화**: 파벌 소유권 색상 + 거점 마커 + 하이라이트
- **TileInspector**: 타일 클릭 시 지형/파벌 상세 정보 패널
- **이벤트 로그**: 실시간 피드
- **Glassmorphism 다크 테마**: Dark Mode / 프리미엄 디자인

### 기술 스택
- React 18 + TypeScript + Vite
- WebSocket (실시간 업데이트)
- Canvas API (세계 지도)
- Vanilla CSS (12컬럼 그리드 시스템)

---

## Phase 6 — CI/CD ✅

### 목표
PR마다 자동 테스트, main 병합 시 린트/타입 체크 및 통제 가능 배포.

### 구현 결과
- **정적 분석**: `ruff` 및 `mypy` 검사를 통한 오류 0 세팅.
- **테스트 최적화**: `pytest`를 도입해 Dirty Region 알고리즘 등 단위 테스트 추가.
- **도커화**: 백엔드와 프론트엔드의 독립 환경(`Dockerfile`, `docker-compose.yml`) 세팅 완료.
### CI/CD 워크플로우
- `.github/workflows/ci.yml` : Push 및 PR 발생 시 Python 3.11 환경에서 Lint/Mypy/Pytest 자동 수행.
- `.github/workflows/cd.yml` : 버전 태그 Push 발생 시 Docker 빌드 환경 자동 구축.

---

## Phase 7 — Plugin SDK ✅

### 목표
외부 게임 엔진에서 WorldAI를 쉽게 연동할 수 있는 SDK 제공.

### 구현 결과
- **Python SDK (`src/sdk/python/worldai_client.py`)**: `httpx`, `websockets` 비동기 연결 구현. 이벤트 리스너 통합.
- **C# SDK (`src/sdk/csharp/WorldAIClient.cs`)**: Unity 구동을 고려한 `HttpClient`, `ConcurrentQueue` 구조 탑재 비동기 랩퍼 완성.
- **REST 클라이언트 가이드**: `src/sdk/README.md` 로 SDK 연동 구조 문서화 완료.

---

## 향후 확장 계획 (Post v1.0)

| 기능 | 설명 |
|------|------|
| LLM 연동 | 종족 지도자 AI 대화 (ChatGPT API) |
| 멀티 대륙 | 여러 대륙이 있는 더 큰 세계 |
| 커스텀 이벤트 | 사용자가 YAML로 이벤트 직접 정의 |
| 역사 기록 | 시뮬레이션 전체 역사를 자동 생성 |
| 웹 에디터 | 브라우저에서 종족·세계관 편집 |
