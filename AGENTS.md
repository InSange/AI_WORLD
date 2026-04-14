# WorldAI — Agent 작업 가이드

## Purpose
이 문서는 Antigravity, Codex 등 AI 에이전트가 이 저장소에서 작업을 시작할 때 읽는 루트 진입점이다.

## Read Order
1. `harness/core/docs/index.md` — 전역 규칙 인덱스
2. `harness/core/workflows/pipeline.md` — 작업 파이프라인
3. `apps/worldai/harness/docs/index.md` — 앱 문서 진입점
4. `apps/worldai/harness/plans/tracker.md` — 현재 Phase 상태 (Phase 7 완료)
5. `docs/roadmap.md` — 전체 마일스톤 및 다음 Phase 상세 계획

## Documentation Map
타 모델이 프로젝트를 파악할 때 다음 문서들을 순서대로 참고하시오:
- [AGENTS.md](file:///c:/Users/선우/source/repos/WorldAI/AGENTS.md): 에이전트 작업 가이드 및 진입점
- [CLAUDE.md](file:///c:/Users/선우/source/repos/WorldAI/CLAUDE.md): 아키텍처 원칙 및 헌법
- [apps/worldai/harness/plans/tracker.md](file:///c:/Users/선우/source/repos/WorldAI/apps/worldai/harness/plans/tracker.md): 시뮬레이션 개발 단계 및 상태 트래커
- [apps/worldai/harness/plans/phase_5_dashboard.md](file:///c:/Users/선우/source/repos/WorldAI/apps/worldai/harness/plans/phase_5_dashboard.md): Phase 5 완수 상세 보고 및 40,000 타일(200x200) 명세
- [docs/](file:///c:/Users/선우/source/repos/WorldAI/docs/): 기획 및 기술 명세서 모음 (인구, 외교, 종교 등)
- [docs/milestones/](file:///c:/Users/선우/source/repos/WorldAI/docs/milestones/): 완료된 주요 단계별 상세 리포트

## Current App
- 기본 작업 대상: `apps/worldai/`

## Working Rules
- repository-level 규칙은 `harness/core/`를 따른다
- app-level 규칙은 `apps/worldai/harness/`를 따른다
- 상태 변경이 있으면 `tracker.md`를 갱신한다
- handoff 전에는 `harness/scripts/cleanup.ps1`을 실행한다
- 큰 변경 전에는 `harness/scripts/checkpoint.ps1`으로 git checkpoint를 만든다
- 한 번에 최대 3개 파일만 수정한다

## Git Commit Rules
모든 AI 에이전트는 커밋 시 아래의 형식을 반드시 준수하여 깃 히스토리를 통일한다.
- **포맷**: `#[넘버링] Phase X: 작업내용 요약 (한글)`
- **예시**: `#18 Phase 6: CI/CD Pipeline 및 정적 분석 린트 에러 수정`
- 커밋 전 `git log --oneline -n 5`를 통해 최근 넘버링(예: #17)을 확인하고 **+1 증가**시켜서 적용한다.
- 영어보다는 한글로 직관적으로 작성하며, 핵심 작업 내역을 명확히 기재한다.

## Current Entry
- `apps/worldai/README.md` — 사람 기준 실행 안내
- `apps/worldai/harness/docs/index.md` — 앱 문서 진입점
- `apps/worldai/harness/plans/tracker.md` — 현재 Phase 상태

## Project Overview
WorldAI는 판타지 세계관 AI 시뮬레이션 시스템이다.
- **Python 코어**: 시뮬레이션 엔진 + FastAPI REST 서버
- **TypeScript 대시보드**: 실시간 세계 현황 시각화
- **YAML 설정**: 종족·세계관을 코드 없이 커스터마이징
- **플러그인 구조**: REST API로 Unity/C++ 등 외부 엔진 연동
- **독립 실행**: 특정 게임 엔진에 종속되지 않음
