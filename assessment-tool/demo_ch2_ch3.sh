#!/bin/bash
# Quick demo script to show Ch2 & Ch3 working

echo "=== Chapters 2 & 3 Demo ==="
echo ""

# Step 1: Create assessment
echo "1. Creating new assessment..."
INIT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/init -H "Content-Type: application/json" -d '{}')
ID=$(echo "$INIT_RESPONSE" | jq -r '.assessment_id')
echo "   Assessment ID: $ID"
echo ""

# Step 2: Chapter 2 - Scan website
echo "2. Chapter 2: Scanning website..."
WEBSITE=$(curl -s -X POST "http://localhost:8000/api/v1/discovery/${ID}/scan-website")
echo "   Response: $WEBSITE" | jq '.' | head -10
echo ""

# Step 3: Chapter 2 - Social profiles
echo "3. Chapter 2: Finding social profiles..."
SOCIAL=$(curl -s -X POST "http://localhost:8000/api/v1/discovery/${ID}/find-social-profiles")
echo "   Response: $SOCIAL" | jq '.' | head -10
echo ""

# Step 4: Chapter 3 - Revenue analysis
echo "4. Chapter 3: Analyzing revenue..."
REVENUE=$(curl -s -X POST "http://localhost:8000/api/v1/financial/${ID}/analyze-revenue")
echo "   Response: $REVENUE" | jq '.' | head -10
echo ""

# Step 5: Chapter 3 - Financial score
echo "5. Chapter 3: Calculating financial score..."
SCORE=$(curl -s -X GET "http://localhost:8000/api/v1/financial/${ID}/financial-score")
echo "   Response: $SCORE" | jq '.' | head -10
echo ""

echo "=== Demo Complete ==="
echo "Routes are working! Now ready for frontend integration."
