@echo off
chcp 65001 >nul
title Audio Chat Studio - בדיקת בריאות

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    בדיקת בריאות המערכת
echo ========================================
echo.

REM Check if virtual environment exists
echo 🔍 בודק סביבת Python...
if exist ".venv" (
    echo ✅ Virtual environment קיים
) else (
    echo ❌ Virtual environment לא נמצא
    echo 🔧 הרץ: scripts\setup.bat
)

REM Check Python processes
echo 🔍 בודק תהליכי Python...
tasklist | find "python.exe" >nul
if not errorlevel 1 (
    echo ✅ תהליכי Python רצים
) else (
    echo ⚠️ אין תהליכי Python פעילים
)

REM Check Node.js processes
echo 🔍 בודק תהליכי Node.js...
tasklist | find "node.exe" >nul
if not errorlevel 1 (
    echo ✅ תהליכי Node.js רצים
) else (
    echo ⚠️ אין תהליכי Node.js פעילים
)

REM Check Electron processes
echo 🔍 בודק תהליכי Electron...
tasklist | find "electron.exe" >nul
if not errorlevel 1 (
    echo ✅ Electron רץ
) else (
    echo ⚠️ Electron לא רץ
)

REM Check ports
echo 🔍 בודק פורטים...
netstat -an | find "127.0.0.1:5000" >nul
if not errorlevel 1 (
    echo ✅ פורט 5000 (Backend) פעיל
) else (
    echo ❌ פורט 5000 (Backend) לא פעיל
)

netstat -an | find "127.0.0.1:5174" >nul
if not errorlevel 1 (
    echo ✅ פורט 5174 (Frontend Dev) פעיל
) else (
    echo ⚠️ פורט 5174 (Frontend Dev) לא פעיל
)

REM Test backend API
echo 🔍 בודק API Backend...
python -c "import requests; r = requests.get('http://127.0.0.1:5000', timeout=3); print('✅ Backend API מגיב:', r.status_code)" 2>nul
if errorlevel 1 (
    echo ❌ Backend API לא מגיב
)

REM Test backend health endpoint
echo 🔍 בודק Swagger UI...
python -c "import requests; r = requests.get('http://127.0.0.1:5000/docs', timeout=3); print('✅ Swagger UI זמין')" 2>nul
if errorlevel 1 (
    echo ⚠️ Swagger UI לא זמין
)

echo.
echo 📊 סיכום בדיקת בריאות:
echo.

REM Overall system status
set /a healthy=0
tasklist | find "python.exe" >nul && set /a healthy+=1
netstat -an | find "127.0.0.1:5000" >nul && set /a healthy+=1

if %healthy% geq 2 (
    echo ✅ המערכת תקינה ופועלת
) else if %healthy% geq 1 (
    echo ⚠️ המערכת פועלת חלקית
) else (
    echo ❌ המערכת לא פועלת
)

echo.
echo 🔧 פקודות תיקון:
echo    • הפעלת המערכת:   scripts\start.bat
echo    • הפעלת פיתוח:    scripts\start-dev.bat
echo    • עצירת המערכת:   scripts\stop.bat
echo    • התקנה מחדש:     scripts\setup.bat
echo.
pause