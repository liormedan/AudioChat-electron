@echo off
title Audio Chat Studio

echo מפעיל Audio Chat Studio...

REM Activate Python environment
call .venv\Scripts\activate.bat

REM Start Backend
echo מפעיל Backend...
start "Backend" cmd /k "call .venv\Scripts\activate.bat && python backend\main.py"

REM Wait and start Frontend
timeout /t 3 /nobreak >nul
echo מפעיל Frontend...
cd frontend\electron-app
start "Frontend" cmd /k "npm run dev"
cd ..\..

REM Open browser
timeout /t 5 /nobreak >nul
start http://127.0.0.1:5000/docs

echo.
echo המערכת הופעלה! בדוק את החלונות שנפתחו.
pause