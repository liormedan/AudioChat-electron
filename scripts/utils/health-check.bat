@echo off
chcp 65001 >nul
title Audio Chat Studio - Health Check

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    בדיקת בריאות המערכת
echo ========================================
echo.

set ERRORS=0
set WARNINGS=0

REM Check Python installation
echo 🔍 בודק התקנת Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python לא נמצא במערכת!
    set /a ERRORS+=1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Python זמין: גרסה !PYTHON_VERSION!
)

REM Check Node.js installation
echo 🔍 בודק התקנת Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Node.js לא נמצא במערכת!
    echo    Frontend לא יוכל לעבוד
    set /a WARNINGS+=1
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo ✅ Node.js זמין: גרסה !NODE_VERSION!
)

REM Check Virtual Environment
echo 🔍 בודק Virtual Environment...
if exist ".venv" (
    echo ✅ Virtual Environment קיים
    
    REM Check if venv can be activated
    call .venv\Scripts\activate.bat >nul 2>&1
    if errorlevel 1 (
        echo ❌ לא ניתן להפעיל Virtual Environment!
        set /a ERRORS+=1
    ) else (
        echo ✅ Virtual Environment פעיל
        
        REM Check Python packages
        echo 🔍 בודק Python packages...
        python -c "import fastapi, uvicorn" >nul 2>&1
        if errorlevel 1 (
            echo ❌ חבילות Python חסרות!
            echo    הרץ: pip install -r requirements.txt
            set /a ERRORS+=1
        ) else (
            echo ✅ חבילות Python זמינות
        )
    )
) else (
    echo ❌ Virtual Environment לא קיים!
    echo    הרץ: scripts\setup.bat
    set /a ERRORS+=1
)

REM Check Backend files
echo 🔍 בודק קבצי Backend...
if exist "backend\main.py" (
    echo ✅ backend\main.py קיים
) else (
    echo ❌ backend\main.py לא נמצא!
    set /a ERRORS+=1
)

if exist "backend\api\main.py" (
    echo ✅ backend\api\main.py קיים
) else (
    echo ❌ backend\api\main.py לא נמצא!
    set /a ERRORS+=1
)

REM Check Frontend files
echo 🔍 בודק קבצי Frontend...
if exist "frontend\electron-app\package.json" (
    echo ✅ frontend\electron-app\package.json קיים
    
    if exist "frontend\electron-app\node_modules" (
        echo ✅ Frontend dependencies מותקנים
    ) else (
        echo ⚠️ Frontend dependencies לא מותקנים!
        echo    הרץ: cd frontend\electron-app && npm install
        set /a WARNINGS+=1
    )
) else (
    echo ⚠️ frontend\electron-app\package.json לא נמצא!
    set /a WARNINGS+=1
)

REM Check required directories
echo 🔍 בודק תיקיות נדרשות...
set REQUIRED_DIRS=data data\uploads data\processed data\temp data\cache logs logs\api logs\system

for %%d in (%REQUIRED_DIRS%) do (
    if exist "%%d" (
        echo ✅ %%d קיים
    ) else (
        echo ⚠️ %%d לא קיים, יוצר...
        mkdir "%%d" >nul 2>&1
        if exist "%%d" (
            echo ✅ %%d נוצר בהצלחה
        ) else (
            echo ❌ לא ניתן ליצור %%d!
            set /a ERRORS+=1
        )
    )
)

REM Check port availability
echo 🔍 בודק זמינות פורטים...
netstat -an | find "127.0.0.1:5000" >nul
if not errorlevel 1 (
    echo ⚠️ פורט 5000 תפוס!
    echo    יש תהליך שרץ על הפורט
    set /a WARNINGS+=1
) else (
    echo ✅ פורט 5000 זמין
)

netstat -an | find "127.0.0.1:5001" >nul
if not errorlevel 1 (
    echo ⚠️ פורט 5001 תפוס!
    echo    יש תהליך שרץ על הפורט
    set /a WARNINGS+=1
) else (
    echo ✅ פורט 5001 זמין
)

netstat -an | find "127.0.0.1:5174" >nul
if not errorlevel 1 (
    echo ⚠️ פורט 5174 תפוס!
    echo    יש תהליך שרץ על הפורט
    set /a WARNINGS+=1
) else (
    echo ✅ פורט 5174 זמין
)

