@echo off
chcp 65001 >nul
title Audio Chat Studio - Health Check

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    בדיקת בריאות המערכת
echo ========================================
echo.

REM Initialize status variables
set PYTHON_OK=0
set VENV_OK=0
set BACKEND_OK=0
set FRONTEND_OK=0
set PORTS_OK=0
set DEPS_OK=0

echo 🔍 בודק רכיבי המערכת...
echo.

REM Check Python
echo 🐍 בודק Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python לא נמצא במערכת
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Python זמין: גרסה !PYTHON_VERSION!
    set PYTHON_OK=1
)

REM Check Virtual Environment
echo 🔧 בודק Virtual Environment...
if exist ".venv" (
    echo ✅ Virtual Environment קיים
    set VENV_OK=1
    
    REM Activate and check dependencies
    call .venv\Scripts\activate.bat >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Virtual Environment פעיל
        
        REM Check key dependencies
        echo 📦 בודק dependencies עיקריים...
        python -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)" 2>nul
        if not errorlevel 1 set /a DEPS_OK+=1
        
        python -c "import uvicorn; print('✅ Uvicorn:', uvicorn.__version__)" 2>nul
        if not errorlevel 1 set /a DEPS_OK+=1
        
        python -c "import librosa; print('✅ Librosa:', librosa.__version__)" 2>nul
        if not errorlevel 1 (
            set /a DEPS_OK+=1
        ) else (
            echo ⚠️ Librosa לא זמין
        )
        
        python -c "import soundfile; print('✅ SoundFile:', soundfile.__version__)" 2>nul
        if not errorlevel 1 (
            set /a DEPS_OK+=1
        ) else (
            echo ⚠️ SoundFile לא זמין
        )
        
        python -c "import pydub; print('✅ Pydub:', pydub.__version__)" 2>nul
        if not errorlevel 1 (
            set /a DEPS_OK+=1
        ) else (
            echo ⚠️ Pydub לא זמין
        )
    ) else (
        echo ❌ לא ניתן להפעיל Virtual Environment
    )
) else (
    echo ❌ Virtual Environment לא קיים
)

REM Check Backend
echo 🔵 בודק Backend...
if %VENV_OK%==1 (
    python -c "from backend.api.main import create_app; print('✅ Backend API נטען בהצלחה')" 2>nul
    if not errorlevel 1 (
        echo ✅ Backend מוכן להפעלה
        set BACKEND_OK=1
    ) else (
        echo ❌ Backend לא נטען כראוי
    )
) else (
    echo ⚠️ לא ניתן לבדוק Backend (Virtual Environment לא זמין)
)

REM Check if Backend is running
echo 🌐 בודק אם Backend רץ...
python -c "import requests; r=requests.get('http://127.0.0.1:5000/', timeout=3); print('✅ Backend רץ על פורט 5000')" 2>nul
if not errorlevel 1 (
    echo ✅ Backend פעיל ומגיב
    
    REM Test API endpoints
    echo 🔗 בודק API endpoints...
    python -c "import requests; r=requests.get('http://127.0.0.1:5000/docs', timeout=3); print('✅ Swagger UI זמין')" 2>nul
    if not errorlevel 1 (
        echo ✅ Swagger UI פעיל
    ) else (
        echo ⚠️ Swagger UI לא מגיב
    )
) else (
    echo ⚠️ Backend לא רץ כרגע
)

REM Check Node.js and Frontend
echo 🌐 בודק Frontend...
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Node.js לא נמצא (Frontend לא יעבוד)
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo ✅ Node.js זמין: גרסה !NODE_VERSION!
    
    if exist "frontend\electron-app\package.json" (
        echo ✅ Frontend project קיים
        
        if exist "frontend\electron-app\node_modules" (
            echo ✅ Frontend dependencies מותקנים
            set FRONTEND_OK=1
        ) else (
            echo ⚠️ Frontend dependencies לא מותקנים
        )
        
        if exist "frontend\electron-app\dist" (
            echo ✅ Production build קיים
        ) else (
            echo ⚠️ Production build לא קיים
        )
    ) else (
        echo ❌ Frontend project לא נמצא
    )
)

REM Check ports availability
echo 🔌 בודק זמינות פורטים...
netstat -an | find "127.0.0.1:5000" >nul
if errorlevel 1 (
    echo ✅ פורט 5000 זמין
    set /a PORTS_OK+=1
) else (
    echo ⚠️ פורט 5000 תפוס
)

netstat -an | find "127.0.0.1:5001" >nul
if errorlevel 1 (
    echo ✅ פורט 5001 זמין
    set /a PORTS_OK+=1
) else (
    echo ⚠️ פורט 5001 תפוס
)

netstat -an | find "127.0.0.1:5174" >nul
if errorlevel 1 (
    echo ✅ פורט 5174 זמין (Vite)
    set /a PORTS_OK+=1
) else (
    echo ⚠️ פורט 5174 תפוס (Vite)
)

REM Check directories
echo 📁 בודק תיקיות...
if exist "data" (
    echo ✅ תיקיית data קיימת
    if exist "data\uploads" echo ✅ data\uploads קיימת
    if exist "data\processed" echo ✅ data\processed קיימת
    if exist "data\temp" echo ✅ data\temp קיימת
    if exist "data\cache" echo ✅ data\cache קיימת
) else (
    echo ⚠️ תיקיית data לא קיימת
)

if exist "logs" (
    echo ✅ תיקיית logs קיימת
    if exist "logs\api" echo ✅ logs\api קיימת
    if exist "logs\system" echo ✅ logs\system קיימת
) else (
    echo ⚠️ תיקיית logs לא קיימת
)

echo.
echo ========================================
echo           📊 סיכום בדיקת בריאות
echo ========================================
echo.

REM Calculate overall health score
set /a TOTAL_SCORE=0
if %PYTHON_OK%==1 set /a TOTAL_SCORE+=1
if %VENV_OK%==1 set /a TOTAL_SCORE+=1
if %BACKEND_OK%==1 set /a TOTAL_SCORE+=1
if %FRONTEND_OK%==1 set /a TOTAL_SCORE+=1
if %DEPS_OK% GEQ 3 set /a TOTAL_SCORE+=1

echo 🎯 ציון כללי: %TOTAL_SCORE%/5
echo.

if %TOTAL_SCORE% GEQ 4 (
    echo ✅ המערכת במצב טוב!
    echo 🚀 ניתן להפעיל את המערכת
) else if %TOTAL_SCORE% GEQ 2 (
    echo ⚠️ המערכת במצב חלקי
    echo 🔧 יש בעיות שדורשות תיקון
) else (
    echo ❌ המערכת במצב לא תקין
    echo 🛠️ נדרש תיקון לפני הפעלה
)

echo.
echo 💡 המלצות:
if %PYTHON_OK%==0 echo    • התקן Python 3.8+
if %VENV_OK%==0 echo    • הרץ scripts\setup.bat
if %BACKEND_OK%==0 echo    • בדוק dependencies של Backend
if %FRONTEND_OK%==0 echo    • הרץ npm install בתיקיית Frontend
if %DEPS_OK% LSS 3 echo    • הרץ pip install -r requirements.txt

echo.
echo 🛠️ פקודות שימושיות:
echo    • התקנה מלאה:     scripts\setup.bat
echo    • הפעלה רגילה:     scripts\start.bat
echo    • מצב פיתוח:       scripts\start-dev.bat
echo    • מצב ייצור:       scripts\start-prod.bat
echo    • עצירת המערכת:    scripts\stop.bat
echo.
pause