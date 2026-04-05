# WorldAI — Phase 상태 트래커

> **마지막 업데이트**: 2026-04-05
> **현재 Phase**: Phase 0 (완료)

---

## 📊 전체 Progress

| Phase | 이름 | 상태 |
|-------|------|------|
| Phase 0 | 하네스 골격 구축 | ✅ 완료 |
| Phase 1 | 기획 문서 작성 | ⬜ 대기 |
| Phase 2 | YAML 종족 데이터 | ⬜ 대기 |
| Phase 3 | 시뮬레이션 코어 | ⬜ 대기 |
| Phase 4 | FastAPI REST 서버 | ⬜ 대기 |
| Phase 5 | 웹 대시보드 | ⬜ 대기 |
| Phase 6 | CI/CD 구축 | ⬜ 대기 |
| Phase 7 | Plugin SDK | ⬜ 대기 |

---

## ✅ Phase 0 — 완료 내역

### 생성된 파일

**루트 파일**
- [x] `CLAUDE.md` — Claude 진입점
- [x] `AGENTS.md` — Antigravity/Codex 진입점
- [x] `README.md` — GitHub 소개 페이지
- [x] `LICENSE` — MIT 라이선스
- [x] `.gitignore`

**하네스 구조**
- [x] `harness/core/docs/index.md` — 전역 인덱스
- [x] `harness/core/rules/constitution.md` — 코딩 헌법
- [x] `harness/core/rules/collab.md` — AI 협업 규칙
- [x] `harness/core/workflows/pipeline.md` — 작업 파이프라인
- [x] `harness/scripts/checkpoint.ps1`
- [x] `harness/scripts/rollback.ps1`
- [x] `harness/scripts/cleanup.ps1`

**앱 하네스**
- [x] `apps/worldai/harness/docs/index.md`
- [x] `apps/worldai/harness/plans/tracker.md` (이 파일)

---

## 🔜 Phase 1 — 다음 작업 (기획 문서)

### 목표
WorldAI의 세계관·종족·외교·시스템을 문서화한다.
이 문서들이 Phase 2 YAML 데이터의 기반이 된다.

### 작업 목록
- [ ] `docs/world_design.md` — 대륙 구조, 시간 개념, 지형 설정
- [ ] `docs/race_specs.md` — 15종족 상세 스펙 (능력치, 성향, 특성)
- [ ] `docs/diplomacy_design.md` — 외교 시스템 상세 설계
- [ ] `docs/system_design.md` — 시뮬레이션 아키텍처 설계
- [ ] `docs/roadmap.md` — 전체 로드맵

### 예상 산출물
15종족 각각의:
- 기본 스탯 (인구 성장률, 전투력, 마법 친화도, 기술 수준)
- 외교 기본 성향 (어떤 종족과 친하고 적대적인지)
- 특수 능력 또는 특성
- 행동 패턴 (공격적, 방어적, 상업적 등)

---

## 📝 메모 (AI 간 커뮤니케이션)

```
[Antigravity → 다음 작업자]
Phase 0 완료. git init 후 초기 커밋 필요.
Phase 1 시작 시 docs/ 폴더부터 생성할 것.
종족 스펙 작성 시 YAML 변환을 염두에 두고 구조화할 것.
```
