@echo off
chcp 65001 >nul
title Audio Chat Studio - Build Script

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    בניית האפליקציה לייצור
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python לא נמצא במערכת!
    echo אנא התקן Python 3.8 או גרסה חדשה יותר
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js לא נמצא במערכת!
    echo אנא התקן Node.js מ: https://nodejs.org/
    pause
    exit /b 1
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo ✅ Node.js נמצא: גרסה !NODE_VERSION!
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment לא נמצא!
    echo.
    echo 🔧 מפעיל התקנה אוטומטית...
    call scripts\setup.bat
    if errorlevel 1 (
        echo ❌ ההתקנה נכשלה!
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔄 מפעיל סביבת Python...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ לא ניתן להפעיל את סביבת Python!
    pause
    exit /b 1
)

echo.
echo 🏗️ מתחיל תהליך הבנייה...
echo.

REM Clean previous builds
echo 🧹 מנקה builds קודמים...
if exist "frontend\electron-app\dist" (
    rmdir /s /q "frontend\electron-app\dist" >nul 2>&1
)
if exist "frontend\electron-app\.vite" (
    rmdir /s /q "frontend\electron-app\.vite" >nul 2>&1
)
if exist "frontend\electron-app\py_build" (
    rmdir /s /q "frontend\electron-app\py_build" >nul 2>&1
)
if exist "frontend\electron-app\release" (
    rmdir /s /q "frontend\electron-app\release" >nul 2>&1
)
echo ✅ ניקוי הושלם

REM Build Backend (Python executable)
echo.
echo 🐍 בונה Backend Python...
if exist "backend\main.py" (
    echo 📦 יוצר executable של Backend...
    
    REM Install PyInstaller if not available
    pip show pyinstaller >nul 2>&1
    if errorlevel 1 (
        echo 📥 מתקין PyInstaller...
        pip install pyinstaller
        if errorlevel 1 (
            echo ❌ התקנת PyInstaller נכשלה!
            pause
            exit /b 1
        )
    )
    
    REM Create backend executable
    mkdir "frontend\electron-app\py_build\dist" >nul 2>&1
    python -m PyInstaller --onefile backend\main.py --distpath frontend\electron-app\py_build\dist --name server_dist --clean
    if errorlevel 1 (
        echo ❌ בניית Backend נכשלה!
        pause
        exit /b 1
    )
    echo ✅ Backend executable נוצר בהצלחה
) else (
    echo ⚠️ backend\main.py לא נמצא, מדלג על בניית Backend
)

REM Build Frontend
echo.
echo 🎨 בונה Frontend...
if exist "frontend\electron-app\package.json" (
    cd frontend\electron-app
    
    REM Install dependencies if needed
    if not exist "node_modules" (
        echo 📦 מתקין Frontend dependencies...
        npm install
        if errorlevel 1 (
            echo ❌ התקנת Frontend dependencies נכשלה!
            cd ..\..
            pause
            exit /b 1
        )
    )
    
    REM Type check
    echo 🔍 בודק TypeScript types...
    npm run type-check
    if errorlevel 1 (
        echo ⚠️ בדיקת TypeScript נכשלה, ממשיך בכל זאת...
    ) else (
        echo ✅ TypeScript types תקינים
    )
    
    REM Lint code
    echo 🔍 בודק איכות קוד...
    npm run lint
    if errorlevel 1 (
        echo ⚠️ בדיקת Lint נכשלה, ממשיך בכל זאת...
    ) else (
        echo ✅ איכות קוד תקינה
    )
    
    REM Build renderer (React app)
    echo 🏗️ בונה Renderer (React)...
    npm run build:renderer
    if errorlevel 1 (
        echo ❌ בניית Renderer נכשלה!
        cd ..\..
        pause
        exit /b 1
    )
    echo ✅ Renderer נבנה בהצלחה
    
    REM Build main process (Electron)
    echo 🏗️ בונה Main Process (Electron)...
    npm run build:main
    if errorlevel 1 (
        echo ❌ בניית Main Process נכשלה!
        cd ..\..
        pause
        exit /b 1
    )
    echo ✅ Main Process נבנה בהצלחה
    
    REM Build preload scripts
    echo 🏗️ בונה Preload Scripts...
    npm run build:preload
    if errorlevel 1 (
        echo ⚠️ בניית Preload Scripts נכשלה, ממשיך בכל זאת...
    ) else (
        echo ✅ Preload Scripts נבנו בהצלחה
    )
    
    cd ..\..
    echo ✅ Frontend נבנה בהצלחה
) else (
    echo ⚠️ frontend\electron-app\package.json לא נמצא, מדלג על בניית Frontend
)

REM Test the build
echo.
echo 🧪 בודק את הבנייה...
if exist "frontend\electron-app\dist\renderer" (
    echo ✅ Renderer build נמצא
) else (
    echo ❌ Renderer build לא נמצא!
)

if exist "frontend\electron-app\dist\main" (
    echo ✅ Main process build נמצא
) else (
    echo ❌ Main process build לא נמצא!
)

if exist "frontend\electron-app\py_build\dist\server_dist.exe" (
    echo ✅ Backend executable נמצא
) else (
    echo ⚠️ Backend executable לא נמצא
)

echo.
echo ========================================
echo    ✅ הבנייה הושלמה בהצלחה! ✅
echo ========================================
echo.
echo 📁 קבצים שנוצרו:
if exist "frontend\electron-app\dist\renderer" (
    echo    • Frontend (React):     frontend\electron-app\dist\renderer\
)
if exist "frontend\electron-app\dist\main" (
    echo    • Main Process:         frontend\electron-app\dist\main\
)
if exist "frontend\electron-app\py_build\dist\server_dist.exe" (
    echo    • Backend Executable:   frontend\electron-app\py_build\dist\server_dist.exe
)
echo.
echo 🚀 להפעלת הבנייה:
echo    • מצב ייצור:            scripts\start-prod.bat
echo    • חבילת Electron:       cd frontend\electron-app && npm run package
echo.
echo 📦 ליצירת installer:
echo    • Windows Installer:    cd frontend\electron-app && npm run package
echo.

REM Ask if user wants to create Electron package
echo האם תרצה ליצור חבילת Electron להפצה? (y/n)
set /p choice="בחר: "
if /i "%choice%"=="y" (
    echo.
    echo 📦 יוצר חבילת Electron...
    cd frontend\electron-app
    npm run package
    if errorlevel 1 (
        echo ❌ יצירת חבילת Electron נכשלה!
        cd ..\..
        pause
        exit /b 1
    )
    echo ✅ חבילת Electron נוצרה בהצלחה!
    echo 📁 מיקום: frontend\electron-app\release\
    cd ..\..
) else if /i "%choice%"=="yes" (
    echo.
    echo 📦 יוצר חבילת Electron...
    cd frontend\electron-app
    npm run package
    if errorlevel 1 (
        echo ❌ יצירת חבילת Electron נכשלה!
        cd ..\..
        pause
        exit /b 1
    )
    echo ✅ חבילת Electron נוצרה בהצלחה!
    echo 📁 מיקום: frontend\electron-app\release\
    cd ..\..
)

echo.
echo 👍 הבנייה הושלמה בהצלחה!
pause