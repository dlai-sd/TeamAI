#!/bin/bash
#
# Backend-Only Test Setup (Alpine Codespace Compatible)
# For intensive testing without Docker/Node dependencies
#

set -e

echo "=================================="
echo "TeamAI - Backend Test Setup"
echo "=================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Setup Python virtual environment
echo "🐍 Setting up Python environment..."
echo "-----------------------------------"

cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    echo "Installing dependencies..."
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
    
    echo "✅ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
    source venv/bin/activate
fi

cd ..

echo ""
echo "=================================="
echo "✅ Backend Test Environment Ready!"
echo "=================================="
echo ""
echo "📋 Quick Start Commands:"
echo ""
echo "1. Activate virtual environment:"
echo "   cd /workspaces/TeamAI/backend"
echo "   source venv/bin/activate"
echo ""
echo "2. Run tests (instant - no Docker):"
echo "   pytest tests/test_agents/test_recipe_evaluator.py -v"
echo "   pytest tests/test_agents/test_agent_runtime.py -v"
echo "   pytest tests/test_api/test_agent_api.py -v"
echo ""
echo "3. Run specific test:"
echo "   pytest tests/test_agents/test_recipe_evaluator.py::TestDAGExecution -v"
echo ""
echo "4. Watch mode (auto-run on change):"
echo "   pip install pytest-watch"
echo "   ptw tests/test_agents/ -- -x --tb=short"
echo ""
echo "5. Run with coverage:"
echo "   pytest tests/ --cov=app --cov=agents --cov-report=term-missing"
echo ""
echo "=================================="
echo "⚡ Fast Iteration Workflow:"
echo "=================================="
echo ""
echo "1. Edit code: vim backend/agents/recipe_evaluator.py"
echo "2. Run test:  pytest tests/test_agents/test_recipe_evaluator.py -x"
echo "3. Fix issue: (edit code)"
echo "4. Re-run:    pytest tests/test_agents/test_recipe_evaluator.py -x"
echo "5. Repeat!"
echo ""
echo "💡 Tip: Use -x flag to stop on first failure"
echo "💡 Tip: Use --tb=short for concise error output"
echo "💡 Tip: Use -k 'test_name' to run specific test"
echo ""
