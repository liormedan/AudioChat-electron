@echo off
chcp 65001 >nul
title Audio Chat Studio - אפליקציה בלבד

echo.
echo ========================================
echo    🟡 Audio Chat Studio App 🟡
echo    הפעלת אפליקציית Electron בלבד
echo ========================================
echo.

REM Check if node_modules exists
if not exist "electron-app\node_modules" (
    echo ❌ Node modules לא נמצאו!
    echo מתקין dependencies...
    cd electron-app
    npm install
    cd ..
    echo ✅ Dependencies הותקנו
)

echo.
echo 🚀 מפעיל אפליקציית Electron...

REM Create logs directory
if not exist "logs" mkdir logs

REM Start Electron app
echo 🟡 אפליקציה פועלת על פורט 3000...
echo 📋 לוג נשמר ב-logs\electron_app.log
echo.
echo 📱 אפליקציה זמינה:
echo    • אפליקציה:      http://127.0.0.1:3000
echo.
echo לעצירה: Ctrl+C
echo.

cd electron-app
npm start

pause