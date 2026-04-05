# WorldAI — 로드맵 (Roadmap)

> 최종 수정: 2026-04-05 | 현재 Phase: Phase 1 완료

---

## 마일스톤 개요

| Phase | 이름 | 목표 | 상태 |
|-------|------|------|------|
| Phase 0 | 하네스 골격 | 프로젝트 구조 + 문서 시스템 | ✅ 완료 |
| Phase 1 | 기획 문서 | 세계관·종족·시스템 설계 문서화 | ✅ 완료 |
| Phase 2 | YAML 데이터 | 15종족 설정 파일 + 설정 로더 | 🔜 예정 |
| Phase 3 | 시뮬레이션 코어 | Python 시뮬레이션 엔진 구현 | 🔜 예정 |
| Phase 4 | API 서버 | FastAPI REST 서버 구현 | 🔜 예정 |
| Phase 5 | 웹 대시보드 | React + TypeScript 시각화 | 🔜 예정 |
| Phase 6 | CI/CD | GitHub Actions 자동화 | 🔜 예정 |
| Phase 7 | Plugin SDK | Python·C# SDK 구현 | 🔜 예정 |

---

## Phase 2 — YAML 종족 데이터

### 목표
docs/race_specs.md의 내용을 실제 YAML 파일로 변환한다.
Python 설정 로더로 자동 탐색·로드한다.

### 작업 목록
- [ ] `configs/races/humanoids/human.yaml`
- [ ] `configs/races/humanoids/elf.yaml`
- [ ] `configs/races/humanoids/dwarf.yaml`
- [ ] `configs/races/humanoids/orc.yaml`
- [ ] `configs/races/humanoids/halfling.yaml`
- [ ] `configs/races/beastmen/beastman.yaml`
- [ ] `configs/races/beastmen/half_beast.yaml`
- [ ] `configs/races/beastmen/fairy.yaml`
- [ ] `configs/races/mythic/dragon.yaml`
- [ ] `configs/races/mythic/undead.yaml`
- [ ] `configs/races/mythic/angel_demon.yaml`
- [ ] `configs/races/others/elemental.yaml`
- [ ] `configs/races/others/golem.yaml`
- [ ] `configs/worlds/default_world.yaml`
- [ ] `src/config/race_loader.py`
- [ ] `src/config/world_loader.py`
- [ ] `tests/test_config/test_loaders.py`

### 완료 기준
```powershell
python -c "from src.config.race_loader import load_all_races; print(load_all_races())"
# → 15개 종족 정보 출력
```

---

## Phase 3 — 시뮬레이션 코어

### 목표
YAML로 정의된 종족들이 실제로 시뮬레이션에서 행동하게 한다.

### 작업 목록
- [ ] `src/core/world.py` — World 클래스, tick() 메인 루프
- [ ] `src/core/race_agent.py` — 종족 AI 행동 결정
- [ ] `src/core/diplomacy.py` — 친밀도 시스템
- [ ] `src/core/event_system.py` — 이벤트 발생·처리
- [ ] `src/core/combat_system.py` — 전투 계산
- [ ] `src/core/state_manager.py` — 상태 저장·로드 (JSON)
- [ ] `tests/test_core/`

### 완료 기준
```powershell
python -m src.core.world --ticks 100
# → 100틱 시뮬레이션 후 종족별 인구, 외교 상태 출력
```

---

## Phase 4 — FastAPI REST 서버

### 목표
시뮬레이션을 HTTP API로 외부에서 제어 가능하게 한다.

### 작업 목록
- [ ] `src/api/main.py` — FastAPI 앱 진입점
- [ ] `src/api/routers/world.py` — /world/ 엔드포인트
- [ ] `src/api/routers/races.py` — /races/ 엔드포인트
- [ ] `src/api/routers/diplomacy.py` — /diplomacy/ 엔드포인트
- [ ] `src/api/routers/simulate.py` — /simulate/ 엔드포인트
- [ ] `src/api/models.py` — Pydantic 응답 모델

### 완료 기준
```powershell
curl http://localhost:8000/world/state
# → JSON 형식으로 현재 세계 상태 반환
```

---

## Phase 5 — 웹 대시보드

### 목표
실시간으로 세계 현황을 브라우저에서 한눈에 확인한다.

### 주요 화면
- **세계 지도 (World Map)**: 종족 영토, 지형 타일 맵
- **종족 현황 (Race Status)**: 인구, 자원, 전투력 그래프
- **외교 관계 (Diplomacy)**: 친밀도 히트맵
- **이벤트 로그 (Event Log)**: 실시간 이벤트 피드
- **타임라인 컨트롤**: 틱 일시정지/재개, 속도 조절

### 기술 스택
- React 18 + TypeScript
- Vite (번들러)
- WebSocket (실시간 업데이트)
- D3.js 또는 Recharts (그래프)
- Canvas / Pixi.js (세계 지도)

---

## Phase 6 — CI/CD

### 목표
PR마다 자동 테스트, main 병합 시 대시보드 자동 배포.

### `.github/workflows/ci.yml`
```yaml
on: [push, pull_request]
jobs:
  lint: ruff check .
  type: mypy src/
  test: pytest tests/ --cov=src --cov-report=xml
  dashboard: npm run build
```

### `.github/workflows/cd.yml`
```yaml
on:
  push:
    branches: [main]
jobs:
  deploy-dashboard:
    # GitHub Pages에 대시보드 정적 배포
  publish-package:
    # PyPI에 worldai-sdk 배포 (Phase 7 이후)
```

---

## Phase 7 — Plugin SDK

### 목표
외부 게임 엔진에서 WorldAI를 쉽게 연동할 수 있는 SDK 제공.

### Python SDK (`src/sdk/python/`)
- `WorldAIClient` 클래스
- 동기/비동기 API 모두 지원
- PyPI 패키지 배포: `pip install worldai-sdk`

### C# SDK (`src/sdk/csharp/`)
- Unity용 `WorldAIClient.cs`
- NuGet 패키지 배포 (향후)
- async/await 패턴

### REST 클라이언트 가이드
- OpenAPI 스펙 (`/docs` 자동 생성)
- Postman 컬렉션 제공
- 연동 예제 (Unity, Unreal, C++, Godot)

---

## 향후 확장 계획 (Post v1.0)

| 기능 | 설명 |
|------|------|
| LLM 연동 | 종족 지도자 AI 대화 (ChatGPT API) |
| 멀티 대륙 | 여러 대륙이 있는 더 큰 세계 |
| 커스텀 이벤트 | 사용자가 YAML로 이벤트 직접 정의 |
| 역사 기록 | 시뮬레이션 전체 역사를 자동 생성 |
| 웹 에디터 | 브라우저에서 종족·세계관 편집 |
