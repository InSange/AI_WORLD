# WorldAI — AI 협업 규칙 (Collab Rules)

## 이 문서의 목적
Claude와 Antigravity가 동일한 레포지토리에서 충돌 없이 협업하기 위한 규칙이다.

---

## 1. 역할 분담

| AI | 주 역할 | 보조 역할 |
|----|---------|---------|
| **Antigravity** | 구현 실행, 파일 생성, 명령어 실행 | 기획 검토 |
| **Claude** | 아키텍처 설계, 코드 리뷰, 기획 자문 | 간단한 파일 수정 |

---

## 2. 핸드오프 (Handoff) 프로토콜

### AI 작업 전 (Before)
1. `apps/worldai/harness/plans/tracker.md` 읽기
2. 현재 Phase 및 진행 상태 확인
3. 작업 범위 결정 (최대 3개 파일)

### AI 작업 후 (After)
1. `tracker.md` Phase 상태 업데이트
2. 변경 파일 목록 기록
3. 다음 AI를 위한 메모 남기기 (tracker.md "Next" 섹션)

### 핸드오프 전 정리
```powershell
# 반드시 실행
.\harness\scripts\cleanup.ps1
```

---

## 3. 상태 동기화 규칙

```
tracker.md = 현재 세계의 진실(Source of Truth)

- Phase 변경 시 반드시 tracker.md 먼저 갱신
- 작업 중 파일 목록 기록
- 완료/미완료 명확히 표시
```

---

## 4. 충돌 방지 규칙

- 같은 파일을 두 AI가 동시에 수정하지 않는다
- 큰 구조 변경 전 반드시 checkpoint 생성:
  ```powershell
  .\harness\scripts\checkpoint.ps1 "변경 전 체크포인트"
  ```
- 문제 발생 시 rollback:
  ```powershell
  .\harness\scripts\rollback.ps1
  ```

---

## 5. 문서 우선순위

```
tracker.md > implementation_plan.md > constitution.md > 코드 주석
```

최신 상태는 항상 tracker.md를 기준으로 한다.
