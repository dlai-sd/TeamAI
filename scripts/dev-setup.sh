#!/bin/bash
#
# Local Development Setup - Fast Iteration
# Run backend/frontend locally, use Docker only for databases
#

set -e

echo "=================================="
echo "TeamAI - Local Development Setup"
echo "=================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 not found"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js not found"; exit 1; }

# Start only database services in Docker
echo ""
echo "📦 Starting database services (Docker)..."
echo "-----------------------------------"
docker compose up -d postgres redis

# Wait for databases to be ready
echo "⏳ Waiting for databases to initialize..."
sleep 5

# Check database health
docker compose ps postgres redis

echo ""
echo "✅ Databases ready"

# Setup Python virtual environment
echo ""
echo "🐍 Setting up Python backend..."
echo "-----------------------------------"

if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    cd ..
else
    echo "Virtual environment exists"
fi

# Run database migrations
echo ""
echo "Running database migrations..."
source backend/venv/bin/activate
cd backend
export DATABASE_URL="postgresql://teamai:teamai_dev_password@localhost:5432/teamai"
export REDIS_URL="redis://localhost:6379/0"
alembic upgrade head
cd ..

echo ""
echo "✅ Backend setup complete"

# Setup Node.js frontend
echo ""
echo "⚛️  Setting up React frontend..."
echo "-----------------------------------"

if [ ! -d "frontend/node_modules" ]; then
    echo "Installing Node dependencies..."
    cd frontend
    npm install
    cd ..
else
    echo "Node modules exist"
fi

echo ""
echo "✅ Frontend setup complete"

# Create local environment files if missing
echo ""
echo "🔧 Checking environment files..."
echo "-----------------------------------"

if [ ! -f "backend/.env" ]; then
    echo "Creating backend/.env..."
    cat > backend/.env << 'EOF'
# Database
DATABASE_URL=postgresql://teamai:teamai_dev_password@localhost:5432/teamai
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=dev_secret_key_change_in_production
SECRET_KEY=dev_secret_key_change_in_production

# OAuth (use your actual credentials)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# Azure Key Vault (local mode)
USE_AZURE_KEYVAULT=false

# Groq API
GROQ_API_KEY=your_groq_api_key

# Environment
ENVIRONMENT=development
LOG_LEVEL=DEBUG
EOF
    echo "⚠️  Created backend/.env - UPDATE with your actual credentials!"
else
    echo "✓ backend/.env exists"
fi

if [ ! -f "frontend/.env" ]; then
    echo "Creating frontend/.env..."
    cat > frontend/.env << 'EOF'
VITE_API_URL=http://localhost:8000
EOF
    echo "✓ Created frontend/.env"
else
    echo "✓ frontend/.env exists"
fi

echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd /workspaces/TeamAI/backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd /workspaces/TeamAI/frontend"
echo "  npm run dev"
echo ""
echo "Terminal 3 - Tests:"
echo "  # Backend tests (instant - no Docker rebuild)"
echo "  cd /workspaces/TeamAI/backend"
echo "  source venv/bin/activate"
echo "  pytest tests/test_agents/ -v"
echo ""
echo "  # Frontend tests (instant)"
echo "  cd /workspaces/TeamAI/frontend"
echo "  npm run test"
echo ""
echo "=================================="
echo "🚀 Fast Iteration Workflow:"
echo "=================================="
echo ""
echo "1. Edit code in /workspaces/TeamAI"
echo "2. Backend auto-reloads (uvicorn --reload)"
echo "3. Frontend auto-reloads (Vite HMR)"
echo "4. Run tests instantly (no Docker rebuild)"
echo "5. Repeat!"
echo ""
echo "💾 Docker services running:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo ""
echo "🔗 Access URLs:"
echo "  - Backend API: http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
