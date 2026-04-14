# WorldAI — 작업 파이프라인 (Pipeline)

## 모든 작업은 이 파이프라인을 따른다

```
요청(Request) → 플랜(Plan) → 구현(Implement) → 검증(Verify) → 커밋(Commit) → 반복
```

---

## Step 1: 요청 (Request)

사용자 또는 다른 AI가 작업을 요청한다.

```
좋은 요청 형식:
  목표: [원하는 결과]
  제약: [건드리면 안 되는 것]
  참고: [관련 파일 또는 문서]
```

---

## Step 2: 플랜 (Plan)

작업 시작 전 반드시 계획을 수립한다.

- `tracker.md` 업데이트
- 수정할 파일 목록 확인 (최대 3개)
- 사용자 승인 후 구현 시작

```
❌ 승인 없이 바로 구현 금지
✅ 플랜 제시 → 승인 → 구현
```

---

## Step 3: 구현 (Implement)

- 한 번에 최대 **3개 파일**만 수정
- 큰 변경 전 checkpoint 생성:
  ```powershell
  .\harness\scripts\checkpoint.ps1 "구현 시작 전"
  ```
- `tracker.md` 진행 상황 업데이트

---

## Step 4: 검증 (Verify)

### Python 코어
```powershell
cd apps/worldai
python -m pytest tests/ -v
```

### API 서버
```powershell
uvicorn src.api.main:app --reload
curl http://localhost:8000/health
```

### 대시보드
```powershell
cd dashboard
npm run build
```

### 체크리스트
- [ ] 구문 오류 없음
- [ ] 테스트 통과
- [ ] YAML 로더 정상 작동
- [ ] API 응답 정상

---

## Step 5: 커밋 (Commit)

검증 통과 후 커밋 메시지는 공통된 규칙에 따라 다음과 같이 자동 제안:

```
#[이슈번호/넘버링] Phase X: 작업내용 요약 (한글)

- 이전 커밋의 넘버링에서 +1 하여 작성 (`git log --oneline -n 5` 참고)
```

---

## Step 6: tracker.md 갱신

```markdown
## 현재 Phase: Phase X
### 완료한 작업
- [x] 작업명
### 다음 작업
- [ ] 다음 작업명
```

---

## 긴급 롤백

```powershell
# 문제 발생 시
.\harness\scripts\rollback.ps1
```
