# WorldAI — 앱 문서 진입점

## 이 파일의 목적
`apps/worldai/` 앱의 문서 진입점이다.
작업 시작 전 이 파일을 읽고 현재 상태를 파악한다.

## 앱 구조

```
apps/worldai/
├── configs/          # YAML 설정 (사용자 커스터마이징 가능)
│   ├── worlds/       # 세계관 설정
│   └── races/        # 종족 데이터 (13종족)
├── src/              # Python 소스코드
│   ├── core/         # 시뮬레이션 코어
│   ├── config/       # YAML 로더
│   ├── api/          # FastAPI REST 서버
│   └── sdk/          # 플러그인 SDK
├── dashboard/        # TypeScript 웹 대시보드
└── tests/            # pytest 테스트
```

## 현재 Phase 상태
→ `harness/plans/tracker.md` 참조

## 빠른 실행

```powershell
# 시뮬레이션 코어 직접 실행
cd apps/worldai
python -m src.core.world

# API 서버 실행
uvicorn src.api.main:app --reload --port 8000

# 웹 대시보드 실행
cd dashboard && npm run dev

# 테스트 실행
python -m pytest tests/ -v
```

## 주요 설정 파일

| 파일 | 설명 |
|------|------|
| `configs/worlds/default_world.yaml` | 기본 세계관 설정 |
| `configs/races/humanoids/*.yaml` | 인간형 종족 5종 |
| `configs/races/beastmen/*.yaml` | 수인/비인간 종족 3종 |
| `configs/races/mythic/*.yaml` | 고위/신화 종족 3종 |
| `configs/races/others/*.yaml` | 기타 종족 2종 |

## 외교 시스템 핵심

```
친밀도: -100 ~ +100

 -100  -60  -30   0   30   60  100
  전쟁  적대  냉전  중립  우호  동맹  혈맹

규칙:
- A→B 수치와 B→A 수치는 독립적으로 관리
- 비우호적이어도 이벤트로 전환 가능
- 임계값 돌파 시 자동 이벤트 발생
```
