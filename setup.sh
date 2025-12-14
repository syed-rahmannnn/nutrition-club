#!/bin/bash

# Membership Management System Setup Script
echo "=== Membership Management System Setup ==="

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first:"
    echo "   https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker is available"

# Use docker-compose if available, otherwise use docker compose
COMPOSE_CMD="docker-compose"
if ! command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker compose"
fi

# Build the containers
echo "📦 Building Docker containers..."
$COMPOSE_CMD build

# Start the services
echo "🚀 Starting services..."
$COMPOSE_CMD up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run migrations
echo "🔄 Running database migrations..."
$COMPOSE_CMD exec web python manage.py migrate

# Create sample data
echo "📊 Creating sample data..."
$COMPOSE_CMD exec web python manage.py seed_data --count 20

# Collect static files
echo "📁 Collecting static files..."
$COMPOSE_CMD exec web python manage.py collectstatic --noinput

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Create superuser: $COMPOSE_CMD exec web python manage.py createsuperuser"
echo "   2. Access admin: http://localhost:8000/admin/"
echo "   3. Access app: http://localhost:8000/"
echo "   4. Run tests: $COMPOSE_CMD exec web python manage.py test"
echo ""
echo "🔧 Useful commands:"
echo "   - View logs: $COMPOSE_CMD logs -f web"
echo "   - Stop services: $COMPOSE_CMD down"
echo "   - Restart: $COMPOSE_CMD restart web"
echo ""