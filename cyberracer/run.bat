@echo off
echo.
echo =====================================================
echo     CYBERRACER - Startup Script (Windows)
echo     OBI Cybernetic Authentication Game
echo =====================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed
    pause
    exit /b 1
)

echo [OK] Python found

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Installing OBI SDK...
pip install obi

echo.
echo [OK] Installation complete!
echo.
echo Starting CyberRacer Backend...
echo Server will be available at: http://localhost:5000
echo.

cd backend
python app.py

pause
