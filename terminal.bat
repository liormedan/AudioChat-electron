@echo off
chcp 65001 >nul
title Audio Chat Studio Terminal

:MENU
cls
echo.
echo 🎵 Audio Chat Studio - Terminal 🎵
echo.

REM Quick status check
python -c "import requests; requests.get('http://127.0.0.1:5000/', timeout=1)" >nul 2>&1
if not errorlevel 1 (
    echo 🟢 Backend: Running
) else (
    echo 🔴 Backend: Stopped
)

netstat -an | find "127.0.0.1:5174" >nul
if not errorlevel 1 (
    echo 🟢 Frontend: Running
) else (
    echo 🔴 Frontend: Stopped
)

echo.
echo [1] Start All  [2] Stop All   [3] Swagger UI  [4] Frontend
echo [5] Logs       [6] Cleanup    [7] Health      [0] Exit
echo.
set /p c="Choose: "

if "%c%"=="1" (
    call .venv\Scripts\activate.bat
    start /b "" python backend\main.py --port 5000 >logs\backend.log 2>&1
    timeout /t 3 /nobreak >nul
    cd frontend\electron-app && start /b "" npm run dev >..\..\logs\frontend.log 2>&1 && cd ..\..
    echo ✅ System started!
    timeout /t 2 /nobreak >nul
)
if "%c%"=="2" (
    taskkill /f /im python.exe /im node.exe /im electron.exe >nul 2>&1
    echo ✅ System stopped!
    timeout /t 2 /nobreak >nul
)
if "%c%"=="3" start http://127.0.0.1:5000/docs
if "%c%"=="4" start http://127.0.0.1:5174
if "%c%"=="5" (
    cls
    echo === Logs ===
    if exist "logs\backend.log" type logs\backend.log | more
    pause
)
if "%c%"=="6" call scripts\utils\cleanup.bat
if "%c%"=="7" call scripts\utils\health-check.bat
if "%c%"=="0" exit

goto MENU