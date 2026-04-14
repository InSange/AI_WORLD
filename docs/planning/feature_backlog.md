# WorldAI — Post v1.0 기능 백로그

> 작성일: 2026-04-15 | 관리자: 전체 AI 에이전트 공동 갱신  
> 참고 분석: `docs/planning/worldbox_reference.md`  
> **이 파일의 역할**: v1.0 이후 추가할 기능의 우선순위 관리. 구현 시작 전 tracker.md로 이동.

---

## 우선순위 기준

| 레벨 | 기준 |
|------|------|
| 🔴 HIGH | 시뮬레이션 핵심 게임성에 직접 영향. WorldBox 대비 명확한 갭 |
| 🟡 MEDIUM | 깊이를 더하지만 없어도 동작함 |
| 🟢 LOW | 비주얼/QoL 개선. 나중에 해도 무방 |

---

## 🔴 HIGH — 핵심 게임성 갭

### 1. 세계 시대 (World Ages) 시스템
- **참고**: WorldBox Ages 시스템
- **내용**: 일정 틱/조건 도달 시 세계가 시대 전환 (선사 → 고대 → 중세 → 근대)
- **효과**: 시대별 이벤트 발생, 기술 언락, 바이옴 변화
- **연관 파일**: `src/core/world.py`, `configs/worlds/default_world.yaml`
- **설계 결정 필요**:
  - 시대 전환 조건 (연도 기반? 기술 수준 기반?)
  - 시대별 해금 종족/이벤트 목록
- **예상 난이도**: 중간

---

### 2. 반란 / 독립 이벤트
- **참고**: WorldBox 반란 시스템
- **내용**: 종속 파벌 불만 누적 → 독립 반란 → 새 파벌 생성
- **효과**: 제국이 약해지면 자연스럽게 분열, 소규모 파벌 증가
- **연관 파일**: `src/core/faction_manager.py`, `src/core/event_system.py`
- **설계 결정 필요**:
  - 불만 수치 계산 방식 (자원 부족, 전쟁 패배, 식량 부족)
  - 반란 성공/실패 확률
- **예상 난이도**: 낮음

---

### 3. 바이옴별 자원 생산 시스템
- **참고**: WorldBox 지형별 자원
- **내용**: 각 타일 바이옴이 실제 자원 생산에 영향
  - 초원 → 식량 +, 평원 → 농업
  - 산악 → 철/금 +
  - 숲 → 목재 +
  - 사막 → 마정석 +
- **효과**: 영토 확장 동기 부여, 자원 전쟁 발생
- **연관 파일**: `src/core/map.py`, `src/core/faction_manager.py`
- **설계 결정 필요**:
  - 자원 타입 정의 (food, iron, wood, magic_stone 등)
  - 파벌별 자원 수치 관리 방식
- **예상 난이도**: 중간

---

### 4. 플레이어 신(God) 개입 API
- **참고**: WorldBox의 핵심 정체성 — 플레이어가 신
- **내용**: 플레이어가 REST API를 통해 세계에 직접 개입
  ```
  POST /god/spawn         - 유닛/종족 소환
  POST /god/disaster      - 재앙 발생 (지진/역병/번개)
  POST /god/bless         - 특정 파벌 축복 (자원/인구 보너스)
  POST /god/curse         - 특정 파벌 저주 (약화/전쟁 유발)
  POST /god/terraform     - 지형 변환 (타일 타입 변경)
  ```
- **효과**: 단순 관찰에서 → 인터랙티브 갓 게임으로 전환
- **연관 파일**: `src/api/main.py`, 새 `src/api/routes/god.py`
- **설계 결정 필요**:
  - 신의 능력 포인트 시스템 (무제한 vs 제한)
  - 개입 후 시뮬레이션 균형 유지 방법
- **예상 난이도**: 낮음 (API만 추가, 코어는 이미 있음)

---

## 🟡 MEDIUM — 깊이 추가

