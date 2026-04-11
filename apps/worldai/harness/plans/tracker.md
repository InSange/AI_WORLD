# WorldAI — Phase 상태 트래커

> **마지막 업데이트**: 2026-04-11
> **현재 Phase**: Phase 5.5 완료 (Snapshot-after-Commit·Dirty Region 최적화 구현)

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
| Phase 6 | CI/CD 구축 | ⬜ 대기 | - |
| Phase 7 | Plugin SDK | ⬜ 대기 | - |

---

## ✅ 완료 내역 요약

### 핵심 파일 구조
```
apps/worldai/src/core/
  models.py         - 전역 데이터 타입 (RaceState, Faction, Character 등)
  diplomacy.py      - 비대칭 친밀도 + 임계값 이벤트 (60틱 쿨다운)
  race_agent.py     - 종족 행동 AI
  world.py          - 메인 틱 루프
  event_system.py   - 랜덤 이벤트 (습격/기근/몬스터/역병)
  faction_manager.py - 파벌 CRUD + 종교 교세 + 초월자

apps/worldai/src/api/
  main.py           - FastAPI 앱 (lifespan, CORS, 기본 파벌 11종)
  schemas.py        - Pydantic 응답 스키마
  routes/
    simulation.py   - POST /tick, /run, /reset
    world.py        - GET /world, /races, /diplomacy, /events, /leaderboard
    factions.py     - GET /factions, POST /{id}/transcendent

docs/
  world_design.md   - 대륙 7개 권역, 다중 파벌 공존
  race_specs.md     - 11개 종족 상세 스펙
  faction_system.md - 파벌 소속/규모 체계
  religion_system.md - 교단 시스템
  rank_level_system.md - 등급/레벨/직위 3축
  transcendent_system.md - 초월자 시스템
  time_system.md    - 시간 시스템
  map.py           - 200x200 중점 기반 지형 시스템 (Enum Sync 완료)
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

## 🔜 Phase 6 — CI/CD 구축 (준비 중)

### 목표
GitHub Actions를 이용한 자동화된 워크플로우 구축 전반.

### 계획
- **자동 테스트**: `pytest`를 통한 코어 엔진 및 API 자동 검증
- **빌드 파이프라인**: 대시보드(Frontend) 정적 빌드 및 배포 자동화
- **정적 분석**: `flake8`, `mypy`, `eslint`를 통한 코드 품질 관리
- **도커화**: 전체 시스템(FastAPI + Dashboard) Docker 컨테이너화 고려

---

## 📋 향후 백로그

### [HIGH] 영토 기반 인구 계산
```
현재: 종족 전체 인구 = 단일 숫자
목표: 각 파벌(마을)에 유동 타입별 인구 분산 저장
      마을 인구가 늘면 이벤트 발생 확률 증가
      유동 타입: 정착민(이동 안 함) / 상인·모험가(이동 가능) / 군인(명령 기반)
      전투 = 해당 타일 군인 수로만 계산
      영토 점령/해방 → 인구 재배치 이벤트

RaceState.population → Faction별 PopulationSegment 합산으로 변경
```

### [HIGH] 플레이어 그리드 API
```
POST /player/register          - 플레이어를 특정 그리드에 등록
POST /player/action            - 이번 틱 행동 등록
GET  /player/events            - 내 그리드 이벤트 + 선택지
POST /player/choice            - 이벤트 선택지 응답
GET  /player/grid-view         - 반경 N타일 현황
```

### [MEDIUM] 세계 지도 타일 시스템
- 100×100 격자에 지형 타입, 파벌 점령 상태 저장
- Faction.territory_tiles → 실제 타일 좌표 목록

### [MEDIUM] 역사 기록 시스템
- 주요 이벤트 연대기 저장
- `GET /world/history?year=3`

### [LOW] 저장/불러오기
- `POST /simulation/save` / `POST /simulation/load`

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
[Phase 5.5 완료 — 2026-04-11]
맵 200x200 확정. Snapshot-after-Commit / Dirty Region / Delta Payload 3중 최적화 구현 완료.

⚠️ 핵심 확인 사항:
  1. 지형 Enum 동기화: map.py TileType 순서 ↔ MapCanvas.tsx TILE_COLORS(0:Water...) 반드시 일치.
  2. 맵 크기: default_world.yaml width/height = 200 확인 (변경 시 프론트 좌표 정규화 깨짐).
  3. 영토 캐시: fm._territory_cache 초기화 전 get_territory_data() 전체 계산 1회 필요.
     → main.py lifespan 및 /reset 엔드포인트에서 초기 캐시 세팅 완료.
  4. territory_delta: WebSocket UPDATE 메시지에 포함. 클라이언트 미처리 시 무시해도 무방
     (REST /world/tiles 호출로 전체 재동기화 가능).

다음 구현 순서 (Phase 6):
  1. ✅ main.py lifespan + /reset에 _territory_cache 초기 세팅 완료
  2. GitHub Actions 워크플로우 (.github/workflows/)
  3. pytest 단위 테스트 보강 (get_territory_delta 포함)
```
