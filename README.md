# WorldAI 🌍

> **판타지 세계관 AI 시뮬레이션 시스템** — 오픈소스 범용 세계관 엔진

[![CI](https://github.com/your-org/WorldAI/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/WorldAI/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)

---

## 🎯 What is WorldAI?

WorldAI는 판타지 세계에서 여러 종족이 자율적으로 행동하는 **AI 시뮬레이션 시스템**이다.

스타듀밸리처럼 NPC들이 알아서 움직이듯, WorldAI의 종족들은 시간이 흐르면서:
- ⚔️ **전쟁**을 선포하거나
- 🤝 **동맹**을 맺거나
- 📈 **성장·쇠퇴**하며
- 🌐 **복잡한 외교 관계**를 형성한다

이 시스템은 **어떤 게임 엔진에도 종속되지 않는 독립 시스템**으로,  
REST API를 통해 Unity, Unreal, NuNuEngine, C++ 등 어디서든 플러그인처럼 연동할 수 있다.

---

## ✨ Features

- 🧬 **데이터 주도 설계**: YAML 파일로 종족·세계관 자유롭게 정의
- 🤝 **외교 시스템**: -100 ~ +100 친밀도 수치로 동적 관계 관리
- 🎲 **이벤트 시스템**: 전쟁, 동맹, 재해, 교역 등 자동 이벤트 발생
- 🔌 **플러그인 구조**: REST API로 Unity/C++ 등 외부 엔진 연동
- 📊 **웹 대시보드**: 실시간 세계 현황 시각화
- 🗺️ **그리드 맵**: 100x80 격자 기반 지형 및 영토 시뮬레이션
- 🔄 **CI/CD**: GitHub Actions 자동 테스트·배포

---

## 🏰 종족 목록 (13종족)

| 카테고리 | 종족 |
|---------|------|
| 인간형 | 인간, 엘프, 드워프, 오크/고블린/트롤, 하플링 |
| 수인/비인간 | 수인(견족·묘족), 반인반수(켄타우로스·하피·라미아), 페어리 |
| 고위/신화 | 드래곤, 언데드(뱀파이어·리치·좀비), 천사/악마 |
| 기타 | 정령(4원소), 골렘/기계종족 |

---

## 🚀 Quick Start

```bash
# 1. 클론
git clone https://github.com/your-org/WorldAI.git
cd WorldAI/apps/worldai

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 시뮬레이션 실행
python -m src.core.world

# 4. API 서버 실행
uvicorn src.api.main:app --reload

# 5. 대시보드 실행 (별도 터미널)
cd dashboard && npm install && npm run dev
```

---

## 🔌 외부 엔진 연동 (Plugin)

```csharp
// Unity에서 WorldAI 사용 예시
var client = new WorldAIClient("http://localhost:8000");
var worldState = await client.GetWorldStateAsync();
var raceStatus = await client.GetRaceAsync("human");
```

```python
# Python에서 직접 사용
from worldai import World
world = World.from_config("configs/worlds/default_world.yaml")
world.tick()  # 시간 1틱 진행
print(world.get_race("human").population)
```

---

## 📁 구조

```
WorldAI/
├── CLAUDE.md / AGENTS.md    # AI 에이전트 진입점
├── docs/                    # 기획 문서 (세계관, 종족 스펙)
├── harness/                 # 하네스 엔지니어링 구조
└── apps/worldai/
    ├── configs/             # YAML 설정 (종족·세계관)
    ├── src/                 # Python 소스
    │   ├── core/            # 시뮬레이션 엔진
    │   ├── api/             # FastAPI REST 서버
    │   └── sdk/             # 플러그인 SDK
    ├── dashboard/           # TypeScript 웹 대시보드
    └── tests/               # 테스트
```

---

## 🗺️ Roadmap

- [x] Phase 0: 하네스 골격 구축
- [x] Phase 1: 기획 문서 작성
- [x] Phase 2: YAML 종족 데이터 (13개 종족)
- [x] Phase 3: 시뮬레이션 코어 (World/RaceAgent)
- [x] Phase 4: FastAPI REST 서버
- [x] Phase 4.6: 시간 시스템 (낮/밤 사이클)
- [x] Phase 4.7: 영토 기반 인구 & 그리드 맵
- [ ] Phase 5: 웹 대시보드 (React/TS 시각화)
- [ ] Phase 6: CI/CD 구축
- [ ] Phase 7: Plugin SDK (Python, C#)

---

## 📄 License

[MIT License](LICENSE) — 자유롭게 사용, 수정, 배포 가능
