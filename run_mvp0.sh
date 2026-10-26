#!/usr/bin/env bash
# Seven RPG — MVP-0 Quick Start (Bash/Linux/macOS)
# Directive: codex-fable5 — verify before completion; evidence-first.
# Usage: ./run_mvp0.sh

set -euo pipefail

echo "🎮 Seven RPG — MVP-0 Quick Start"
echo "========================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install Python 3.11+ first."
    exit 1
fi
echo "✅ Python found: $(python3 --version)"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run mock provider smoke test
echo ""
echo "🧪 Running mock provider smoke test..."
python3 tools/mock_provider.py

# Run MVP-0 tests
echo ""
echo "🧪 Running MVP-0 acceptance tests..."
pytest tests/test_mvp0_smoke.py -v

# Run main smoke test
echo ""
echo "🚀 Running main MVP-0 smoke test..."
python3 main.py

echo ""
echo "✅ MVP-0 Quick Start complete."
echo "Next: Complete stack scorecard (docs/STACK_SCORECARD.md) and ADR-0001."