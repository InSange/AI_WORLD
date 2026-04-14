# WorldAI — 전역 문서 인덱스

## 이 파일의 목적
모든 AI 에이전트(Claude, Antigravity, Codex 등)가 작업 시작 전 반드시 읽어야 할 문서 목록이다.

## 읽기 순서

| 순서 | 파일 | 설명 |
|------|------|------|
| 1 | `harness/core/docs/index.md` | 이 파일 — 전역 인덱스 |
| 2 | `harness/core/rules/constitution.md` | 코딩 헌법 (반드시 준수) |
| 3 | `harness/core/rules/collab.md` | AI 간 협업 규칙 |
| 4 | `harness/core/workflows/pipeline.md` | 작업 파이프라인 |
| 5 | `apps/worldai/harness/docs/index.md` | 앱 문서 진입점 |
| 6 | `apps/worldai/harness/plans/tracker.md` | 현재 Phase 상태 (Phase 7 완료) |

## 핵심 원칙 요약

- **데이터 주도**: 종족·세계관은 YAML로, 코드에 하드코딩 금지
- **범용성**: REST API 기반 플러그인 구조, 특정 엔진 종속 금지
- **3파일 규칙**: 한 번에 최대 3개 파일만 수정
- **tracker.md 갱신**: 상태 변경 시 반드시 tracker.md 업데이트

## 관련 문서

| 종류 | 위치 |
|------|------|
| 세계관 기획서 | `docs/world_design.md` |
| 종족 스펙 | `docs/race_specs.md` |
| 외교 시스템 설계 | `docs/diplomacy_design.md` |
| 시스템 아키텍처 | `docs/system_design.md` |
| 로드맵 | `docs/roadmap.md` |
