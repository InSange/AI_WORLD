# WorldAI — Phase 상태 트래커

> **마지막 업데이트**: 2026-04-06
> **현재 Phase**: Phase 5 완료 (실시간 영토 가시성 2.0 및 버그 수정 완료)

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
  map.py           - 100x80 그리드 맵 시스템 ← 신규 추가
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
[확정] 100x80 그리드 맵: 위도(Y) 기준 지형 생성 (북부-설원, 중앙-평원, 남부-사막)
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
- [x] 기능 고도화: 영토 소유권 시각화, 거점 하이라이트, 100x80 좌표 정규화 정밀 제어
- [x] 버그 수정: 파벌 인구 세터 오류 해결 및 캔버스 렌더링 불일치 교정

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
- 100×80 격자에 지형 타입, 파벌 점령 상태 저장
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
[Antigravity → 다음 작업자]
Phase 5까지 완료. 실시간 웹 대시보드가 성공적으로 구축되어 WebSocket 통신이 가능함.
현재 100x80 그리드 맵과 인구/이벤트 실시간 피드가 시각적으로 표현됨.

서버 실행:
  cd apps/worldai
  python -m uvicorn src.api.main:app --reload --port 8000
  (별도 터미널) cd dashboard && npm run dev

다음 구현 순서 (Phase 6):
  1. GitHub Actions 워크플로우 설정 (.github/workflows/)
  2. 코어 로직의 단위 테스트(Pytest) 대폭 보강
  3. 프론트엔드 E2E 테스트 또는 빌드 자동화
  4. Docker Compose를 통한 원클릭 배포 환경 구축

핵심 포인트:
  - 대시보드는 `apps/worldai/dashboard/`에 위치함
  - 브로드캐스트 데이터 구조는 `src/api/websocket_manager.py`를 따름
  
docs/milestones/ 및 phase_5_dashboard.md 참고 필수.
```
