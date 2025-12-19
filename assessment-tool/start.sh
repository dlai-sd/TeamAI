#!/bin/bash

echo "🔄 Stopping all existing processes..."
pkill -9 -f "uvicorn.*main_enhanced" 2>/dev/null || true
pkill -9 -f vite 2>/dev/null || true
pkill -9 -f "npm.*dev" 2>/dev/null || true
sleep 2

echo "🧹 Cleaning up old logs..."
rm -f /tmp/backend.log /tmp/frontend.log

echo "🚀 Starting backend on port 8000..."
cd /workspaces/TeamAI/assessment-tool/backend
source venv/bin/activate
nohup python main_enhanced.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

sleep 3

echo "🚀 Starting frontend on port 3000..."
cd /workspaces/TeamAI/assessment-tool/frontend-v1
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

sleep 4

echo ""
echo "✅ Services started!"
echo ""
echo "📋 Backend:  http://localhost:8000"
echo "   Health:   curl http://localhost:8000/health"
echo "   Logs:     tail -f /tmp/backend.log"
echo ""
echo "📋 Frontend: http://localhost:3000"
echo "   Logs:     tail -f /tmp/frontend.log"
echo ""
echo "🌐 Public URLs:"
echo "   Frontend: https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
echo "   Backend:  https://${CODESPACE_NAME}-8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
echo ""
echo "💡 Make sure both ports are set to PUBLIC in VS Code PORTS tab!"
echo ""
