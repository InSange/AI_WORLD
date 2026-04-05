# WorldAI — 시스템 아키텍처 설계 (System Design)

> 최종 수정: 2026-04-05 | 상태: Draft

---

## 1. 전체 아키텍처

```
┌────────────────────────────────────────────────────────────┐
│                    WorldAI System                          │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Python Core (시뮬레이션 엔진)             │  │
│  │                                                      │  │
│  │  WorldEngine                                         │  │
│  │   ├── TimeSystem       (틱/계절/연도 관리)           │  │
│  │   ├── RaceAgent        (종족 행동 AI)                │  │
│  │   ├── DiplomacySystem  (친밀도 -100~+100)            │  │
│  │   ├── EventSystem      (이벤트 발생/처리)             │  │
│  │   ├── CombatSystem     (전투 계산)                   │  │
│  │   └── StateManager     (저장/로드)                   │  │
│  │                                                      │  │
│  │  ConfigLoader                                        │  │
│  │   ├── WorldLoader      (worlds/*.yaml)               │  │
│  │   └── RaceLoader       (races/**/*.yaml)             │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕ REST API (FastAPI)               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Layer (FastAPI)                     │  │
│  │   GET  /world/state         현재 세계 전체 상태       │  │
│  │   POST /world/tick          1틱 진행                 │  │
│  │   POST /world/tick/{n}      N틱 진행                 │  │
│  │   GET  /races               전체 종족 목록           │  │
│  │   GET  /races/{id}          특정 종족 상태           │  │
│  │   GET  /diplomacy           전체 외교 관계           │  │
│  │   GET  /events              최근 이벤트 로그         │  │
│  │   POST /world/reset         시뮬레이션 리셋          │  │
│  └──────────────────────────────────────────────────────┘  │
│         ↕ WebSocket (실시간)          ↕ HTTP               │
│  ┌────────────────┐        ┌───────────────────────────┐   │
│  │ Web Dashboard  │        │     Plugin SDK            │   │
│  │ (React + TS)   │        │  Python / REST / C#(Unity)│   │
│  └────────────────┘        └───────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

---

## 2. 시뮬레이션 루프 (Tick Loop)

```python
def tick(world: World) -> TickResult:
    """시뮬레이션 1틱 처리"""

    # 1. 시간 진행
    time_system.advance(world)           # 틱 +1, 계절 체크

    # 2. 자원 생산
    for race in world.active_races:
        resource_system.produce(race)    # 지형 기반 자원 생산

    # 3. 인구 변화
    for race in world.active_races:
        race_agent.update_population(race)

    # 4. 외교 수치 자연 감쇠
    diplomacy_system.decay_all(world)    # 모든 관계를 중립으로 조금 수렴

    # 5. 종족 행동 결정 (AI)
    for race in world.active_races:
        action = race_agent.decide_action(race, world)
        # IDLE / TRADE / EXPAND / ATTACK / NEGOTIATE / RESEARCH

    # 6. 행동 실행 + 외교 수치 변화
    for action in pending_actions:
        action_system.execute(action, world)

    # 7. 이벤트 체크 (임계값, 랜덤)
    events = event_system.check_and_fire(world)

    # 8. 전투 처리
    for war in world.active_wars:
        combat_system.resolve_battle(war, world)

    # 9. 상태 스냅샷 저장
    state_manager.snapshot(world)

    return TickResult(events=events, world_state=world.to_dict())
```

---

## 3. 모듈 상세 설계

### 3.1 WorldEngine (`src/core/world.py`)

```python
@dataclass
class World:
    id: str
    name: str
    tick: int = 0
    season: str = "spring"
    year: int = 1
    races: dict[str, Race] = field(default_factory=dict)
    relations: dict[tuple, float] = field(default_factory=dict)
    active_events: list[Event] = field(default_factory=list)
    event_log: list[EventLog] = field(default_factory=list)

    @classmethod
    def from_config(cls, config_path: str) -> "World":
        """YAML 설정으로부터 월드 생성"""
        ...

    def tick(self) -> TickResult:
        """1틱 진행"""
        ...

    def get_relation(self, from_id: str, to_id: str) -> float:
        """종족 간 친밀도 조회 (기본값 0)"""
        return self.relations.get((from_id, to_id), 0.0)
