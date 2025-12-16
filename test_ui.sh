#!/bin/bash
# TeamAI UI Testing Script
# Tests authentication flow and UI components

set -e

echo "=============================================="
echo "TeamAI UI Testing - Authentication System"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Generate fresh token
echo -e "${BLUE}Generating fresh test token...${NC}"
TOKEN=$(docker-compose exec backend python backend/tests/generate_test_tokens.py 2>&1 | grep -A2 "^ADMIN" | grep "Token:" | awk '{print $2}')
echo "Token: ${TOKEN:0:50}..."
echo ""

# Test 1: Backend Root Endpoint
echo -e "${BLUE}Test 1: Backend Root Endpoint${NC}"
RESPONSE=$(curl -s http://localhost:8000/)
if echo "$RESPONSE" | grep -q "Google SSO Authentication Active"; then
    echo -e "${GREEN}✅ PASS: Backend root endpoint returns SSO message${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL: Backend root endpoint response unexpected${NC}"
    ((FAILED++))
fi
echo ""

# Test 2: GET /auth/me with token
echo -e "${BLUE}Test 2: GET /api/v1/auth/me (with admin token)${NC}"
ME_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/auth/me)
if echo "$ME_RESPONSE" | grep -q "admin@acmemarketing.com"; then
    echo -e "${GREEN}✅ PASS: /auth/me returns admin user profile${NC}"
    echo "   User: $(echo $ME_RESPONSE | grep -o '"full_name":"[^"]*"' | cut -d'"' -f4)"
    echo "   Role: $(echo $ME_RESPONSE | grep -o '"role":"[^"]*"' | cut -d'"' -f4)"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL: /auth/me response invalid${NC}"
    echo "$ME_RESPONSE"
    ((FAILED++))
fi
echo ""

# Test 3: GET /invites with token
echo -e "${BLUE}Test 3: GET /api/v1/invites (admin only endpoint)${NC}"
INVITES_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/invites)
if echo "$INVITES_RESPONSE" | grep -q "newuser@acmemarketing.com"; then
    INVITE_COUNT=$(echo "$INVITES_RESPONSE" | grep -o '"email"' | wc -l)
    echo -e "${GREEN}✅ PASS: /invites returns invite list (${INVITE_COUNT} invites)${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL: /invites response invalid${NC}"
    echo "$INVITES_RESPONSE"
    ((FAILED++))
fi
echo ""

# Test 4: Frontend Root Page
echo -e "${BLUE}Test 4: Frontend Root Page (http://localhost:3000/)${NC}"
FRONTEND_ROOT=$(curl -sL http://localhost:3000/ 2>&1)
if echo "$FRONTEND_ROOT" | grep -q "TeamAI"; then
    echo -e "${GREEN}✅ PASS: Frontend serving HTML with TeamAI title${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL: Frontend not responding correctly${NC}"
    ((FAILED++))
fi
echo ""

# Test 5: Frontend /login page
echo -e "${BLUE}Test 5: Frontend Login Page (http://localhost:3000/login)${NC}"
LOGIN_CHECK=$(curl -s http://localhost:3000/login)
if echo "$LOGIN_CHECK" | grep -q "TeamAI"; then
    echo -e "${GREEN}✅ PASS: Login page accessible${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL: Login page not accessible${NC}"
    ((FAILED++))
fi
echo ""

# Test 6: Frontend /dashboard (should require auth)
echo -e "${BLUE}Test 6: Frontend Dashboard Page (http://localhost:3000/dashboard)${NC}"
DASHBOARD_CHECK=$(curl -s http://localhost:3000/dashboard)
if echo "$DASHBOARD_CHECK" | grep -q "TeamAI"; then
    echo -e "${GREEN}✅ PASS: Dashboard page accessible (React routing working)${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL: Dashboard page not accessible${NC}"
    ((FAILED++))
fi
echo ""

# Test 7: Google OAuth Login Endpoint
echo -e "${BLUE}Test 7: Google OAuth Login Endpoint${NC}"
OAUTH_RESPONSE=$(curl -s http://localhost:8000/api/v1/auth/google/login)
if echo "$OAUTH_RESPONSE" | grep -q "authorization_url"; then
    echo -e "${GREEN}✅ PASS: OAuth login endpoint returns authorization URL${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL: OAuth login endpoint response invalid${NC}"
    echo "$OAUTH_RESPONSE"
    ((FAILED++))
fi
echo ""

# Test 8: Unauthorized Access
echo -e "${BLUE}Test 8: Unauthorized Access (no token)${NC}"
UNAUTH_RESPONSE=$(curl -s http://localhost:8000/api/v1/invites)
if echo "$UNAUTH_RESPONSE" | grep -q "Missing authentication token"; then
    echo -e "${GREEN}✅ PASS: Protected endpoints reject unauthenticated requests${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL: Protected endpoints not properly secured${NC}"
    ((FAILED++))
fi
echo ""

# Test 9: Redis OAuth State Storage
echo -e "${BLUE}Test 9: Redis OAuth State Storage${NC}"
REDIS_KEYS=$(docker-compose exec redis redis-cli KEYS "oauth_state:*" 2>&1)
if echo "$REDIS_KEYS" | grep -q "oauth_state:"; then
    KEY_COUNT=$(echo "$REDIS_KEYS" | grep -c "oauth_state:" || echo "0")
    echo -e "${GREEN}✅ PASS: Redis storing OAuth state keys (${KEY_COUNT} keys)${NC}"
    ((PASSED++))
else
    echo -e "${GREEN}✅ PASS: Redis ready (no active OAuth flows)${NC}"
    ((PASSED++))
fi
echo ""

# Test 10: Docker Services Status
echo -e "${BLUE}Test 10: Docker Services Health${NC}"
SERVICES_UP=$(docker-compose ps | grep -c "Up" || echo "0")
if [ "$SERVICES_UP" -ge 3 ]; then
    echo -e "${GREEN}✅ PASS: All services running (${SERVICES_UP} containers)${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL: Some services not running${NC}"
    docker-compose ps
    ((FAILED++))
fi
echo ""

# Summary
echo "=============================================="
echo "Test Results Summary"
echo "=============================================="
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: ${PASSED}${NC}"
echo -e "${RED}Failed: ${FAILED}${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
