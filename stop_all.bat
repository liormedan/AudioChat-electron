@echo off
chcp 65001 >nul
title Audio Chat Studio - עצירת כל השרתים

echo.
echo ========================================
echo    🛑 Audio Chat Studio 🛑
echo    עצירת כל השרתים והאפליקציה
echo ========================================
echo.

echo 🔄 מחפש תהליכים פעילים...

REM Kill processes by port
echo 🔵 עוצר שרת API (פורט 5000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do (
    echo עוצר תהליך %%a
    taskkill /PID %%a /F >nul 2>&1
)

echo 🟢 עוצר ממשק ניהול (פורט 5001)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5001 ^| findstr LISTENING') do (
    echo עוצר תהליך %%a
    taskkill /PID %%a /F >nul 2>&1
)

echo 🟡 עוצר אפליקציית Electron (פורט 3000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do (
    echo עוצר תהליך %%a
    taskkill /PID %%a /F >nul 2>&1
)

REM Kill Python processes related to our servers
echo 🐍 עוצר תהליכי Python...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1

REM Kill Node processes
echo 📦 עוצר תהליכי Node.js...
taskkill /F /IM node.exe >nul 2>&1

REM Kill Electron processes
echo ⚡ עוצר תהליכי Electron...
taskkill /F /IM electron.exe >nul 2>&1

echo.
echo ✅ כל השרתים נעצרו!
echo.

REM Clean up temporary files
echo 🧹 מנקה קבצים זמניים...
if exist "temp" rmdir /s /q temp >nul 2>&1
if exist "__pycache__" rmdir /s /q __pycache__ >nul 2>&1

echo ✅ ניקוי הושלם!
echo.
pause