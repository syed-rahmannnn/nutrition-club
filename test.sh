#!/bin/bash

# Comprehensive Test Script for Membership Management System
echo "=== Running Comprehensive Tests ==="

COMPOSE_CMD="docker-compose"
if ! command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker compose"
fi

BASE_URL="http://localhost:8000"

echo "🧪 Running Django unit tests..."
$COMPOSE_CMD exec web python manage.py test

if [ $? -ne 0 ]; then
    echo "❌ Unit tests failed!"
    exit 1
fi

echo "✅ Unit tests passed"

echo "🔍 Testing API endpoints..."

# Test health check
echo "Testing health check endpoint..."
response=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/health/)
if [ "$response" = "200" ]; then
    echo "✅ Health check OK"
else
    echo "❌ Health check failed (HTTP $response)"
fi

# Test dashboard stats (requires auth)
echo "Testing dashboard stats..."
response=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/dashboard/stats/)
if [ "$response" = "403" ]; then
    echo "✅ Dashboard stats requires authentication (as expected)"
elif [ "$response" = "200" ]; then
    echo "✅ Dashboard stats OK (authenticated user)"
else
    echo "⚠️  Dashboard stats returned HTTP $response"
fi

echo "📊 Testing database operations..."
# Check if we can connect to database
$COMPOSE_CMD exec web python manage.py dbshell -c "SELECT COUNT(*) FROM django_migrations;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Database connection OK"
else
    echo "❌ Database connection failed"
fi

echo "🔄 Testing migrations..."
$COMPOSE_CMD exec web python manage.py showmigrations --plan > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Migration status OK"
else
    echo "❌ Migration check failed"
fi

echo "📁 Testing static files..."
response=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/static/js/ums.js)
if [ "$response" = "200" ]; then
    echo "✅ Static files serving OK"
else
    echo "⚠️  Static files check returned HTTP $response"
fi

echo "🏠 Testing homepage..."
response=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/)
if [ "$response" = "200" ]; then
    echo "✅ Homepage loading OK"
else
    echo "❌ Homepage failed (HTTP $response)"
fi

echo "🎯 Testing UMS page..."
response=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/ums/)
if [ "$response" = "200" ]; then
    echo "✅ UMS page loading OK"
else
    echo "❌ UMS page failed (HTTP $response)"
fi

echo ""
echo "🎉 Test suite completed!"
echo "📋 Summary:"
echo "   - Unit tests: Django test suite"
echo "   - API endpoints: Health, auth, static files"
echo "   - Database: Connection and migrations"
echo "   - Frontend: Homepage and UMS page"
echo ""
echo "💡 To test attendance submission:"
echo "   1. Login to admin: $BASE_URL/admin/"
echo "   2. Go to UMS page: $BASE_URL/ums/"
echo "   3. Select members and submit attendance"
echo "   4. Generate PDF report"
echo ""