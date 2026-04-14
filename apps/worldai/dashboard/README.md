# WorldAI — 웹 대시보드

> React 18 + TypeScript + Vite 기반 실시간 시뮬레이션 시각화 대시보드

---

## 실행 방법

```bash
# 의존성 설치
npm install

# 개발 서버 실행 (http://localhost:5173)
npm run dev

# 프로덕션 빌드
npm run build
```

> **주의**: 백엔드 API 서버(`uvicorn src.api.main:app --reload --port 8000`)가 먼저 실행되어 있어야 합니다.

---

## 주요 컴포넌트

| 컴포넌트 | 설명 |
|----------|------|
| `MapCanvas` | Canvas API 기반 200x200 그리드 지형 렌더링 (40,000 타일) |
| `TileInspector` | 타일 클릭 시 지형/파벌 상세 정보 패널 |
| `StatsDashboard` | 종족별 인구·군사력·기술력 통계 |
| `EventLog` | 실시간 이벤트 피드 |

---

## 지형 색상 팔레트 (Enum Index 동기화 필수)

백엔드 `src/core/map.py`의 `TileType` Enum 순서와 프론트엔드 `TILE_COLORS` 배열 인덱스가 반드시 일치해야 합니다.

```
0: WATER     1: PLAINS    2: FOREST    3: MOUNTAIN
4: DESERT    5: SNOW      6: WASTELAND 7: TUNDRA
8: TROPICAL
```

---

## WebSocket 통신

- 접속 시: 전체 상태 Full Payload 수신
- 틱 발생 시: `territory_delta` (변경된 타일만) + `SimulationStatus` + `EventLog` 브로드캐스트
- REST 폴백: `GET /world/tiles` 로 전체 영토 재동기화 가능
