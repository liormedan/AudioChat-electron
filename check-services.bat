@echo off
chcp 65001 >nul
title Audio Chat Studio - Service Status Check

echo.
echo ========================================
echo    🔍 Audio Chat Studio Status Check
echo ========================================
echo.

echo 🔵 Checking Backend (Port 5000)...
curl -s http://127.0.0.1:5000/health >nul 2>&1
if %ERRORLEVEL%==0 (
    echo ✅ Backend is running on http://127.0.0.1:5000
) else (
    echo ❌ Backend is not responding
)

echo.
echo 🌐 Checking Frontend (Port 5174)...
curl -s http://127.0.0.1:5174 >nul 2>&1
if %ERRORLEVEL%==0 (
    echo ✅ Frontend is running on http://127.0.0.1:5174
) else (
    echo ❌ Frontend is not responding
)

echo.
echo 📊 Process Status:
tasklist /fi "windowtitle eq Audio Chat Studio - Backend*" 2>nul | find "cmd.exe" >nul
if %ERRORLEVEL%==0 (
    echo ✅ Backend process found
) else (
    echo ❌ Backend process not found
)

tasklist /fi "windowtitle eq Audio Chat Studio - Frontend*" 2>nul | find "cmd.exe" >nul
if %ERRORLEVEL%==0 (
    echo ✅ Frontend process found
) else (
    echo ❌ Frontend process not found
)

echo.
pause