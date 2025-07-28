@echo off
chcp 65001 >nul
title Audio Chat Studio - Complete System

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    הפעלת מערכת מלאה
echo ========================================
echo.

REM Check virtual environment
if not exist ".venv" (
    echo ❌ Virtual environment לא נמצא!
    echo הרץ: scripts\setup\install_dependencies.bat
    pause
    exit /b 1
)

REM Check node_modules
if not exist "electron-app\node_modules" (
    echo ❌ Node modules לא נמצאו!
    echo מתקין dependencies...
    cd electron-app
    npm install
    cd ..
    echo ✅ Dependencies הותקנו
)

echo 🚀 מפעיל שרתים...
echo.

REM Create data directories
if not exist "data\uploads" mkdir data\uploads
if not exist "logs" mkdir logs

echo 🔵 מפעיל שרת API פשוט (פורט 5000)...
start "Simple API Server" cmd /k "call .venv\Scripts\activate.bat && cd backend\api && python simple_main.py"

timeout /t 3 /nobreak >nul

echo 🟢 מפעיל ממשק ניהול פשוט (פורט 5001)...
start "Simple Admin Interface" cmd /k "call .venv\Scripts\activate.bat && cd backend\admin && python simple_main.py"

timeout /t 3 /nobreak >nul

echo 🟡 מפעיל אפליקציית Electron (פורט 3000)...
start "Electron App" cmd /k "cd electron-app && npm start"

echo.
echo ✅ כל השרתים הופעלו!
echo.
echo 📱 ממשקים זמינים:
echo    • API פשוט:      http://127.0.0.1:5000
echo    • Swagger UI:    http://127.0.0.1:5000/docs
echo    • ממשק ניהול:    http://127.0.0.1:5001
echo    • אפליקציה:      http://127.0.0.1:3000
echo.

echo ⏳ ממתין 10 שניות ואז פותח דפדפנים...
timeout /t 10 /nobreak >nul

echo 🌐 פותח דפדפנים...
start http://127.0.0.1:5001
timeout /t 2 /nobreak >nul
start http://127.0.0.1:5000/docs
timeout /t 2 /nobreak >nul
start http://127.0.0.1:3000

echo.
echo 🎉 המערכת המלאה פועלת!
echo.
echo 💡 טיפים:
echo    • השתמש בSwagger UI לבדיקת API
echo    • ממשק הניהול מציג סטטוס בזמן אמת
echo    • האפליקציה תיפתח בדפדפן או בחלון Electron
echo.
echo לעצירה: Ctrl+C בכל חלון או סגור את החלונות
pause