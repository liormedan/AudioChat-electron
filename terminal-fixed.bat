@echo off
chcp 65001 >nul
title Audio Chat Studio - Terminal

:MENU
cls
echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    Terminal Control Center
echo ========================================
echo.

REM Check Backend status
python -c "import requests; requests.get('http://127.0.0.1:5000/', timeout=1)" >nul 2>&1
if not errorlevel 1 (
    echo 🟢 Backend: Running
) else (
    echo 🔴 Backend: Stopped
)

REM Check Frontend status
netstat -an | find "127.0.0.1:5174" >nul
if not errorlevel 1 (
    echo 🟢 Frontend: Running
) else (
    echo 🔴 Frontend: Stopped
)

echo.
echo ========================================
echo 🎛️ Main Menu:
echo ========================================
echo.
echo [1] Start Full System (Backend + Frontend)
echo [2] Start Backend Only
echo [3] Start Frontend Only
echo [4] Stop All Services
echo [5] System Health Check
echo [6] Open Swagger UI
echo [7] Open Frontend Browser
echo [8] View Logs
echo [9] Clean System
echo [0] Exit
echo.
echo ========================================
set /p choice="Choose option (0-9): "
echo ========================================

if "%choice%"=="1" goto START_ALL
if "%choice%"=="2" goto START_BACKEND
if "%choice%"=="3" goto START_FRONTEND
if "%choice%"=="4" goto STOP_ALL
if "%choice%"=="5" goto HEALTH_CHECK
if "%choice%"=="6" goto OPEN_SWAGGER
if "%choice%"=="7" goto OPEN_FRONTEND
if "%choice%"=="8" goto VIEW_LOGS
if "%choice%"=="9" goto CLEANUP
if "%choice%"=="0" goto EXIT

echo ❌ Invalid choice! Please try again.
timeout /t 2 /nobreak >nul
goto MENU

:START_ALL
echo.
echo 🚀 Starting Full System...
call .venv\Scripts\activate.bat
start /b "" python backend\main.py --port 5000 >logs\backend.log 2>&1
echo ⏳ Starting Backend...
timeout /t 3 /nobreak >nul
cd frontend\electron-app
start /b "" npm run dev >..\..\logs\frontend.log 2>&1
cd ..\..
echo ⏳ Starting Frontend...
timeout /t 5 /nobreak >nul
echo ✅ System started successfully!
echo.
echo 📱 Available at:
echo    • API: http://127.0.0.1:5000
echo    • Swagger: http://127.0.0.1:5000/docs
echo    • Frontend: http://127.0.0.1:5174
pause
goto MENU

:START_BACKEND
echo.
echo 🔵 Starting Backend Only...
call .venv\Scripts\activate.bat
start /b "" python backend\main.py --port 5000 >logs\backend.log 2>&1
echo ⏳ Initializing...
timeout /t 5 /nobreak >nul
echo ✅ Backend started!
echo 📱 Available at: http://127.0.0.1:5000
pause
goto MENU

:START_FRONTEND
echo.
echo 🌐 Starting Frontend Only...
cd frontend\electron-app
start /b "" npm run dev >..\..\logs\frontend.log 2>&1
cd ..\..
echo ⏳ Initializing...
timeout /t 8 /nobreak >nul
echo ✅ Frontend started!
echo 📱 Available at: http://127.0.0.1:5174
pause
goto MENU

:STOP_ALL
echo.
echo 🛑 Stopping all services...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im electron.exe >nul 2>&1
echo ✅ All services stopped!
pause
goto MENU

:HEALTH_CHECK
echo.
echo 🔍 Running system health check...
call scripts\utils\health-check.bat
goto MENU

:OPEN_SWAGGER
echo.
echo 🌐 Opening Swagger UI...
start http://127.0.0.1:5000/docs
echo ✅ Swagger UI opened in browser
pause
goto MENU

:OPEN_FRONTEND
echo.
echo 🌐 Opening Frontend...
start http://127.0.0.1:5174
echo ✅ Frontend opened in browser
pause
goto MENU

:VIEW_LOGS
cls
echo.
echo 📋 System Logs:
echo ========================================
echo.
echo === Backend Logs ===
if exist "logs\backend.log" (
    type logs\backend.log | more
) else (
    echo No backend logs available
)
echo.
echo === Frontend Logs ===
if exist "logs\frontend.log" (
    type logs\frontend.log | more
) else (
    echo No frontend logs available
)
echo.
pause
goto MENU

:CLEANUP
echo.
echo 🧹 Running system cleanup...
call scripts\utils\cleanup.bat
goto MENU

:EXIT
echo.
echo 👋 Exiting Audio Chat Studio Terminal...
echo.
echo Would you like to stop running services? (y/n)
set /p stop="Choose: "
if /i "%stop%"=="y" (
    taskkill /f /im python.exe >nul 2>&1
    taskkill /f /im node.exe >nul 2>&1
    taskkill /f /im electron.exe >nul 2>&1
    echo ✅ Services stopped
)
echo.
echo 🎵 Thank you for using Audio Chat Studio!
timeout /t 2 /nobreak >nul
exit