### 5. 영토 기반 인구 분산 (기존 백로그 HIGH)
- **내용**: 파벌 인구를 유동 타입별로 분산 (정착민/상인/군인/모험가/피난민)
- **연관 파일**: `src/core/faction_manager.py`, `src/core/models.py`
- **설계**: `PopulationSegment` 모델 이미 설계됨 (tracker.md 참조)

---

### 6. 트레잇 유전 시스템
- **참고**: WorldBox 유닛 트레잇 전파
- **내용**: 파벌 특성(behavior)이 이벤트/전투 경험으로 변화
  - 전쟁 승리 多 → aggression 증가
  - 교역 多 → trade_focus 증가
  - 기근 생존 → adaptability 증가
- **연관 파일**: `src/core/race_agent.py`, `configs/races/`
- **예상 난이도**: 낮음

---

### 7. 날씨 / 기후 이벤트 확장
- **참고**: WorldBox 날씨 조작
- **내용**: 가뭄, 홍수, 혹한파, 폭풍 등 기후 이벤트 추가
- **효과**: 계절 시스템 + 랜덤 기후 변화 → 식량/이동 패널티
- **연관 파일**: `src/core/event_system.py`, `src/core/world.py`

---

### 8. 항해 / 해상 이동
- **참고**: WorldBox 섬 탐험
- **내용**: WATER 타일을 통한 파벌 간 해상 교역/침공
- **연관 파일**: `src/core/map.py`, `src/core/race_agent.py`

---

### 9. 역사 기록 시스템
- **내용**: 주요 이벤트 자동 연대기 저장
  ```
  GET /world/history?year=3
  GET /world/history/events?type=war
  ```
- **연관 파일**: 새 `src/core/history_manager.py`

---

### 10. LLM 연동 — 종족 지도자 AI 대화
- **내용**: Claude API로 종족 지도자가 실제 대화/협상
  - 외교 협상 대화 생성
  - 전쟁 선포 이유 생성
  - 이벤트 내러티브 자동 생성
- **연관 파일**: 새 `src/core/llm_advisor.py`
- **의존성**: `anthropic` SDK 추가 필요

---

## 🟢 LOW — QoL / 비주얼

### 11. 왕국 배너 / 문장 시스템
- **참고**: WorldBox 커스터마이징
- **내용**: 파벌별 색상·문장 커스터마이징 (대시보드 시각화 강화)

### 12. 저장 / 불러오기
- **내용**: `POST /simulation/save`, `POST /simulation/load`
- **연관 파일**: 새 `src/core/state_manager.py`

### 13. 웹 에디터
- **내용**: 브라우저에서 종족·파벌·세계관 편집 UI

### 14. 화산 / 습지 바이옴 추가
- **내용**: `TileType.VOLCANO`, `TileType.SWAMP` 추가
- **연관 파일**: `src/core/map.py`, 프론트 `TILE_COLORS`

---

## 구현 순서 추천 (타 모델 참고용)

```
1단계 (가장 임팩트 크고 구현 쉬움):
  → 반란/독립 이벤트 (#2)
  → 플레이어 신 개입 API (#4)

2단계 (게임성 핵심):
  → 바이옴별 자원 생산 (#3)
  → 세계 시대 시스템 (#1)

3단계 (깊이):
  → 영토 기반 인구 분산 (#5)
  → 트레잇 유전 (#6)
  → 역사 기록 (#9)

4단계 (확장):
  → LLM 연동 (#10)
  → 날씨 이벤트 (#7)
  → 항해 시스템 (#8)
```

---

## 작업 시 주의사항

- 기능 구현 시작 전 이 파일에서 해당 항목을 **tracker.md의 새 Phase**로 이동
- 한 번에 최대 3개 파일 수정 (CLAUDE.md 헌법 준수)
- 새 Phase 번호는 `git log --oneline -n 5`로 커밋 넘버링 확인 후 결정
