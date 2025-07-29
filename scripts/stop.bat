@echo off
chcp 65001 >nul
title Audio Chat Studio - עצירת המערכת

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    עצירת המערכת
echo ========================================
echo.

echo 🛑 עוצר תהליכי המערכת...

REM Stop Python processes (Backend)
echo 🔵 עוצר שרת Backend...
tasklist | find "python.exe" >nul
if not errorlevel 1 (
    taskkill /f /im python.exe 2>nul
    if not errorlevel 1 (
        echo ✅ שרת Backend נעצר
    ) else (
        echo ⚠️ לא הצלחתי לעצור את שרת Backend
    )
) else (
    echo ℹ️ שרת Backend לא רץ
)

REM Stop Node.js processes (Frontend)
echo 🟢 עוצר Frontend...
tasklist | find "node.exe" >nul
if not errorlevel 1 (
    taskkill /f /im node.exe 2>nul
    if not errorlevel 1 (
        echo ✅ Frontend נעצר
    ) else (
        echo ⚠️ לא הצלחתי לעצור את Frontend
    )
) else (
    echo ℹ️ Frontend לא רץ
)

REM Stop Electron processes
echo 🖥️ עוצר תהליכי Electron...
tasklist | find "electron.exe" >nul
if not errorlevel 1 (
    taskkill /f /im electron.exe 2>nul
    if not errorlevel 1 (
        echo ✅ Electron נעצר
    ) else (
        echo ⚠️ לא הצלחתי לעצור את Electron
    )
) else (
    echo ℹ️ Electron לא רץ
)

REM Close command windows
echo 🪟 סוגר חלונות פקודה...
taskkill /f /fi "WindowTitle eq Backend Server*" 2>nul
taskkill /f /fi "WindowTitle eq Frontend*" 2>nul

REM Wait a moment for processes to close
timeout /t 2 /nobreak >nul

REM Check if ports are now free
echo 🔍 בודק שחרור פורטים...
netstat -an | find "127.0.0.1:5000" >nul
if errorlevel 1 (
    echo ✅ פורט 5000 פנוי
) else (
    echo ⚠️ פורט 5000 עדיין תפוס
)

netstat -an | find "127.0.0.1:5174" >nul
if errorlevel 1 (
    echo ✅ פורט 5174 פנוי
) else (
    echo ⚠️ פורט 5174 עדיין תפוס
)

echo.
echo ✅ המערכת נעצרה!
echo.
echo 🚀 להפעלה מחדש הרץ: scripts\start.bat
echo.
pause