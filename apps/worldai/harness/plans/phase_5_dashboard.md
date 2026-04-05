# Phase 5: 웹 대시보드 (실시간 시각화) 상세 계획

- **상위 문서**: [tracker.md](file:///c:/Users/선우/source/repos/WorldAI/apps/worldai/harness/plans/tracker.md)
- **현재 상태**: ✅ 완료 (2026-04-06)
- **작업 목표**: 시뮬레이션의 상태와 영토 소유권을 실시간으로 시각화하는 프리미엄 웹 인터페이스 구축.

---

## 1. 시스템 아키텍처

### Backend (FastAPI)
- **WebSocket Manager**: `src/api/websocket_manager.py`를 신설하여 클라이언트 연결 관리.
- **Broadcast System**: `simulation.py`의 `/tick` 또는 `/run` 종료 시 변경된 상태(맵, 인구, 이벤트)를 WS로 전파.

### Frontend (React + TypeScript)
- **Scaffold**: Vite (`apps/worldai/dashboard/`)
- **State Management**: React Context 또는 단순 `useEffect` 기반 WS 수신.
- **Components**:
    - `MapViewer`: Canvas API 기반 100x80 그리드 렌더링.
    - `EventLog`: Framer Motion 애니메이션이 적용된 실시간 피드.
    - `RaceStats`: Recharts 기반 인구/군사력/기술력 시계열 차트.

---

## 2. 세부 구현 로직

### 2.1 맵 시각화 (MapCanvas)
- 8,000개 타일을 효율적으로 그리기 위해 Canvas API 사용.
- 지형 타입별 색상 팔레트 완비 (9종 지형 범례).
- 파벌 거점(Capital) 다이아몬드 마커 및 종족별 고유 색상 적용.
- **영토-거점 하이라이트**: 영토 호버 시 해당 파벌의 본성과 점선 및 펄스 효과로 연결.

### 2.2 실시간 통신 (WebSockets)
- 클라이언트 접속 시 현재 세계 상태(Full Payload) 전송.
- 틱 발생 시마다 `SimulationStatus`와 `EventLog` 브로드캐스트.
- 틱 직후 `/factions` 데이터를 재로드하여 인구 변화 실시간 동기화.

### 2.3 레이아웃 (Vanilla CSS)
- Tailwind 의존성 없이 `index.css`에 직접 정의된 12컬럼 그리드 시스템.
- Glassmorphism 기반의 투명 카드 및 다크 모드 테마.

---

## 3. 디자인 시스템 (Premium Aesthetics)

- **테마**: 다크 모드 (배경: #0a0a0a)
- **색채**:
    - 평원: `hsl(120, 40%, 30%)`
    - 사막: `hsl(45, 50%, 40%)`
    - 설원: `hsl(200, 10%, 80%)`
- **폰트**: Inter (Google Fonts)
- **레이아웃**: 2컬럼 그리드 (좌: 맵 / 우: 통계 및 로그)

---

## 4. 할 일 목록 (Checklist)

- [x] 백엔드: `websocket_manager.py` 및 브로드캐스트 로직 구현
- [x] 백엔드: Simulation/World API 스키마 확장 (hour, territories 추가)
- [x] 프론트엔드: Vite 프로젝트 초기화 및 고정 그리드 레이아웃 구축
- [x] 프론트엔드: MapCanvas 시각화 2.0 (거점 마커, 하이라이트 연결) 개발
- [x] 프론트엔드: TileInspector 상세 정보 패널 구현
- [x] 프론트엔드: 실시간 이벤트 피드 및 범례(Legend) 개발
- [x] 통합: 100x80 전체 그리드에 대한 정밀 마우스 좌표 인식 최적화

---

## 🔗 참고 문서
- [전체 프로젝트 가이드 (AGENTS.md)](file:///c:/Users/선우/source/repos/WorldAI/AGENTS.md)
- [시뮬레이션 상태 트래커 (tracker.md)](file:///c:/Users/선우/source/repos/WorldAI/apps/worldai/harness/plans/tracker.md)
