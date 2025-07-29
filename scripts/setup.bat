@echo off
chcp 65001 >nul
title Audio Chat Studio - Setup & Installation

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    התקנה ראשונית של המערכת
echo ========================================
echo.

REM Check if Python is available
echo 🔍 בודק זמינות Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python לא נמצא במערכת!
    echo.
    echo 📥 אנא התקן Python 3.8 או גרסה חדשה יותר מ:
    echo    https://www.python.org/downloads/
    echo.
    echo לאחר ההתקנה, הפעל מחדש את הסקריפט הזה
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Python נמצא: גרסה !PYTHON_VERSION!
)

REM Check if pip is available
echo 🔍 בודק זמינות pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip לא נמצא!
    echo מנסה להתקין pip...
    python -m ensurepip --upgrade
    if errorlevel 1 (
        echo ❌ התקנת pip נכשלה!
        pause
        exit /b 1
    )
) else (
    echo ✅ pip זמין
)

REM Create virtual environment if it doesn't exist
if exist ".venv" (
    echo ✅ Virtual environment כבר קיים
) else (
    echo 🔧 יוצר Virtual Environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ יצירת Virtual Environment נכשלה!
        pause
        exit /b 1
    )
    echo ✅ Virtual Environment נוצר בהצלחה
)

REM Activate virtual environment
echo 🔄 מפעיל Virtual Environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ לא ניתן להפעיל את Virtual Environment!
    pause
    exit /b 1
)

REM Upgrade pip in virtual environment
echo 🔄 מעדכן pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ⚠️ עדכון pip נכשל, ממשיך בכל זאת...
)

REM Install Python dependencies
echo 📦 מתקין Python dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ התקנת Python dependencies נכשלה!
        echo.
        echo 💡 נסה להריץ ידנית:
        echo    .venv\Scripts\activate.bat
        echo    pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo ✅ Python dependencies הותקנו בהצלחה
) else (
    echo ⚠️ requirements.txt לא נמצא!
    echo מתקין חבילות בסיסיות...
    pip install fastapi uvicorn pydantic python-multipart
    if errorlevel 1 (
        echo ❌ התקנת חבילות בסיסיות נכשלה!
        pause
        exit /b 1
    )
)

REM Check if Node.js is available for frontend
echo.
echo 🔍 בודק זמינות Node.js לפרונטאנד...
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Node.js לא נמצא!
    echo.
    echo 📥 לפיתוח Frontend, התקן Node.js מ:
    echo    https://nodejs.org/
    echo.
    echo המערכת תעבוד גם בלי Node.js (רק Backend)
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo ✅ Node.js נמצא: גרסה !NODE_VERSION!
    
    REM Install frontend dependencies if package.json exists
    if exist "frontend\electron-app\package.json" (
        echo 📦 מתקין Frontend dependencies...
        cd frontend\electron-app
        npm install
        if errorlevel 1 (
            echo ⚠️ התקנת Frontend dependencies נכשלה!
            echo המערכת תעבוד גם בלי Frontend
        ) else (
            echo ✅ Frontend dependencies הותקנו בהצלחה
        )
        cd ..\..
    )
)

REM Create necessary directories
echo 📁 יוצר תיקיות נדרשות...
if not exist "data" mkdir data
if not exist "data\uploads" mkdir data\uploads
if not exist "data\processed" mkdir data\processed
if not exist "data\temp" mkdir data\temp
if not exist "data\cache" mkdir data\cache
if not exist "logs" mkdir logs
if not exist "logs\api" mkdir logs\api
if not exist "logs\system" mkdir logs\system
echo ✅ תיקיות נוצרו בהצלחה

REM Test the installation
echo.
echo 🧪 בודק את ההתקנה...
python -c "import fastapi, uvicorn; print('✅ FastAPI זמין')" 2>nul
if errorlevel 1 (
    echo ❌ בדיקת FastAPI נכשלה!
    pause
    exit /b 1
)

python -c "from backend.api.main import create_app; app = create_app(); print('✅ Backend API זמין')" 2>nul
if errorlevel 1 (
    echo ⚠️ בדיקת Backend API נכשלה, אבל זה עשוי לעבוד בכל זאת
)

echo.
echo ========================================
echo    ✅ ההתקנה הושלמה בהצלחה! ✅
echo ========================================
echo.
echo 🚀 להפעלת המערכת:
echo    • הפעלה רגילה:     scripts\start.bat
echo    • מצב פיתוח:       scripts\start-dev.bat
echo.
echo 🛠️ כלים נוספים:
echo    • עצירת המערכת:    scripts\stop.bat
echo    • בדיקת בריאות:    scripts\utils\health-check.bat
echo.
echo 📚 תיעוד:
echo    • API Documentation: http://127.0.0.1:5000/docs (לאחר הפעלה)
echo    • README.md: מידע כללי על הפרויקט
echo.

REM Ask if user wants to start the system now
echo האם תרצה להפעיל את המערכת עכשיו? (y/n)
set /p choice="בחר: "
if /i "%choice%"=="y" (
    echo.
    echo 🚀 מפעיל את המערכת...
    call scripts\start.bat
) else if /i "%choice%"=="yes" (
    echo.
    echo 🚀 מפעיל את המערכת...
    call scripts\start.bat
) else (
    echo.
    echo 👍 ההתקנה הושלמה. הפעל scripts\start.bat כשתהיה מוכן
    pause
)