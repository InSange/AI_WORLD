# WorldAI — Cleanup Script
# 핸드오프 전 임시 파일 및 불필요한 아티팩트를 정리한다

Write-Host "🧹 WorldAI 클린업 시작..." -ForegroundColor Cyan

# Python 캐시 정리
Write-Host "  Python 캐시 정리 중..." -ForegroundColor Gray
Get-ChildItem -Path "." -Recurse -Directory -Filter "__pycache__" |
    ForEach-Object { Remove-Item $_.FullName -Recurse -Force }

Get-ChildItem -Path "." -Recurse -Filter "*.pyc" |
    ForEach-Object { Remove-Item $_.FullName -Force }

Get-ChildItem -Path "." -Recurse -Filter "*.pyo" |
    ForEach-Object { Remove-Item $_.FullName -Force }

# pytest 캐시 정리
if (Test-Path ".pytest_cache") {
    Remove-Item ".pytest_cache" -Recurse -Force
}

# mypy 캐시 정리
if (Test-Path ".mypy_cache") {
    Remove-Item ".mypy_cache" -Recurse -Force
}

# Node modules는 유지 (재설치 비용 큼)
Write-Host "  ℹ️  node_modules는 유지됨 (필요시 수동 삭제)" -ForegroundColor Gray

# runtime 임시파일 정리
Get-ChildItem -Path "harness/runtime" -Exclude ".gitkeep" |
    ForEach-Object { Remove-Item $_.FullName -Force }

Write-Host "✅ 클린업 완료" -ForegroundColor Green
Write-Host "   이제 핸드오프가 준비되었습니다." -ForegroundColor Yellow
