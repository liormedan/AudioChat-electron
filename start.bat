@echo off
chcp 65001 >nul
title Audio Chat Studio - Quick Start

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    Quick Start - Starting Everything
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment not found!
    echo Running setup...
    call scripts\setup.bat
    if errorlevel 1 (
        echo ❌ Setup failed!
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔄 Activating Python environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment!
    pause
    exit /b 1
)

REM Create directories
echo 📁 Creating directories...
if not exist "uploads" mkdir uploads
if not exist "data" mkdir data
if not exist "data\uploads" mkdir data\uploads
if not exist "data\temp" mkdir data\temp
if not exist "logs" mkdir logs

REM Start Backend
echo 🔵 Starting Backend API (Port 5000)...
start /min "Audio Chat Studio - Backend" cmd /c "python backend\main.py --port 5000"

REM Wait for backend
echo ⏳ Waiting for Backend initialization...
timeout /t 5 /nobreak >nul

REM Check for Node.js and start frontend
where node >nul 2>&1
if not errorlevel 1 (
    if exist "frontend\electron-app\package.json" (
        echo 🌐 Starting Frontend...
        start /min "Audio Chat Studio - Frontend" cmd /c "cd frontend\electron-app && npm run dev"
    )
)

REM Wait for services
echo ⏳ Waiting for services to start...
timeout /t 8 /nobreak >nul

REM Open browser
echo 🌐 Opening Audio Chat Studio...
start "" http://127.0.0.1:5000

echo.
echo ✅ Audio Chat Studio Started Successfully!
echo.
echo 📱 Available Services:
echo    • Backend API:   http://127.0.0.1:5000
echo    • API Docs:      http://127.0.0.1:5000/docs
echo    • Frontend:      http://127.0.0.1:5174 (if Node.js available)
echo.
echo 🛑 To stop: Run scripts\stop.bat
echo.
echo The system is now running in the background.
echo You can close this window safely.
timeout /t 3 /nobreak >nul
