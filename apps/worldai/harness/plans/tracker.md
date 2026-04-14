# WorldAI — Phase 상태 트래커

> **마지막 업데이트**: 2026-04-15
> **현재 Phase**: Phase 7 완료 (Plugin SDK 연동 완료)

---

## 📊 전체 Progress

| Phase | 이름 | 상태 | 커밋 |
|-------|------|------|------|
| Phase 0 | 하네스 골격 구축 | ✅ 완료 | #1 |
| Phase 1 | 기획 문서 작성 | ✅ 완료 | #2 |
| Phase 2 | YAML 종족 데이터 + 로더 | ✅ 완료 | #3~#4 |
| Phase 3 | 시뮬레이션 코어 | ✅ 완료 | #5 |
| Phase 3.5 | 파벌·종교·초월자 시스템 | ✅ 완료 | #7 |
| Phase 4 | FastAPI REST 서버 | ✅ 완료 | #8 |
| Phase 4.5 | 밸런스 수정 (이벤트 시스템) | ✅ 완료 | #9 |
| Phase 4.6 | 시간 시스템 모델 (낮/밤·유동인구) | ✅ 완료 | #11 |
| Phase 4.7 | 영토 기반 인구 & 그리드 시스템 | ✅ 완료 | #12 |
| Phase 5 | 웹 대시보드 (실시간 시각화 2.0) | ✅ 완료 | #13~#15 |
| Phase 5.5 | 성능 최적화 (Snapshot-after-Commit·Dirty Region) | ✅ 완료 | #16 |
| Phase 6 | CI/CD 구축 (Ruff, Mypy, Actions, Docker) | ✅ 완료 | 머지 전 |
| Phase 7 | Plugin SDK | ✅ 완료 | 머지 전 |

---

## ✅ 완료 내역 요약

### 핵심 파일 구조
```
apps/worldai/src/core/
  models.py          - 전역 데이터 타입 (RaceState, Faction, Character 등)
  diplomacy.py       - 비대칭 친밀도 + 임계값 이벤트 (60틱 쿨다운)
  race_agent.py      - 종족 행동 AI
  world.py           - 메인 틱 루프
  event_system.py    - 랜덤 이벤트 (습격/기근/몬스터/역병)
  faction_manager.py - 파벌 CRUD + 종교 교세 + 초월자
  map.py             - 200x200 Hub 기반 지형 생성 + Dirty Region (Enum Sync 완료)

apps/worldai/src/api/
  main.py               - FastAPI 앱 (lifespan, CORS, 기본 파벌 13종)
  schemas.py            - Pydantic 응답 스키마
  websocket_manager.py  - WebSocket 연결 관리 + 실시간 브로드캐스트
  routes/
    simulation.py       - POST /simulation/tick, /run, /reset
    world.py            - GET /world, /world/map, /leaderboard, /events
    factions.py         - GET /factions, POST /factions/{id}/transcendent

apps/worldai/src/config/
  loader.py          - YAML 설정 로더 (종족·세계관 자동 탐색)

apps/worldai/src/sdk/
  README.md          - SDK 연동 가이드 (C#/Python 사용 예시)
  python/
    worldai_client.py - httpx + websockets 기반 비동기 Python 클라이언트
    example.py        - 사용 예시
  csharp/
    WorldAIClient.cs  - HttpClient + ConcurrentQueue 기반 Unity 대응 C# 클라이언트
    Models.cs         - 응답 DTO (FactionDto, EventDto, WsMessage 등)

apps/worldai/
  Dockerfile            - Python 백엔드 컨테이너
  docker-compose.yml    - engine(8000) + dashboard(80) 멀티 컨테이너
  dashboard/Dockerfile  - React 프론트엔드 컨테이너

.github/workflows/
  ci.yml  - Push/PR 시 Ruff·Mypy·Pytest 자동 실행
  cd.yml  - 버전 태그 Push 시 Docker 빌드 환경 구성

docs/
  world_design.md       - 대륙 7개 권역, 다중 파벌 공존
  race_specs.md         - 13개 종족 상세 스펙
  faction_system.md     - 파벌 소속/규모 체계
  religion_system.md    - 교단 시스템
  rank_level_system.md  - 등급/레벨/직위 3축
  transcendent_system.md - 초월자 시스템
  time_system.md        - 시간 시스템
```

