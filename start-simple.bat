@echo off
title Audio Chat Studio

echo Starting Audio Chat Studio...

REM Activate Python environment
call .venv\Scripts\activate.bat

REM Start Backend
echo Starting Backend...
start "Backend" cmd /k "call .venv\Scripts\activate.bat && python backend\main.py"

REM Wait and start Frontend
timeout /t 3 /nobreak >nul
echo Starting Frontend...
cd frontend\electron-app
start "Frontend" cmd /k "npm run dev"
cd ..\..

REM Open browser
timeout /t 5 /nobreak >nul
start http://127.0.0.1:5174

echo.
echo Audio Chat Studio is starting!
echo Check the opened windows and browser.
echo.
echo To stop: Close the Backend and Frontend windows
echo or use the Terminal page in the app.