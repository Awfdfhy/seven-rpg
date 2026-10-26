# Seven RPG — MVP-0 Quick Start (PowerShell)
# Directive: codex-fable5 — verify before completion; evidence-first.
# Run: .\run_mvp0.ps1

$ErrorActionPreference = "Stop"

Write-Host "🎮 Seven RPG — MVP-0 Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check Python
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Write-Host "❌ Python not found. Install Python 3.11+ first." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python found: $($pythonPath.Source)" -ForegroundColor Green

# Install dependencies
Write-Host "`n📦 Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

# Run mock provider smoke test
Write-Host "`n🧪 Running mock provider smoke test..." -ForegroundColor Cyan
python tools/mock_provider.py

# Run MVP-0 tests
Write-Host "`n🧪 Running MVP-0 acceptance tests..." -ForegroundColor Cyan
pytest tests/test_mvp0_smoke.py -v

# Run main smoke test
Write-Host "`n🚀 Running main MVP-0 smoke test..." -ForegroundColor Cyan
python main.py

Write-Host "`n✅ MVP-0 Quick Start complete." -ForegroundColor Green
Write-Host "Next: Complete stack scorecard (docs/STACK_SCORECARD.md) and ADR-0001." -ForegroundColor Yellow