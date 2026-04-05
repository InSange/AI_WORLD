# WorldAI — Rollback Script
# 이전 체크포인트로 복구한다

param(
    [string]$Tag = ""
)

if ($Tag -eq "") {
    Write-Host "📋 사용 가능한 체크포인트 목록:" -ForegroundColor Cyan
    git tag --list "checkpoint/*" --sort=-creatordate | Select-Object -First 10
    Write-Host ""
    $Tag = Read-Host "롤백할 태그를 입력하세요"
}

Write-Host "⚠️  경고: 현재 변경사항이 모두 사라집니다!" -ForegroundColor Red
$confirm = Read-Host "계속하시겠습니까? (yes/no)"

if ($confirm -ne "yes") {
    Write-Host "❌ 롤백 취소됨" -ForegroundColor Yellow
    exit 0
}

Write-Host "🔄 롤백 중: $Tag" -ForegroundColor Cyan
git checkout $Tag
Write-Host "✅ 롤백 완료" -ForegroundColor Green
