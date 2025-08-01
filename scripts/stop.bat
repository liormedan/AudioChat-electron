@echo off
chcp 65001 >nul
title Audio Chat Studio - Stop Services

echo.
echo ========================================
echo    🛑 Audio Chat Studio Stop Services
echo ========================================
echo.

echo 🔍 Stopping Audio Chat Studio services...

REM Stop Backend processes
echo 🔵 Stopping Backend processes...
taskkill /f /fi "windowtitle eq Audio Chat Studio - Backend*" 2>nul
if %ERRORLEVEL%==0 (
    echo ✅ Backend processes stopped
) else (
    echo ⚠️ No Backend processes found
)

REM Stop Frontend processes  
echo 🌐 Stopping Frontend processes...
taskkill /f /fi "windowtitle eq Audio Chat Studio - Frontend*" 2>nul
if %ERRORLEVEL%==0 (
    echo ✅ Frontend processes stopped
) else (
    echo ⚠️ No Frontend processes found
)

REM Stop any remaining Python processes on port 5000
echo 🐍 Stopping Python processes on port 5000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do (
    taskkill /f /pid %%a 2>nul
    if %ERRORLEVEL%==0 echo ✅ Stopped process %%a
)

REM Stop any remaining Node processes on port 5176
echo 📦 Stopping Node processes on port 5176...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5176" ^| find "LISTENING"') do (
    taskkill /f /pid %%a 2>nul
    if %ERRORLEVEL%==0 echo ✅ Stopped process %%a
)

echo.
echo ✅ All Audio Chat Studio services have been stopped
echo.
pause