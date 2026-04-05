# WorldAI — Checkpoint Script
# 큰 변경 전 git 체크포인트를 생성한다

param(
    [string]$Message = "checkpoint"
)

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$tag = "checkpoint/$timestamp"
$commitMsg = "🔖 CHECKPOINT: $Message [$timestamp]"

Write-Host "📸 체크포인트 생성 중..." -ForegroundColor Cyan
Write-Host "  메시지: $commitMsg" -ForegroundColor Gray

# 현재 변경사항 임시 저장
git add -A
git stash push -m $commitMsg

# 스태시를 다시 적용 (변경사항 유지하면서 기록만)
git stash pop

# 현재 HEAD를 태그로 표시
git tag $tag
Write-Host "✅ 체크포인트 생성 완료: $tag" -ForegroundColor Green
Write-Host "   롤백하려면: .\harness\scripts\rollback.ps1 $tag" -ForegroundColor Yellow
