# WorldAI App — 실행 안내

## 개발 환경 설정

### 필수 요구사항
- Python 3.11+
- Node.js 18+
- pip 또는 uv

### 1. Python 환경 설정

```powershell
cd apps/worldai

# 가상 환경 생성
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 의존성 설치
pip install -r requirements.txt
```

### 2. 시뮬레이션 코어 실행 (Phase 3 이후)

```powershell
# 기본 시뮬레이션 실행
python -m src.core.world

# 특정 세계관으로 실행
python -m src.core.world --config configs/worlds/default_world.yaml
```

### 3. API 서버 실행 (Phase 4 이후)

```powershell
uvicorn src.api.main:app --reload --port 8000
# 접속: http://localhost:8000
# 문서: http://localhost:8000/docs
```

### 4. 웹 대시보드 실행 (Phase 5 이후)

```powershell
cd dashboard
npm install
npm run dev
# 접속: http://localhost:5173
```

### 5. 테스트 실행

```powershell
python -m pytest tests/ -v --cov=src
```

---

## 커스터마이징

### 새 종족 추가

```yaml
# configs/races/my_category/my_race.yaml 생성
id: my_race
name: 나의 종족
category: humanoid
stats:
  max_population: 5000
  growth_rate: 1.03
  military_strength: 50
  magic_affinity: 70
  technology_level: 30
  adaptability: 60
diplomacy_defaults:
  - target: human
    affinity: 20
behavior:
  aggression: 0.4
  expansion_drive: 0.5
  alliance_tendency: 0.7
```

파일을 저장하면 자동으로 시스템이 인식한다.

### 새 세계관 만들기

```yaml
# configs/worlds/my_world.yaml 생성
id: my_world
name: 나의 세계
description: "나만의 판타지 세계관"
map:
  width: 100
  height: 80
time:
  ticks_per_season: 90
  seasons: [spring, summer, autumn, winter]
starting_races:
  - id: human
    territory: [10, 10]
    population: 1000
  - id: elf
    territory: [80, 60]
    population: 500
```

---

## 현재 상태
→ `harness/plans/tracker.md` 참조
