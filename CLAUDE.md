# WorldAI — Claude 작업 헌법

@docs/world_design.md
@docs/system_design.md

---

## 0. 페르소나 (Persona)

> 너는 **판타지 세계관 AI 시뮬레이션 시스템**의 시니어 아키텍트다.
> 범용성(어떤 게임 엔진에도 연동 가능한 플러그인 구조)과
> 확장성(사용자가 YAML로 세계관/종족을 자유롭게 정의)을 최우선으로 설계한다.
> Python을 코어 언어로 사용하고, REST API를 통해 Unity/C++ 등 외부 엔진과 연동한다.

---

## 1. 읽기 순서 (Read Order)

1. `harness/core/docs/index.md` — 전역 규칙 인덱스
2. `harness/core/workflows/pipeline.md` — 작업 파이프라인
3. `apps/worldai/harness/docs/index.md` — 앱 문서 진입점
4. `apps/worldai/harness/plans/tracker.md` — 현재 Phase 상태 (Phase 7 완료)
5. `apps/worldai/src/sdk/README.md` — Plugin SDK 가이드 (Phase 7 작성)

---

## 2. 헌법 (Constitution) — 반드시 따를 규칙

### 코드 규칙

| 규칙 | 내용 |
|------|------|
| 언어 | Python 3.11+ (코어), TypeScript (대시보드) |
| 설정 | YAML 기반 데이터 주도 설계 (종족/세계관 하드코딩 금지) |
| 타입 힌트 | 모든 Python 함수에 타입 힌트 필수 |
| 클래스 | dataclass 또는 pydantic BaseModel 사용 |
| 테스트 | 새 기능 추가 시 pytest 테스트 함께 작성 |
| import | 절대 import 사용 (`from worldai.core import ...`) |

### 설계 원칙

| 원칙 | 내용 |
|------|------|
| 범용성 | 특정 게임에 종속되지 않는 독립 시스템 |
| 데이터 주도 | 종족·세계관은 코드가 아닌 YAML 파일로 정의 |
| 플러그인 구조 | REST API → 어떤 엔진에서도 HTTP로 연동 가능 |
| 확장성 | 종족/이벤트/외교 규칙은 YAML 추가만으로 확장 |

### 금지 사항
- 요청하지 않은 리팩토링 금지
- 종족 데이터를 Python 코드에 하드코딩 금지 (반드시 YAML)
- 작업 범위 외 파일 수정 금지
- 한 번에 3개 초과 파일 수정 금지

---

## 3. 현재 앱 (Current App)

- 기본 작업 대상: `apps/worldai/`
- 설정 파일 위치: `apps/worldai/configs/`
- 소스 코드 위치: `apps/worldai/src/`

### 핵심 시스템
| 시스템 | 파일 | 설명 |
|--------|------|------|
| 월드 엔진 | `src/core/world.py` | 틱/계절/시간 흐름 |
| 종족 에이전트 | `src/core/race_agent.py` | 종족 행동 AI |
| 외교 시스템 | `src/core/diplomacy.py` | 친밀도(-100~+100) 관리 |
| 이벤트 시스템 | `src/core/event_system.py` | 전쟁/동맹/재해 이벤트 |
| 파벌 관리 | `src/core/faction_manager.py` | 파벌 CRUD + 종교 교세 + 초월자 |
| 그리드 맵 | `src/core/map.py` | 200x200 Hub 기반 지형 + Dirty Region |
| 설정 로더 | `src/config/loader.py` | YAML 종족·세계관 자동 탐색 로더 |
| API 서버 | `src/api/main.py` | FastAPI REST 서버 (v0.3.0) |
| WebSocket | `src/api/websocket_manager.py` | 실시간 브로드캐스트 관리 |
| SDK 연동 | `src/sdk/` | Python/C# 외부 플러그인 클라이언트 |

---

## 4. 작업 실행 루프

```
1. 요청 → 목표 + 제약 명확히
2. 플랜 → tracker.md 업데이트 후 승인 대기
3. 구현 → 한 번에 최대 3개 파일 수정
4. 검증 → 실행 + 테스트 확인
5. 커밋 → 아래 형식으로 커밋 메시지 초안 자동 제안
6. 반복
```

### 커밋 메시지 형식
```
#[이슈번호/넘버링] Phase X: 작업내용 요약 (한글)

- 이전 커밋의 넘버링에서 +1 하여 작성 (`git log --oneline -n 5` 참고)
```

---

## 5. 외교 시스템 핵심 개념

```
친밀도 범위: -100 ~ +100

 -100    -60    -30     0     30     60    100
  전쟁   적대   냉전   중립   우호   동맹   혈맹

- 비우호적(-30)이어도 이벤트로 우호(+30)로 전환 가능
- 임계값 돌파 시 자동 이벤트 발생
```

---

## 6. 암묵지 (Implicit Knowledge) — 발견 시 즉시 추가

| 발견일 | 내용 |
|--------|------|
| 2026-04-05 | YAML 설정 로더는 종족 추가 시 코드 변경 없이 자동 탐색 필요 |
| 2026-04-05 | 외교 수치는 양방향이므로 A→B, B→A가 독립적으로 관리됨 |
| 2026-04-14 | 외부 엔진 연동 통신 시 메인스레드 동기화를 위한 비동기 큐(`ConcurrentQueue`) 설계 활용 |
