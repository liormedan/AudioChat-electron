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
    echo ❌ Virtual environment לא נמצא!
    echo 🔧 מפעיל התקנה אוטומטית...
    call scripts\setup.bat
    if errorlevel 1 (
        echo ❌ ההתקנה נכשלה!
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔄 Activating Python environment...
call .venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

REM Ensure upload directories exist
echo 📁 Checking upload directories...
if not exist "uploads" mkdir uploads
if not exist "data\uploads" mkdir data\uploads
if not exist "data\temp" mkdir data\temp
if not exist "logs" mkdir logs

REM Start Backend in background
echo 🔵 Starting Backend API (Port 5000)...
start /min "Audio Chat Studio - Backend" cmd /c "python backend\main.py --port 5000"

REM Wait for backend to initialize
echo ⏳ Waiting for Backend initialization...
timeout /t 5 /nobreak >nul

REM Check if Node.js is available
where node >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Node.js not found, starting Backend only
    set "HAS_NODE=false"
) else (
    if exist "frontend\electron-app\package.json" (
        echo 🌐 Starting Frontend (Port 5174)...
        start /min "Audio Chat Studio - Frontend" cmd /c "cd frontend\electron-app && npm run dev"
        set "HAS_NODE=true"
    ) else (
        echo ⚠️ Frontend not found, starting Backend only
        set "HAS_NODE=false"
    )
)

REM Wait for services to start
echo ⏳ Waiting for services to start...
timeout /t 8 /nobreak >nul

REM Check if backend is running
echo 🔍 Checking Backend status...
where curl >nul 2>&1
if %ERRORLEVEL%==0 (
    curl -s http://127.0.0.1:5000/health >nul 2>&1
    if %ERRORLEVEL%==0 (
        echo ✅ Backend is running
    ) else (
        echo ⚠️ Backend may not be ready yet
    )
) else (
    echo ⚠️ curl not available, skipping backend check
)

REM Open the application
echo 🌐 Opening Audio Chat Studio...
if "%HAS_NODE%"=="true" (
    start "" http://127.0.0.1:5174
) else (
    start "" http://127.0.0.1:5000
)

echo.
echo ✅ Audio Chat Studio Started Successfully!
echo.
echo 📱 Available Services:
if "%HAS_NODE%"=="true" (
    echo    • Main App:      http://127.0.0.1:5174
    echo    • Backend API:   http://127.0.0.1:5000
    echo    • Swagger UI:    http://127.0.0.1:5000/docs
) else (
    echo    • Backend API:   http://127.0.0.1:5000
    echo    • Swagger UI:    http://127.0.0.1:5000/docs
    echo    • Note: Frontend requires Node.js
)
echo.
echo 🎛️ Use the Terminal page in the app for system control
echo 🛑 To stop: Run scripts\stop.bat or use Terminal page
echo.
echo The system is now running in the background.
echo You can close this window safely.
timeout /t 3 /nobreak >nul
