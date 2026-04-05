# WorldAI — Agent 작업 가이드

## Purpose
이 문서는 Antigravity, Codex 등 AI 에이전트가 이 저장소에서 작업을 시작할 때 읽는 루트 진입점이다.

## Read Order
1. `harness/core/docs/index.md` — 전역 규칙 인덱스
2. `harness/core/workflows/pipeline.md` — 작업 파이프라인
3. `apps/worldai/harness/docs/index.md` — 앱 문서 진입점
4. `apps/worldai/harness/plans/tracker.md` — 현재 Phase 상태

## Current App
- 기본 작업 대상: `apps/worldai/`

## Working Rules
- repository-level 규칙은 `harness/core/`를 따른다
- app-level 규칙은 `apps/worldai/harness/`를 따른다
- 상태 변경이 있으면 `tracker.md`를 갱신한다
- handoff 전에는 `harness/scripts/cleanup.ps1`을 실행한다
- 큰 변경 전에는 `harness/scripts/checkpoint.ps1`으로 git checkpoint를 만든다
- 한 번에 최대 3개 파일만 수정한다

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
