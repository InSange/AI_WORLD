# WorldAI — 코딩 헌법 (Constitution)

> 이 문서는 모든 기여자(사람 + AI)가 반드시 따라야 할 규칙이다.

---

## 1. 언어 & 버전

| 영역 | 언어 | 버전 |
|------|------|------|
| 시뮬레이션 코어 | Python | 3.11+ |
| API 서버 | Python (FastAPI) | 3.11+ |
| 웹 대시보드 | TypeScript | 5.0+ |
| 설정 파일 | YAML | - |

---

## 2. Python 코드 규칙

| 규칙 | 내용 | 이유 |
|------|------|------|
| 타입 힌트 | 모든 함수에 타입 힌트 필수 | 런타임 오류 조기 탐지 |
| 데이터 클래스 | `@dataclass` 또는 `pydantic.BaseModel` 사용 | 구조화된 데이터 관리 |
| 절대 import | `from worldai.core import ...` | 상대 import 혼란 방지 |
| 파일 크기 | 단일 파일 300줄 이하 유지 | 가독성 |
| 명명 규칙 | snake_case (Python 표준) | PEP8 준수 |
| 상수 | UPPER_SNAKE_CASE | 상수임을 명확히 표시 |

---

## 3. 설계 원칙

### 데이터 주도 (Data-Driven)
```
✅ 올바른 방법
# configs/races/human.yaml 에 정의, 코드에서 로드
race = yaml.safe_load(open("configs/races/human.yaml"))

❌ 금지
# Python 코드에 직접 하드코딩
HUMAN_STATS = {"population": 1000, "strength": 60}
```

### 범용 플러그인 구조
```
외부 엔진 → HTTP REST API → WorldAI 코어
(Unity, C++ 등)  (JSON 응답)      (Python)

절대로 특정 게임 엔진의 API를 직접 import 하지 않는다.
```

### 단일 책임 원칙
```
world.py        → 시간(틱/계절)만 관리
race_agent.py   → 종족 행동만 관리
diplomacy.py    → 외교 수치만 관리
event_system.py → 이벤트 발생만 관리
```

---

## 4. 금지 사항

- ❌ 요청하지 않은 리팩토링
- ❌ 종족 데이터를 Python 코드에 하드코딩
- ❌ 특정 게임 엔진 SDK를 코어에 import
- ❌ 한 번에 3개 초과 파일 수정
- ❌ 작업 범위 외 파일 수정
- ❌ tracker.md 갱신 없이 Phase 전환

---

## 5. 테스트 규칙

```python
# 새 기능 추가 시 반드시 테스트 파일도 함께 작성
# apps/worldai/tests/test_core/test_diplomacy.py
def test_affinity_changes_on_war_event():
    ...

def test_cold_war_can_become_friendly():
    ...
```

- 테스트 프레임워크: `pytest`
- 커버리지 목표: 코어 시스템 80% 이상

---

## 6. 커밋 규칙

```
#이슈번호 작업내용 요약 (한 줄)

- 변경된 핵심 내용 1
- 변경된 핵심 내용 2
```

예시:
```
#12 드워프 종족 YAML 및 config loader 추가

- configs/races/humanoids/dwarf.yaml 생성
- race_loader.py에 드워프 로드 로직 추가
```
