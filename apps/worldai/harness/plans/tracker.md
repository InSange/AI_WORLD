# WorldAI — Phase 상태 트래커

> **마지막 업데이트**: 2026-04-06
> **현재 Phase**: Phase 5 대기 (Phase 4까지 완료)

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
| Phase 5 | 웹 대시보드 (실시간 시각화) | ⬜ 대기 | - |
| Phase 6 | CI/CD 구축 | ⬜ 대기 | - |
| Phase 7 | Plugin SDK | ⬜ 대기 | - |

---

## ✅ 완료 내역 (Phase 3~4.5)

### Phase 3 — 시뮬레이션 코어 (`src/core/`)

| 파일 | 역할 |
|------|------|
| `models.py` | Season/AffinityLevel/RaceState/EventLog/Action/TickResult 등 전역 데이터 타입 |
| `diplomacy.py` | 비대칭 친밀도 관리, 임계값 이벤트(혈맹/동맹/전쟁), 자연 감쇠 |
| `race_agent.py` | 행동 AI (위협→교역→협상→연구 우선순위) |
| `world.py` | 메인 틱 루프 (계절/인구/외교/행동/기술) |
| `event_system.py` | 랜덤 이벤트: 인구 과밀→영역확장/기근, 습격, 몬스터 토벌, 역병 |

### Phase 3.5 — 파벌·종교·초월자 시스템

| 파일/문서 | 내용 |
|---------|------|
| `models.py` (추가) | Faction / Character / Religion / TranscendentInfo 데이터 타입 |
| `faction_manager.py` | 파벌 CRUD, 부모-자식 소속, 30틱마다 교세 전파, 초월자 이벤트 |
| `docs/faction_system.md` | 소속 유형 (colony/vassal/independent), 마을~제국 규모 체계 |
| `docs/religion_system.md` | 6가지 교단, 교세 전파, 교단 간 갈등 |
| `docs/rank_level_system.md` | 등급(Grade)/레벨(Level)/직위(Title) 3축 분리, 종족별 등급 |
| `docs/transcendent_system.md` | 초월 조건, 용인 진화, 세계 5대 신물 |

### Phase 4 — FastAPI REST 서버 (`src/api/`)

| 엔드포인트 | 설명 |
|-----------|------|
| `GET /simulation/status` | 현재 틱·연도·계절 |
| `POST /simulation/tick` | 1틱 진행 |
| `POST /simulation/run?ticks=N` | N틱 자동 실행 |
| `GET /world` | 전체 세계 스냅샷 |
| `GET /world/races` | 종족 목록/정렬 |
| `GET /world/diplomacy` | 외교 관계 필터 |
| `GET /world/leaderboard` | 4개 항목 순위표 |
| `GET /factions` | 파벌 전체 목록 |
| `POST /factions/{id}/transcendent` | 초월자 이벤트 발생 |

서버 실행: `cd apps/worldai && py -m uvicorn src.api.main:app --port 8000 --reload`

### Phase 4.5 — 밸런스 수정

| 버그 | 수정 내용 |
|------|---------|
| BLOOD_PACT 반복 발화 | 임계값 이벤트에 60틱 쿨다운 + BOND 이상 positive delta 80% 감쇠 |
| 인구 hard cap (성장 0) | soft cap (1.02x 여유) + 영역 확장 이벤트 (85%+) + 기근(95%+) |
| 전쟁 피해 없음 | `event_system.py`에서 습격 → 패자 인구 감소, 외교 하락, 원한 추적 |

---

## 🔜 Phase 5 — 다음 작업 (웹 대시보드)

### 목표
실시간으로 시뮬레이션 상태를 시각화하는 웹 인터페이스.

### 계획
- WebSocket으로 틱마다 자동 갱신
- 100x80 맵에 종족 영역 시각화
- 외교 관계 그래프 (네트워크 다이어그램)
- 이벤트 피드 (실시간 스크롤)
- 인구·기술·군사력 차트

---

## 📋 향후 백로그 (Future Backlog)

> 지금 당장 구현하지 않지만 설계에 반영해야 할 항목들.

### [HIGH] 영토 기반 인구 계산 시스템
```
현재: 종족 전체 인구를 단일 숫자로 관리
목표: 각 마을(파벌)에 실제 인구가 분산되어 존재
      마을 인구가 늘면 이웃 마을로 이주 이벤트 발생
      전투는 해당 타일의 주둔 병력만 계산
      영토 타일 점령/해방에 따라 인구가 재배치됨

구현 시 변경 필요:
  - RaceState.population → 각 Faction.population의 합계로 계산
  - EventSystem 습격 → Faction 단위 전투로 전환
  - 이동 이벤트: Faction A → Faction B 인구 이전 (교역, 피난, 이주)
  - 타일 맵과 Faction 위치(x, y) 연동
```

### [MEDIUM] 세계 지도 타일 시스템
- 100×80 격자에 지형 타입, 파벌 점령 상태 저장
- Faction.territory_tiles → 실제 타일 좌표 목록으로 전환
- 인접 타일 계산 (전투 발생 조건)

### [MEDIUM] 역사 기록 시스템
- 주요 이벤트를 연도별 연대기로 저장
- "Year 3 봄 — 인간 제국이 언데드와 전쟁 시작"
- API: `GET /world/history?year=3`

### [LOW] 저장/불러오기 시스템
- 시뮬레이션 상태를 JSON으로 직렬화
- `POST /simulation/save` / `POST /simulation/load`

### [LOW] 몬스터 종족 시스템
- 오크/고블린과 별개로 "야생 몬스터" 집단 관리
- 마을 공격 이벤트의 몬스터를 실제 엔티티로 표현

---

## 📝 메모 (AI 간 커뮤니케이션)

```
[Antigravity → 다음 작업자]
Phase 4까지 모두 완료. 서버 정상 동작 확인.

핵심 아키텍처:
  - World (world.py) = 메인 틱 루프
  - DiplomacySystem (diplomacy.py) = 비대칭 친밀도
  - RaceAgent (race_agent.py) = 종족 행동 AI
  - EventSystem (event_system.py) = 랜덤 세계 이벤트
  - FactionManager (faction_manager.py) = 파벌 관리
  - FastAPI (src/api/) = REST 서버

설계 결정 사항:
  - 외교 임계값 이벤트: 60틱 쿨다운 (반복 발화 방지)
  - BOND(80+) 이상에서 positive delta 80% 감쇠 (포화 방지)
  - 인구 soft cap: max_population * 1.02까지 허용, 이후 이벤트 처리
  - 파벌 소속: colony(직할) / vassal(봉신) / independent(자연 발생)
  - 초월자: TranscendentInfo로 레벨 상한 확장, 특성 추가

다음 작업: Phase 5 웹 대시보드
  WebSocket + Canvas/D3.js로 실시간 세계 지도 시각화
```

---

## 🗂️ 문서 인덱스

| 문서 | 내용 |
|------|------|
| `docs/world_design.md` | 대륙 7개 권역, 지역별 다중 파벌 공존 |
| `docs/race_specs.md` | 11개 종족 상세 스펙 |
| `docs/faction_system.md` | 파벌 소속/규모 체계 |
| `docs/religion_system.md` | 교단 시스템 |
| `docs/rank_level_system.md` | 등급/레벨/직위 3축 |
| `docs/transcendent_system.md` | 초월자 시스템 |
