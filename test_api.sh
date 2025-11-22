#!/bin/bash

# Task Management API Test Script
# This script demonstrates the API functionality

set -e

BASE_URL="http://localhost:5000"
API_URL="${BASE_URL}/api"

echo "🧪 Task Management API Test Script"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo -e "${BLUE}Test 1: Health Check${NC}"
curl -s "${BASE_URL}/health" | jq '.'
echo ""
echo ""

# Test 2: Register User
echo -e "${BLUE}Test 2: Register User${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "${API_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }')

echo "$REGISTER_RESPONSE" | jq '.'
TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.token')
echo -e "${GREEN}✓ User registered, token saved${NC}"
echo ""
echo ""

# Test 3: Login
echo -e "${BLUE}Test 3: Login${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }')

echo "$LOGIN_RESPONSE" | jq '.'
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token')
echo -e "${GREEN}✓ Login successful${NC}"
echo ""
echo ""

# Test 4: Get Current User
echo -e "${BLUE}Test 4: Get Current User${NC}"
curl -s -X GET "${API_URL}/auth/me" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
echo -e "${GREEN}✓ User info retrieved${NC}"
echo ""
echo ""

# Test 5: Create Category
echo -e "${BLUE}Test 5: Create Category${NC}"
CATEGORY_RESPONSE=$(curl -s -X POST "${API_URL}/categories" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Work",
    "description": "Work-related tasks",
    "color": "#3498db"
  }')

echo "$CATEGORY_RESPONSE" | jq '.'
CATEGORY_ID=$(echo "$CATEGORY_RESPONSE" | jq -r '.category.id')
echo -e "${GREEN}✓ Category created (ID: ${CATEGORY_ID})${NC}"
echo ""
echo ""

# Test 6: Get All Categories
echo -e "${BLUE}Test 6: Get All Categories${NC}"
curl -s -X GET "${API_URL}/categories" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
echo -e "${GREEN}✓ Categories retrieved${NC}"
echo ""
echo ""

# Test 7: Create Task
echo -e "${BLUE}Test 7: Create Task${NC}"
TASK_RESPONSE=$(curl -s -X POST "${API_URL}/tasks" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Complete API Testing\",
    \"description\": \"Test all API endpoints thoroughly\",
    \"status\": \"pending\",
    \"priority\": \"high\",
    \"category_id\": ${CATEGORY_ID},
    \"due_date\": \"2024-12-31T23:59:59\"
  }")

echo "$TASK_RESPONSE" | jq '.'
TASK_ID=$(echo "$TASK_RESPONSE" | jq -r '.task.id')
echo -e "${GREEN}✓ Task created (ID: ${TASK_ID})${NC}"
echo ""
echo ""

# Test 8: Get All Tasks
echo -e "${BLUE}Test 8: Get All Tasks${NC}"
curl -s -X GET "${API_URL}/tasks" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
echo -e "${GREEN}✓ Tasks retrieved${NC}"
echo ""
echo ""

# Test 9: Get Single Task
echo -e "${BLUE}Test 9: Get Single Task${NC}"
curl -s -X GET "${API_URL}/tasks/${TASK_ID}" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
echo -e "${GREEN}✓ Task retrieved${NC}"
echo ""
echo ""

# Test 10: Update Task
echo -e "${BLUE}Test 10: Update Task${NC}"
curl -s -X PUT "${API_URL}/tasks/${TASK_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "priority": "high"
  }' | jq '.'
echo -e "${GREEN}✓ Task updated${NC}"
echo ""
echo ""

# Test 11: Get Task Statistics
echo -e "${BLUE}Test 11: Get Task Statistics${NC}"
curl -s -X GET "${API_URL}/stats" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
echo -e "${GREEN}✓ Statistics retrieved${NC}"
echo ""
echo ""

# Test 12: Filter Tasks
echo -e "${BLUE}Test 12: Filter Tasks (status=in_progress)${NC}"
curl -s -X GET "${API_URL}/tasks?status=in_progress&page=1&per_page=10" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
echo -e "${GREEN}✓ Filtered tasks retrieved${NC}"
echo ""
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ All tests completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Token for manual testing: ${TOKEN}"
echo ""
echo "You can now use this token to test other endpoints manually:"
echo "export TOKEN='${TOKEN}'"
echo ""
