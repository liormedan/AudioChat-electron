@echo off
chcp 65001 >nul
title Audio Chat Studio - Terminal Control Center

:MAIN_MENU
cls
echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    Terminal Control Center
echo ========================================
echo.

REM Check system status
call :CHECK_STATUS

echo.
echo 🎛️ Main Menu:
echo.
echo [1] Start Full System (Backend + Frontend)
echo [2] Start Backend Only
echo [3] Start Frontend Only  
echo [4] Stop All Services
echo [5] System Health Check
echo [6] Open Swagger UI (API Management)
echo [7] Open Frontend in Browser
echo [8] Clean Temporary Files
echo [9] View Logs
echo [0] Exit
echo.
set /p choice="Choose option (0-9): "

if "%choice%"=="1" goto START_ALL
if "%choice%"=="2" goto START_BACKEND
if "%choice%"=="3" goto START_FRONTEND
if "%choice%"=="4" goto STOP_ALL
if "%choice%"=="5" goto HEALTH_CHECK
if "%choice%"=="6" goto OPEN_SWAGGER
if "%choice%"=="7" goto OPEN_FRONTEND
if "%choice%"=="8" goto CLEANUP
if "%choice%"=="9" goto VIEW_LOGS
if "%choice%"=="0" goto EXIT

echo ❌ Invalid choice!
timeout /t 2 /nobreak >nul
goto MAIN_MENU

:CHECK_STATUS
echo 📊 System Status:
REM Check if backend is running
python -c "import requests; requests.get('http://127.0.0.1:5000/', timeout=2)" >nul 2>&1
if not errorlevel 1 (
    echo    🔵 Backend: Running ✅
    set BACKEND_STATUS=RUNNING
) else (
    echo    🔵 Backend: Stopped ❌
    set BACKEND_STATUS=STOPPED
)

REM Check if frontend port is in use
netstat -an | find "127.0.0.1:5174" >nul
if not errorlevel 1 (
    echo    🌐 Frontend: Running ✅
    set FRONTEND_STATUS=RUNNING
) else (
    echo    🌐 Frontend: Stopped ❌
    set FRONTEND_STATUS=STOPPED
)
goto :eof

:START_ALL
echo.
echo 🚀 Starting Full System...
echo.

REM Activate virtual environment
if not exist ".venv" (
    echo ❌ Virtual environment not found! Run scripts\setup.bat
    pause
    goto MAIN_MENU
)

call .venv\Scripts\activate.bat

REM Start Backend in background
echo 🔵 Starting Backend API...
start /b "" python backend\main.py --port 5000 >logs\backend_output.log 2>&1

REM Wait for backend
echo ⏳ Waiting for Backend initialization...
timeout /t 5 /nobreak >nul

REM Check if Node.js is available and start Frontend
where node >nul 2>&1
if not errorlevel 1 (
    if exist "frontend\electron-app\package.json" (
        echo 🌐 Starting Frontend...
        cd frontend\electron-app
        start /b "" npm run dev >..\..\logs\frontend_output.log 2>&1
        cd ..\..
    )
) else (
    echo ⚠️ Node.js not found, starting Backend only
)

echo ⏳ Waiting for services initialization...
timeout /t 8 /nobreak >nul

echo ✅ System started successfully!
echo.
echo 📱 Quick Links:
echo    • API Server: http://127.0.0.1:5000
echo    • Swagger UI: http://127.0.0.1:5000/docs
echo    • Frontend: http://127.0.0.1:5174
echo.
pause
goto MAIN_MENU

:START_BACKEND
echo.
echo 🔵 Starting Backend Only...
call .venv\Scripts\activate.bat
start /b "" python backend\main.py --port 5000 >logs\backend_output.log 2>&1
echo ⏳ Waiting for initialization...
timeout /t 5 /nobreak >nul
echo ✅ Backend started!
pause
goto MAIN_MENU

:START_FRONTEND
echo.
echo 🌐 Starting Frontend Only...
if exist "frontend\electron-app\package.json" (
    cd frontend\electron-app
    start /b "" npm run dev >..\..\logs\frontend_output.log 2>&1
    cd ..\..
    echo ⏳ Waiting for initialization...
    timeout /t 8 /nobreak >nul
    echo ✅ Frontend started!
) else (
    echo ❌ Frontend not found!
)
pause
goto MAIN_MENU

:STOP_ALL
echo.
echo 🛑 Stopping system...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im electron.exe >nul 2>&1
echo ✅ System stopped!
pause
goto MAIN_MENU

:HEALTH_CHECK
echo.
echo 🔍 Running health check...
call scripts\utils\health-check.bat
goto MAIN_MENU

:OPEN_SWAGGER
echo.
echo 🌐 Opening Swagger UI...
start http://127.0.0.1:5000/docs
echo ✅ Swagger UI opened in browser
pause
goto MAIN_MENU

:OPEN_FRONTEND
echo.
echo 🌐 Opening Frontend...
start http://127.0.0.1:5174
echo ✅ Frontend opened in browser
pause
goto MAIN_MENU

:CLEANUP
echo.
echo 🧹 Running cleanup...
call scripts\utils\cleanup.bat
goto MAIN_MENU

:VIEW_LOGS
cls
echo.
echo 📋 Recent Logs:
echo.
echo === Backend Logs ===
if exist "logs\backend_output.log" (
    type logs\backend_output.log | more
) else (
    echo No Backend logs available
)
echo.
echo === Frontend Logs ===
if exist "logs\frontend_output.log" (
    type logs\frontend_output.log | more
) else (
    echo No Frontend logs available
)
echo.
pause
goto MAIN_MENU

:EXIT
echo.
echo 👋 Exiting system...
echo Would you like to stop running services? (y/n)
set /p stop_services="Choose: "
if /i "%stop_services%"=="y" (
    taskkill /f /im python.exe >nul 2>&1
    taskkill /f /im node.exe >nul 2>&1
    taskkill /f /im electron.exe >nul 2>&1
    echo ✅ Services stopped
)
echo.
echo 🎵 Thank you for using Audio Chat Studio!
timeout /t 3 /nobreak >nul
exit