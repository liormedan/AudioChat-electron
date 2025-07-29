@echo off
title Audio Chat Studio

echo Starting Audio Chat Studio...

call .venv\Scripts\activate.bat

start /min "" python backend\main.py --port 5000
timeout /t 3 /nobreak >nul

cd frontend\electron-app
start /min "" npm run dev
cd ..\..

timeout /t 8 /nobreak >nul
start http://127.0.0.1:5174

echo Audio Chat Studio is running!
echo Open: http://127.0.0.1:5174
pause