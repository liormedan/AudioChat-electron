@echo off
chcp 65001 >nul
title Audio Chat Studio - Cleanup

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    ניקוי קבצים זמניים
echo ========================================
echo.

echo 🧹 מנקה קבצים זמניים...
echo.

REM Clean temporary data files
echo 📁 מנקה תיקיית temp...
if exist "data\temp" (
    del /q "data\temp\*.*" >nul 2>&1
    for /d %%i in ("data\temp\*") do rmdir /s /q "%%i" >nul 2>&1
    echo ✅ תיקיית temp נוקתה
) else (
    echo ✅ תיקיית temp לא קיימת
)

REM Clean cache files
echo 💾 מנקה תיקיית cache...
if exist "data\cache" (
    del /q "data\cache\*.*" >nul 2>&1
    for /d %%i in ("data\cache\*") do rmdir /s /q "%%i" >nul 2>&1
    echo ✅ תיקיית cache נוקתה
) else (
    echo ✅ תיקיית cache לא קיימת
)

REM Clean old log files (keep recent ones)
echo 📋 מנקה קבצי לוג ישנים...
if exist "logs" (
    REM Delete log files older than 7 days
    forfiles /p "logs" /m "*.log" /d -7 /c "cmd /c del @path" >nul 2>&1
    echo ✅ קבצי לוג ישנים נמחקו (מעל 7 ימים)
) else (
    echo ✅ תיקיית logs לא קיימת
)

REM Clean Python cache files
echo 🐍 מנקה Python cache...
if exist "backend\__pycache__" (
    rmdir /s /q "backend\__pycache__" >nul 2>&1
    echo ✅ Python __pycache__ נמחק
)

for /r "backend" %%i in (__pycache__) do (
    if exist "%%i" rmdir /s /q "%%i" >nul 2>&1
)

for /r "backend" %%i in (*.pyc) do (
    if exist "%%i" del /q "%%i" >nul 2>&1
)
echo ✅ קבצי Python cache נוקו

REM Clean Node.js cache (if exists)
echo 🌐 מנקה Node.js cache...
if exist "frontend\electron-app\.vite" (
    rmdir /s /q "frontend\electron-app\.vite" >nul 2>&1
    echo ✅ Vite cache נמחק
)

if exist "frontend\electron-app\node_modules\.cache" (
    rmdir /s /q "frontend\electron-app\node_modules\.cache" >nul 2>&1
    echo ✅ Node.js cache נמחק
)

REM Clean build artifacts (optional)
echo 🏗️ רוצה למחוק build artifacts? (y/n)
set /p clean_builds="בחר: "
if /i "%clean_builds%"=="y" (
    echo 🏗️ מנקה build artifacts...
    
    if exist "frontend\electron-app\dist" (
        rmdir /s /q "frontend\electron-app\dist" >nul 2>&1
        echo ✅ Frontend dist נמחק
    )
    
    if exist "py_build" (
        rmdir /s /q "py_build" >nul 2>&1
        echo ✅ Python build נמחק
    )
    
    if exist "frontend\electron-app\release" (
        rmdir /s /q "frontend\electron-app\release" >nul 2>&1
        echo ✅ Electron release נמחק
    )
) else if /i "%clean_builds%"=="yes" (
    echo 🏗️ מנקה build artifacts...
    
    if exist "frontend\electron-app\dist" (
        rmdir /s /q "frontend\electron-app\dist" >nul 2>&1
        echo ✅ Frontend dist נמחק
    )
    
    if exist "py_build" (
        rmdir /s /q "py_build" >nul 2>&1
        echo ✅ Python build נמחק
    )
    
    if exist "frontend\electron-app\release" (
        rmdir /s /q "frontend\electron-app\release" >nul 2>&1
        echo ✅ Electron release נמחק
    )
) else (
    echo ✅ דילוג על build artifacts
)

REM Clean uploaded files (with confirmation)
echo 📤 רוצה למחוק קבצים שהועלו? (y/n)
echo ⚠️ זה ימחק את כל הקבצים שהועלו למערכת!
set /p clean_uploads="בחר: "
if /i "%clean_uploads%"=="y" (
    echo 📤 מנקה קבצים שהועלו...
    
    if exist "data\uploads" (
        del /q "data\uploads\*.*" >nul 2>&1
        for /d %%i in ("data\uploads\*") do rmdir /s /q "%%i" >nul 2>&1
        echo ✅ קבצים שהועלו נמחקו
    )
    
    if exist "data\processed" (
        del /q "data\processed\*.*" >nul 2>&1
        for /d %%i in ("data\processed\*") do rmdir /s /q "%%i" >nul 2>&1
        echo ✅ קבצים מעובדים נמחקו
    )
) else if /i "%clean_uploads%"=="yes" (
    echo 📤 מנקה קבצים שהועלו...
    
    if exist "data\uploads" (
        del /q "data\uploads\*.*" >nul 2>&1
        for /d %%i in ("data\uploads\*") do rmdir /s /q "%%i" >nul 2>&1
        echo ✅ קבצים שהועלו נמחקו
    )
    
    if exist "data\processed" (
        del /q "data\processed\*.*" >nul 2>&1
        for /d %%i in ("data\processed\*") do rmdir /s /q "%%i" >nul 2>&1
        echo ✅ קבצים מעובדים נמחקו
    )
) else (
    echo ✅ דילוג על קבצים שהועלו
)

echo.
echo ========================================
echo    ✅ הניקוי הושלם בהצלחה! ✅
echo ========================================
echo.
echo 🧹 מה שנוקה:
echo    • קבצים זמניים
echo    • קבצי cache
echo    • קבצי לוג ישנים
echo    • Python cache files
echo    • Node.js cache files
if /i "%clean_builds%"=="y" echo    • Build artifacts
if /i "%clean_uploads%"=="y" echo    • קבצים שהועלו
echo.
echo 💡 המערכת נקייה ומוכנה לשימוש!
echo.
echo 🚀 להפעלת המערכת:
echo    scripts\start.bat
echo.
pause