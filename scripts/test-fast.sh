#!/bin/bash
#
# Quick Test Runner - Local Development (No Docker)
# Run tests instantly without Docker rebuild cycle
#

set -e

echo "=================================="
echo "TeamAI - Fast Test Runner"
echo "=================================="
echo ""

# Activate Python venv if exists
if [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
    echo "✓ Python venv activated"
else
    echo "⚠️  Run ./scripts/dev-setup.sh first to create venv"
    exit 1
fi

# Export test environment variables
export DATABASE_URL="postgresql://teamai:teamai_dev_password@localhost:5432/teamai"
export REDIS_URL="redis://localhost:6379/0"
export USE_AZURE_KEYVAULT="false"
export GROQ_API_KEY="${GROQ_API_KEY:-mock_key_for_tests}"
export ENVIRONMENT="test"

# Parse command line arguments
PATTERN="${1:-tests/}"
VERBOSE="${2:--v}"

echo ""
echo "🧪 Running Backend Tests..."
echo "Pattern: $PATTERN"
echo "-----------------------------------"

cd backend

# Run pytest with coverage
pytest $PATTERN $VERBOSE \
    --tb=short \
    --maxfail=3 \
    -x \
    2>&1

TEST_EXIT_CODE=$?

cd ..

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Tests failed with exit code $TEST_EXIT_CODE"
    exit $TEST_EXIT_CODE
fi

echo ""
echo "=================================="
echo "⚡ Fast Test Examples:"
echo "=================================="
echo ""
echo "All tests:"
echo "  ./scripts/test-fast.sh"
echo ""
echo "Specific file:"
echo "  ./scripts/test-fast.sh tests/test_agents/test_recipe_evaluator.py"
echo ""
echo "Specific test class:"
echo "  ./scripts/test-fast.sh tests/test_agents/test_recipe_evaluator.py::TestDAGExecution"
echo ""
echo "Specific test:"
echo "  ./scripts/test-fast.sh tests/test_agents/test_recipe_evaluator.py::TestDAGExecution::test_build_execution_order"
echo ""
echo "With detailed output:"
echo "  ./scripts/test-fast.sh tests/ -vv"
echo ""
echo "Watch mode (run on file change):"
echo "  cd backend && pytest-watch tests/"
echo ""
