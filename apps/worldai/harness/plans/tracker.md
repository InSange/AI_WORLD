# WorldAI — Phase 상태 트래커

> **마지막 업데이트**: 2026-04-06
> **현재 Phase**: Phase 5 준비 중 (Phase 4.5까지 완료)

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
| Phase 4.6 | 시간 시스템 모델 (낮/밤·유동인구) | 🔄 진행 중 | - |
| Phase 5 | 웹 대시보드 (실시간 시각화) | ⬜ 대기 | - |
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
  time_system.md    - 시간 시스템 ← 신규 추가
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
[미확정] 멀티플레이어 시 틱 동기화 방식
```

### 작업 목록

- [x] `docs/time_system.md` 작성 완료
- [ ] `models.py`: `DayPhase`, `PopulationType`, `PopulationSegment`, `TimeConfig` 추가
- [ ] `world.py`: `hour_of_day`, `day_phase` 프로퍼티, 활성도 배율 적용
- [ ] `event_system.py`: 이벤트 확률 1틱=1시간 기준으로 재조정
- [ ] `configs/worlds/asteria.yaml`: `time_config` 블록 추가
- [ ] `faction_manager.py`: `PopulationSegment` 기반 파벌 인구 관리

---

## 🔜 Phase 5 — 웹 대시보드

### 목표
실시간 세계 시각화 웹 인터페이스.

### 계획
- WebSocket: 틱마다 자동 갱신
- 100×80 맵: 종족 영역·파벌 위치 시각화
- 외교 관계 그래프 (네트워크 다이어그램)
- 이벤트 피드 (실시간 스크롤)
- 인구·기술·군사력 시계열 차트
- 낮/밤 시각화 (맵 밝기 변화)

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
Phase 4.5까지 완료. 서버 정상 동작 확인.
Phase 4.6 진행 중 (시간 시스템 모델 미구현).

서버 실행:
  cd apps/worldai
  py -m uvicorn src.api.main:app --port 8000 --reload

다음 구현 순서:
  1. models.py에 DayPhase/PopulationType/TimeConfig 추가
  2. world.py에 hour_of_day, day_phase 프로퍼티 + 2160틱/계절 설정
  3. event_system.py 이벤트 확률 재조정 (1틱=1시간 기준)
  4. asteria.yaml에 time_config 블록 추가
  5. Phase 5 웹 대시보드

핵심 설계:
  - 1틱 = 1시간, 온라인 전용 틱 처리
  - 낮/밤 5구간 × 종족별 활성도 배율
  - 유동 인구 5타입 (SETTLER 70% / MERCHANT 10% / ADVENTURER 8% / MILITARY 10% / REFUGEE 2%)
  - 플레이어는 그리드 단위로 존재, 1틱=1행동
  
docs/time_system.md 참고 필수.
```
