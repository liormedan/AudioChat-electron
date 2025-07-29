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
    echo Please run: scripts\setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔄 Activating Python environment...
call .venv\Scripts\activate.bat

REM Start Backend in background
echo 🔵 Starting Backend API (Port 5000)...
start /min "Audio Chat Studio - Backend" cmd /c "call .venv\Scripts\activate.bat && python backend\main.py --port 5000"

REM Wait for backend to initialize
echo ⏳ Waiting for Backend initialization...
timeout /t 5 /nobreak >nul

REM Check if Node.js is available
where node >nul 2>&1
if not errorlevel 1 (
    if exist "frontend\electron-app\package.json" (
        echo 🌐 Starting Frontend (Port 5174)...
        cd frontend\electron-app
        start /min "Audio Chat Studio - Frontend" cmd /c "npm run dev"
        cd ..\..
    ) else (
        echo ⚠️ Frontend not found, starting Backend only
    )
) else (
    echo ⚠️ Node.js not found, starting Backend only
)

REM Wait for services to start
echo ⏳ Waiting for services to start...
timeout /t 8 /nobreak >nul

REM Open the application
echo 🌐 Opening Audio Chat Studio...
start "" http://127.0.0.1:5174

echo.
echo ✅ Audio Chat Studio Started Successfully!
echo.
echo 📱 Available Services:
echo    • Main App:      http://127.0.0.1:5174
echo    • Backend API:   http://127.0.0.1:5000
echo    • Swagger UI:    http://127.0.0.1:5000/docs
echo.
echo 🎛️ Use the Terminal page in the app for system control
echo 🛑 To stop: Run scripts\stop.bat or use Terminal page
echo.
echo The system is now running in the background.
echo You can close this window safely.
timeout /t 3 /nobreak >nul