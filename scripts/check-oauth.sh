#!/bin/bash
# Quick setup script to check Google OAuth configuration

echo "🔍 Checking Google OAuth Configuration..."
echo ""

# Check if backend .env exists
if [ ! -f "backend/.env" ]; then
    echo "❌ backend/.env not found!"
    echo "   Run: cp backend/.env.example backend/.env"
    exit 1
fi

# Source the .env file
source backend/.env

# Check GOOGLE_CLIENT_ID
if [ -z "$GOOGLE_CLIENT_ID" ]; then
    echo "❌ GOOGLE_CLIENT_ID is empty in backend/.env"
    echo ""
    echo "📋 Setup instructions:"
    echo "   1. Visit: https://console.cloud.google.com/apis/credentials"
    echo "   2. Create OAuth 2.0 Client ID"
    echo "   3. Set redirect URI: http://localhost:8000/api/v1/auth/google/callback"
    echo "   4. Copy Client ID to backend/.env"
    echo ""
    echo "📖 Full guide: docs/GOOGLE_OAUTH_SETUP.md"
    exit 1
else
    echo "✅ GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID:0:20}..."
fi

# Check GOOGLE_CLIENT_SECRET
if [ -z "$GOOGLE_CLIENT_SECRET" ]; then
    echo "❌ GOOGLE_CLIENT_SECRET is empty in backend/.env"
    echo "   Add your client secret from Google Cloud Console"
    exit 1
else
    echo "✅ GOOGLE_CLIENT_SECRET: ${GOOGLE_CLIENT_SECRET:0:10}..."
fi

# Check GOOGLE_REDIRECT_URI
if [ -z "$GOOGLE_REDIRECT_URI" ]; then
    echo "⚠️  GOOGLE_REDIRECT_URI is empty (using default)"
    export GOOGLE_REDIRECT_URI="http://localhost:8000/api/v1/auth/google/callback"
fi
echo "✅ GOOGLE_REDIRECT_URI: $GOOGLE_REDIRECT_URI"

# Check if services are running
echo ""
echo "🐳 Checking Docker services..."
if ! docker-compose ps | grep -q "teamai-backend.*Up"; then
    echo "❌ Backend service not running"
    echo "   Run: docker-compose up -d"
    exit 1
else
    echo "✅ Backend running on port 8000"
fi

if ! docker-compose ps | grep -q "teamai-frontend.*Up"; then
    echo "❌ Frontend service not running"
    echo "   Run: docker-compose up -d"
    exit 1
else
    echo "✅ Frontend running on port 3000"
fi

# Test backend health
echo ""
echo "🏥 Testing backend health..."
HEALTH=$(curl -s http://localhost:8000/ | grep -o "Google SSO")
if [ -n "$HEALTH" ]; then
    echo "✅ Backend responding correctly"
else
    echo "❌ Backend not responding"
    echo "   Check logs: docker-compose logs backend"
    exit 1
fi

echo ""
echo "✅ All checks passed!"
echo ""
echo "🚀 Next steps:"
echo "   1. Open: http://localhost:3000/login"
echo "   2. Click 'Sign in with Google'"
echo "   3. Authenticate with your Google account"
echo "   4. You should be redirected to the dashboard"
echo ""
echo "📊 Monitor logs:"
echo "   Backend:  docker-compose logs -f backend"
echo "   Frontend: docker-compose logs -f frontend"
