@echo off
chcp 65001 >nul
title Audio Chat Studio - בדיקת סטטוס

echo.
echo ========================================
echo    📊 Audio Chat Studio Status 📊
echo    בדיקת סטטוס כל השרתים
echo ========================================
echo.

echo 🔍 בודק פורטים פעילים...
echo.

REM Check port 5000 (API Server)
netstat -an | findstr :5000 | findstr LISTENING >nul
if errorlevel 1 (
    echo 🔴 שרת API (פורט 5000): לא פעיל
) else (
    echo 🟢 שרת API (פורט 5000): פעיל
    echo    📱 http://127.0.0.1:5000
    echo    📚 http://127.0.0.1:5000/docs
)

echo.

REM Check port 5001 (Admin Interface)
netstat -an | findstr :5001 | findstr LISTENING >nul
if errorlevel 1 (
    echo 🔴 ממשק ניהול (פורט 5001): לא פעיל
) else (
    echo 🟢 ממשק ניהול (פורט 5001): פעיל
    echo    📱 http://127.0.0.1:5001
)

echo.

REM Check port 3000 (Electron App)
netstat -an | findstr :3000 | findstr LISTENING >nul
if errorlevel 1 (
    echo 🔴 אפליקציית Electron (פורט 3000): לא פעילה
) else (
    echo 🟢 אפליקציית Electron (פורט 3000): פעילה
    echo    📱 http://127.0.0.1:3000
)

echo.
echo 📋 תהליכים פעילים:
echo.

REM Show Python processes
echo 🐍 תהליכי Python:
tasklist | findstr python.exe
if errorlevel 1 echo    אין תהליכי Python פעילים

echo.

REM Show Node processes
echo 📦 תהליכי Node.js:
tasklist | findstr node.exe
if errorlevel 1 echo    אין תהליכי Node.js פעילים

echo.

REM Show Electron processes
echo ⚡ תהליכי Electron:
tasklist | findstr electron.exe
if errorlevel 1 echo    אין תהליכי Electron פעילים

echo.
echo 📁 בדיקת תיקיות:
if exist "uploads" (
    echo ✅ תיקיית uploads קיימת
    dir uploads /b | find /c /v "" > temp_count.txt
    set /p file_count=<temp_count.txt
    del temp_count.txt
    echo    📄 קבצים: !file_count!
) else (
    echo ❌ תיקיית uploads לא קיימת
)

if exist "logs" (
    echo ✅ תיקיית logs קיימת
) else (
    echo ❌ תיקיית logs לא קיימת
)

if exist ".venv" (
    echo ✅ Virtual environment קיים
) else (
    echo ❌ Virtual environment לא קיים
)

echo.
echo 🔧 פעולות זמינות:
echo    • start_all.bat - הפעלת כל המערכת
echo    • stop_all.bat - עצירת כל המערכת
echo    • install_dependencies.bat - התקנת תלויות
echo.
pause