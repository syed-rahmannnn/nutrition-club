@echo off
REM Membership Management System Setup Script for Windows

echo === Membership Management System Setup ===

REM Check if Docker is available
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first:
    echo    https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo ✅ Docker is available

REM Try docker-compose first, then docker compose
docker-compose version >nul 2>&1
if %errorlevel% equ 0 (
    set COMPOSE_CMD=docker-compose
) else (
    docker compose version >nul 2>&1
    if %errorlevel% equ 0 (
        set COMPOSE_CMD=docker compose
    ) else (
        echo ❌ Docker Compose is not available
        pause
        exit /b 1
    )
)

echo 📦 Building Docker containers...
%COMPOSE_CMD% build

echo 🚀 Starting services...
%COMPOSE_CMD% up -d

echo ⏳ Waiting for database to be ready...
timeout /t 10 /nobreak >nul

echo 🔄 Running database migrations...
%COMPOSE_CMD% exec web python manage.py migrate

echo 📊 Creating sample data...
%COMPOSE_CMD% exec web python manage.py seed_data --count 20

echo 📁 Collecting static files...
%COMPOSE_CMD% exec web python manage.py collectstatic --noinput

echo.
echo 🎉 Setup complete!
echo.
echo 📋 Next steps:
echo    1. Create superuser: %COMPOSE_CMD% exec web python manage.py createsuperuser
echo    2. Access admin: http://localhost:8000/admin/
echo    3. Access app: http://localhost:8000/
echo    4. Run tests: %COMPOSE_CMD% exec web python manage.py test
echo.
echo 🔧 Useful commands:
echo    - View logs: %COMPOSE_CMD% logs -f web
echo    - Stop services: %COMPOSE_CMD% down
echo    - Restart: %COMPOSE_CMD% restart web
echo.
pause