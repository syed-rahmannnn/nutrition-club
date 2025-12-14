@echo off
echo === Checking Docker Status ===
echo.

REM Check if Docker is responding
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Desktop is not running yet
    echo.
    echo Please:
    echo 1. Start Docker Desktop from Start Menu
    echo 2. Wait for it to fully load ^(whale icon in system tray^)
    echo 3. Run this script again
    echo.
    pause
    exit /b 1
)

echo ✅ Docker is running!
echo.
echo 🚀 Starting membership management system...
echo.

REM Build and start services
docker-compose up --build -d

if %errorlevel% neq 0 (
    echo ❌ Failed to start services
    echo.
    echo 📋 Troubleshooting:
    echo - Check Docker Desktop is fully started
    echo - Try: docker-compose down then docker-compose up --build
    echo.
    pause
    exit /b 1
)

echo ⏳ Waiting for services to initialize...
timeout /t 15 /nobreak >nul

echo 🔄 Running database migrations...
docker-compose exec web python manage.py migrate

echo 📊 Creating sample data...
docker-compose exec web python manage.py seed_data --count 20

echo.
echo 🎉 System is ready!
echo.
echo 📋 Access Points:
echo    Homepage: http://localhost:8000/
echo    Admin:    http://localhost:8000/admin/
echo    UMS:      http://localhost:8000/ums/
echo.
echo 🔑 Default Credentials:
echo    Admin:    admin / admin123
echo    Operator: operator / operator123
echo.
echo 📝 Next Steps:
echo 1. Open browser: http://localhost:8000/
echo 2. Try UMS attendance: http://localhost:8000/ums/
echo 3. Login to admin: http://localhost:8000/admin/
echo.
pause