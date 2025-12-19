#!/bin/bash
# Development setup script
# Prepares the environment for local development

set -e  # Exit on error

echo "🚀 Setting up Assessment Tool development environment..."

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: Run this script from the assessment-tool directory"
    exit 1
fi

# Backend setup
echo ""
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Initialize database
if [ ! -f "assessment.db" ]; then
    echo "Initializing database..."
    python -c "from database import init_db; init_db()"
fi

# Create logs directory
mkdir -p logs

echo "✅ Backend setup complete"

# Frontend setup
echo ""
echo "📦 Setting up frontend..."
cd ../frontend-v1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install --silent
else
    echo "npm dependencies already installed"
fi

echo "✅ Frontend setup complete"

# Create .env files if they don't exist
cd ..
echo ""
echo "📝 Creating environment files..."

if [ ! -f "backend/.env" ]; then
    echo "Creating backend/.env from example..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your actual credentials"
fi

if [ ! -f "frontend-v1/.env" ]; then
    echo "Creating frontend-v1/.env from example..."
    cp frontend-v1/.env.example frontend-v1/.env
fi

echo "✅ Environment files ready"

# Summary
echo ""
echo "✨ Setup complete! Next steps:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    cd backend"
echo "    source venv/bin/activate"
echo "    python main.py"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    cd frontend-v1"
echo "    npm run dev"
echo ""
echo "  Then open: http://localhost:3000"
echo ""
echo "  API Docs: http://localhost:8000/docs"
echo ""

# Offer to start services
read -p "Start services now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting backend..."
    cd backend
    source venv/bin/activate
    python main.py &
    BACKEND_PID=$!
    
    echo "Starting frontend..."
    cd ../frontend-v1
    npm run dev &
    FRONTEND_PID=$!
    
    echo ""
    echo "✅ Services started!"
    echo "   Backend PID: $BACKEND_PID"
    echo "   Frontend PID: $FRONTEND_PID"
    echo ""
    echo "   Press Ctrl+C to stop services"
    echo ""
    
    # Wait for user interrupt
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
    wait
fi