---

## 🔄 Phase 4.6 — 시간 시스템 (진행 중)

### 확정된 설계 결정

```
[확정] 1틱 = 1시간 (world YAML의 tick_unit으로 설정 가능)
[확정] 1일 = 24틱, 1계절 = 2160틱 (90일), 1년 = 8640틱
[확정] 온라인 전용: 플레이어 행동 시에만 틱 진행 (오프라인 시 시간 정지)
[확정] 세션 기반: 플레이어 접속 → 이전 상태 로드 → 행동 → 틱 처리 → 반환
[확정] 낮/밤 5구간: DEEP_NIGHT / DAWN / DAY / DUSK / NIGHT
[확정] 계절별 일조: 봄·가을 12h, 여름 16h, 겨울 8h
[확정] 종족별 시간대 활성도 배율 (언데드 DEEP_NIGHT: 2.0, 등)
[확정] 유동 인구 5타입: SETTLER / MERCHANT / ADVENTURER / MILITARY / REFUGEE
[확정] 정착민은 인구 과잉에도 이동 안 함 (기근·전쟁 시에만 이주민 전환)
[확정] 200x200 그리드 맵: 중점(Hub) 기반 방사형 생성 (0:Water, 1:Plains...)
[확정] 틱당 이동: 1틱(1시간)마다 인접 1타일 이동 가능
[미확정] 멀티플레이어 시 틱 동기화 방식
```

### 작업 목록

- [x] `docs/time_system.md` 작성 완료
- [x] `models.py`: `DayPhase`, `PopulationType`, `PopulationSegment`, `TimeConfig` 추가
- [x] `world.py`: `hour_of_day`, `day_phase` 프로퍼티, 활성도 배율 적용
- [x] `event_system.py`: 이벤트 확률 1틱=1시간 기준으로 재조정
- [x] `configs/worlds/asteria.yaml`: `time_config` 블록 추가 (`default_world.yaml`)
- [x] `faction_manager.py`: `PopulationSegment` 모델 설계 완료 (구체적 통합은 Phase 5 전후 백로그로 이동)

- [x] 백엔드: WebSocket 매니저 및 틱 브로드캐스트 로직 구현
- [x] 프론트엔드: Vite + React 대시보드 구축 (MapCanvas, StatsDashboard)
- [x] 프리미엄 디자인(Dark Mode, Glassmorphism) 적용 완료
- [x] 기능 고도화: 영토 소유권 시각화, 거점 하이라이트, 200x200 좌표 정규화 정밀 제어
- [x] 지형 엔진 혁신: 5대 거점(Hub) 기반 방사형 지형 생성 및 군집화(Clustered) 로직 적용
- [x] 데이터 정합성: 백엔드-프론트엔드 지형 Enum Index (0:WATER...) 완벽 동기화
- [x] 버그 수정: TileInspector 크래시 해결 및 100x80 YAML 설정 오버라이드 해결

---

## ✅ Phase 5.5 — 성능 최적화

### 구현 내용

| 패턴 | 파일 | 설명 |
|---|---|---|
| **Snapshot-after-Commit** | `simulation.py` | 틱 전 처리 완료 후 단일 브로드캐스트 — 클라이언트 중간 상태 노출 차단 |
| **Dirty Region** | `map.py` | 인구 변화 파벌 반경 타일만 재계산 (전체 40,000 타일 순회 제거) |
| **Delta Payload** | `simulation.py` | WebSocket에 변경된 타일만 포함 (`territory_delta`) — 페이로드 최소화 |

### 설계 결정
```
[확정] territory_delta = 변경 타일 index + owner만 전송 (전체 territories 배열 전송 금지)
[확정] _territory_cache: FactionManager에 이전 틱 territories 배열 캐시
[확정] 초기 로드 / 강제 리프레시는 get_territory_data() (전체 계산) 사용
[확정] Dirty Region 반경 = max(10, int(pop^0.4 * 10^0.5) + 2) 타일
```

---

## ✅ Phase 6 — CI/CD 자동화 및 통제 환경 구축