REM Check if services are running
echo 🔍 בודק שירותים פעילים...
python -c "import requests; requests.get('http://127.0.0.1:5000/', timeout=2)" >nul 2>&1
if not errorlevel 1 (
    echo ✅ Backend API רץ על פורט 5000
    
    REM Test API endpoints
    echo 🔍 בודק API endpoints...
    python -c "import requests; r=requests.get('http://127.0.0.1:5000/docs', timeout=2); print('✅ Swagger UI זמין') if r.status_code==200 else print('⚠️ Swagger UI לא זמין')" 2>nul
    
) else (
    echo ⚠️ Backend API לא רץ
    echo    השירות לא פעיל או לא מגיב
)

python -c "import requests; requests.get('http://127.0.0.1:5001/', timeout=2)" >nul 2>&1
if not errorlevel 1 (
    echo ✅ Admin Interface רץ על פורט 5001
) else (
    echo ⚠️ Admin Interface לא רץ
)

REM Check system resources
echo 🔍 בודק משאבי מערכת...
for /f "tokens=2 delims=:" %%i in ('wmic OS get TotalVisibleMemorySize /value ^| find "="') do set TOTAL_MEM=%%i
for /f "tokens=2 delims=:" %%i in ('wmic OS get FreePhysicalMemory /value ^| find "="') do set FREE_MEM=%%i

if defined TOTAL_MEM if defined FREE_MEM (
    set /a MEM_USAGE_PCT=100-(!FREE_MEM!*100/!TOTAL_MEM!)
    echo ✅ זיכרון: !MEM_USAGE_PCT!%% בשימוש
    
    if !MEM_USAGE_PCT! GTR 90 (
        echo ⚠️ זיכרון גבוה! ייתכנו בעיות ביצועים
        set /a WARNINGS+=1
    )
) else (
    echo ⚠️ לא ניתן לבדוק שימוש בזיכרון
)

REM Check disk space
for /f "tokens=3" %%i in ('dir /-c ^| find "bytes free"') do set FREE_SPACE=%%i
if defined FREE_SPACE (
    set /a FREE_GB=!FREE_SPACE!/1073741824
    echo ✅ מקום פנוי בדיסק: !FREE_GB! GB
    
    if !FREE_GB! LSS 1 (
        echo ❌ מקום דיסק נמוך מאוד!
        set /a ERRORS+=1
    ) else if !FREE_GB! LSS 5 (
        echo ⚠️ מקום דיסק נמוך!
        set /a WARNINGS+=1
    )
) else (
    echo ⚠️ לא ניתן לבדוק מקום דיסק
)

echo.
echo ========================================
echo           📊 סיכום בדיקת בריאות
echo ========================================
echo.

if %ERRORS% EQU 0 if %WARNINGS% EQU 0 (
    echo 🎉 המערכת תקינה לחלוטין!
    echo ✅ כל הבדיקות עברו בהצלחה
    echo.
    echo 🚀 המערכת מוכנה להפעלה:
    echo    • הפעלה רגילה:     scripts\start.bat
    echo    • מצב פיתוח:       scripts\start-dev.bat
    echo    • מצב ייצור:       scripts\start-prod.bat
) else (
    if %ERRORS% GTR 0 (
        echo ❌ נמצאו %ERRORS% שגיאות קריטיות!
        echo 🔧 יש לתקן את השגיאות לפני הפעלת המערכת
    )
    
    if %WARNINGS% GTR 0 (
        echo ⚠️ נמצאו %WARNINGS% אזהרות
        echo 💡 המערכת תעבוד אבל עם מגבלות
    )
    
    echo.
    echo 🛠️ פעולות מומלצות:
    if %ERRORS% GTR 0 (
        echo    • הרץ: scripts\setup.bat
        echo    • בדוק התקנת Python ו-dependencies
    )
    if %WARNINGS% GTR 0 (
        echo    • התקן Node.js לתמיכה מלאה בFrontend
        echo    • הרץ: cd frontend\electron-app && npm install
    )
)

echo.
echo 📋 פקודות שימושיות:
echo    • התקנה מחדש:      scripts\setup.bat
echo    • בדיקה חוזרת:     scripts\utils\health-check.bat
echo    • עצירת שירותים:   scripts\stop.bat
echo.
pause