```

### 3.2 RaceAgent (`src/core/race_agent.py`)

```python
class RaceAgent:
    """종족의 자율 행동 AI"""

    def decide_action(self, race: Race, world: World) -> Action:
        """종족의 현재 상태와 세계 상황에 따라 행동 결정"""
        if self._is_under_threat(race, world):
            return self._defensive_action(race, world)
        if self._has_expansion_opportunity(race, world):
            return self._expansion_action(race, world)
        if self._has_trade_opportunity(race, world):
            return self._trade_action(race, world)
        return IdleAction(race_id=race.id)

    def _is_under_threat(self, race: Race, world: World) -> bool:
        """적대적 세력이 주변에 있는지 확인"""
        ...
```

### 3.3 DiplomacySystem (`src/core/diplomacy.py`)

```python
class DiplomacySystem:
    LEVELS = {
        (-100, -61): "WAR",
        (-60, -31): "HOSTILE",
        (-30, -11): "COLD",
        (-10, +19): "NEUTRAL",
        (+20, +49): "FRIEND",
        (+50, +79): "ALLIED",
        (+80, +100): "BOND",
    }

    def adjust_affinity(
        self,
        world: World,
        from_id: str,
        to_id: str,
        delta: float,
        reason: str
    ) -> AffinityChangeResult:
        """친밀도 조정 + 임계값 이벤트 체크"""
        prev = world.get_relation(from_id, to_id)
        new_val = max(-100, min(100, prev + delta))
        world.set_relation(from_id, to_id, new_val)

        # 임계값 통과 여부 확인
        threshold_event = self._check_threshold(prev, new_val, from_id, to_id)
        return AffinityChangeResult(old=prev, new=new_val, event=threshold_event)
```

### 3.4 EventSystem (`src/core/event_system.py`)

```python
@dataclass
class Event:
    id: str
    name: str
    description: str
    trigger: EventTrigger      # THRESHOLD / RANDOM / SCHEDULED
    effects: list[EventEffect]

class EventSystem:
    def check_and_fire(self, world: World) -> list[FiredEvent]:
        """이벤트 발생 여부 체크 및 실행"""
        fired = []
        # 랜덤 이벤트
        fired += self._check_random_events(world)
        # 계절 이벤트
        fired += self._check_season_events(world)
        # 임계값 이벤트 (외교 변화에 의해 이미 발생됨)
        return fired
```

---

## 4. API 설계 (FastAPI)

### 응답 형식 (JSON)

```json
// GET /world/state
{
  "tick": 450,
  "year": 1,
  "season": "autumn",
  "races": {
    "human": {
      "population": 2840,
      "territory_count": 12,
      "military_strength": 65,
      "resources": { "food": 1200, "iron": 340 }
    },
    "elf": {
      "population": 780,
      "territory_count": 8,
      "military_strength": 72,
      "resources": { "food": 900, "magic_stone": 200 }
    }
  },
  "diplomacy": {
    "human→elf": { "affinity": 28, "level": "FRIEND" },
    "elf→orc": { "affinity": -55, "level": "HOSTILE" }
  },
  "recent_events": [
    {
      "tick": 448,
      "type": "TRADE",
      "description": "인간과 드워프 교역 협정 체결",
      "affected": ["human", "dwarf"],
      "affinity_change": { "human→dwarf": +5, "dwarf→human": +3 }
    }
  ]
}
```

---

## 5. Plugin SDK 인터페이스

### Python SDK

```python
from worldai.sdk import WorldAIClient

client = WorldAIClient(base_url="http://localhost:8000")

# 1틱 진행
result = client.tick()

# 종족 상태 조회
human = client.get_race("human")
print(f"인간 인구: {human.population}")

# 외교 관계 조회
diplomacy = client.get_diplomacy("human", "elf")
print(f"인간↔엘프 친밀도: {diplomacy.affinity} ({diplomacy.level})")
```

### C# SDK (Unity용 스텁)

```csharp
// WorldAI/apps/worldai/src/sdk/csharp/WorldAIClient.cs
public class WorldAIClient {
    private string baseUrl;

    public WorldAIClient(string baseUrl) {
        this.baseUrl = baseUrl;
    }

    public async Task<WorldState> GetWorldStateAsync() { ... }
    public async Task<TickResult> TickAsync() { ... }
    public async Task<Race> GetRaceAsync(string raceId) { ... }
    public async Task<DiplomacyInfo> GetDiplomacyAsync(string from, string to) { ... }
}
```

---

## 6. CI/CD 파이프라인

```yaml
# .github/workflows/ci.yml
on: [push, pull_request]

jobs:
  test:
    steps:
      - ruff check .              # 린트
      - mypy src/                 # 타입 체크
      - pytest tests/ --cov=src   # 테스트 + 커버리지
      - npm run build (dashboard) # 대시보드 빌드

  # cd.yml (main 브랜치만)
  deploy:
    steps:
      - docker build .
      - github pages deploy (dashboard)
```