### 구현 내용
| 항목              | 설명                                                                 |
| ----------------- | -------------------------------------------------------------------- |
| **정적 분석 보수**| `ruff`(린팅) 및 `mypy`(타입 무결성) 전면 검사 및 에러율 0 달성        |
| **GitHub Actions**| `/workflows/ci.yml` (테스트 자동화), `cd.yml` (배포 뼈대) 구축        |
| **도커화(Docker)**| `Dockerfile`, `docker-compose.yml`을 통한 멀티 컨테이너 원클릭 인프라 |
| **유닛 테스트**   | `pytest` 적용, `get_territory_delta` 최적화 로직의 부분 갱신 검증 완료 |

---

## ✅ Phase 7 — 플러그인 SDK 연동

### 목표
유니티/C++ 등 프론트 외부 시스템에서 WorldAI 코어를 제어할 수 있는 SDK 및 API 확충.

### 구현 내용
| 언어 | 경로 | 설명 |
|---|---|---|
| **Python** | `src/sdk/python/worldai_client.py` | `httpx`, `websockets` 기반의 외부 봇/마이크로서비스용 비동기 클라이언트 |
| **C#** | `src/sdk/csharp/WorldAIClient.cs` | `HttpClient`, `ClientWebSocket` 및 `ConcurrentQueue`를 사용한 Unity/순수 C# 대응 비동기 클라이언트 |
| **C# 모델** | `src/sdk/csharp/Models.cs` | 응답 DTO (`FactionDto`, `EventDto`, `WsMessage`) |
| **명세** | `src/sdk/README.md` | 각종 언어별 초기화 방법 및 아키텍처 설명서 작성 |


---

## 📋 향후 백로그

> **상세 기능 목록 및 우선순위** → `docs/planning/feature_backlog.md` 참조  
> **WorldBox 기능 분석 및 대응표** → `docs/planning/worldbox_reference.md` 참조

### 요약 (상위 우선순위)

| 순위 | 기능 | 난이도 | 참고 |
|------|------|--------|------|
| 1 | 반란/독립 이벤트 | 낮음 | WorldBox 반란 시스템 |
| 2 | 플레이어 신(God) 개입 API | 낮음 | WorldBox 신의 능력 |
| 3 | 바이옴별 자원 생산 | 중간 | WorldBox 지형 자원 |
| 4 | 세계 시대 (Ages) 시스템 | 중간 | WorldBox Ages |
| 5 | 영토 기반 인구 분산 | 중간 | 기존 PopulationSegment 설계 |
| 6 | LLM 연동 (지도자 AI 대화) | 높음 | Claude API |
| 7 | 역사 기록 시스템 | 낮음 | `GET /world/history` |
| 8 | 저장/불러오기 | 낮음 | state_manager.py 신규 |

---

## ⚙️ 문서화된 매직넘버 (1틱=1시간 기준)

| 값 | 의미 | 근거 |
|----|------|------|
| `TICKS_PER_DAY = 24` | 하루 24시간 | 확정 |
| `TICKS_PER_SEASON = 2160` | 90일 × 24h | 확정 |
| `습격 주기 = 72틱` | 3일마다 | 너무 잦으면 게임 피로 |
| `역병 주기 = 720틱` | 30일마다 | 월 1회 |
| `몬스터 출현 = 240틱` | 10일마다 | 격주~월 2회 |
| `임계값 쿨다운 = 60틱` | 2.5일 | 같은 이벤트 최소 2.5일 간격 |
| `BOND delta 80% 감쇠` | 포화 방지 | 혈맹 이후 변화 느리게 |

---

## 📝 AI 인수인계 메모

```
[Phase 7 완료 — 2026-04-15]
Python SDK 및 C#(Unity 대응, ConcurrentQueue 적용) SDK가 무사히 구축되었습니다. Github Actions(CI)도 최신화 완료.

⚠️ 핵심 확인 사항:
  1. 외부 게임 클라이언트는 ws:// 접속 시 이벤트 스트림을 백그라운드 큐에 넣고 메인 스레드에서 반영해야 함.
  2. 현재 Phase 7로 v1.0 로드맵의 정규 개발이 완전 종료되었습니다.

다음 구현 순서 (Post v1.0):
  1. LLM 연동 또는 커스텀 이벤트 등 향후 확장 계획
```
