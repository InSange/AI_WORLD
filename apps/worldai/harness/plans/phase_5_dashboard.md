# Phase 5: 웹 대시보드 (실시간 시각화) 상세 계획

- **상위 문서**: [tracker.md](file:///c:/Users/선우/source/repos/WorldAI/apps/worldai/harness/plans/tracker.md)
- **현재 상태**: ⬜ 계획 중 (승인 대기)
- **작업 목표**: 시뮬레이션의 상태와 이벤트를 실시간으로 시각화하는 프리미엄 웹 인터페이스 구축.

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
- 8,000개 타일을 효율적으로 그리기 위해 `requestAnimationFrame`과 Canvas API 사용.
- 지형 타입별 색상 팔레트 (HSL 기반 프리미엄 룩 적용).
- 파벌 위치에 심볼 표시 및 마우스 오버 시 정보 툴팁 제공.

### 2.2 실시간 통신 (WebSockets)
- 클라이언트 접속 시 현재 세계 상태(Full Payload) 전송.
- 틱 발생 시마다 `Diff` 또는 `Incremental Update` 전송 고려 (데이터량 최적화).

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

- [ ] 백엔드: `websocket_manager.py` 구현
- [ ] 백엔드: `main.py`에 WS 라우터(/ws) 추가
- [ ] 백엔드: 틱 결과 브로드캐스트 로직 연동
- [ ] 프론트엔드: Vite 프로젝트 초기화 (apps/worldai/dashboard)
- [ ] 프론트엔드: 디자인 시스템 및 공통 레이아웃 구축
- [ ] 프론트엔드: MapCanvas 컴포넌트 개발
- [ ] 프론트엔드: 실시간 이벤트 피드 및 차트 개발
- [ ] 통합: 실제 틱 진행 시 UI 갱신 성능 최적화

---

## 🔗 참고 문서
- [전체 프로젝트 가이드 (AGENTS.md)](file:///c:/Users/선우/source/repos/WorldAI/AGENTS.md)
- [시뮬레이션 상태 트래커 (tracker.md)](file:///c:/Users/선우/source/repos/WorldAI/apps/worldai/harness/plans/tracker.md)
