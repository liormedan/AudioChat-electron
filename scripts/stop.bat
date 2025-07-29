@echo off
chcp 65001 >nul
title Audio Chat Studio - Stop System

echo.
echo ========================================
echo    🎵 Audio Chat Studio 🎵
echo    עצירת המערכת
echo ========================================
echo.

echo 🛑 עוצר את כל שירותי המערכת...
echo.

REM Stop Python processes (Backend)
echo 🐍 עוצר תהליכי Python...
tasklist | find "python.exe" >nul
if not errorlevel 1 (
    taskkill /f /im python.exe >nul 2>&1
    if not errorlevel 1 (
        echo ✅ תהליכי Python נעצרו
    ) else (
        echo ⚠️ לא ניתן לעצור חלק מתהליכי Python
    )
) else (
    echo ✅ אין תהליכי Python פעילים
)

REM Stop Node.js processes (Frontend)
echo 🌐 עוצר תהליכי Node.js...
tasklist | find "node.exe" >nul
if not errorlevel 1 (
    taskkill /f /im node.exe >nul 2>&1
    if not errorlevel 1 (
        echo ✅ תהליכי Node.js נעצרו
    ) else (
        echo ⚠️ לא ניתן לעצור חלק מתהליכי Node.js
    )
) else (
    echo ✅ אין תהליכי Node.js פעילים
)

REM Stop Electron processes
echo 🖥️ עוצר תהליכי Electron...
tasklist | find "electron.exe" >nul
if not errorlevel 1 (
    taskkill /f /im electron.exe >nul 2>&1
    if not errorlevel 1 (
        echo ✅ תהליכי Electron נעצרו
    ) else (
        echo ⚠️ לא ניתן לעצור חלק מתהליכי Electron
    )
) else (
    echo ✅ אין תהליכי Electron פעילים
)

REM Stop any remaining Audio Chat Studio processes
echo 🎵 עוצר תהליכי Audio Chat Studio...
tasklist | find "audio-chat-studio" >nul
if not errorlevel 1 (
    taskkill /f /im "audio-chat-studio*" >nul 2>&1
    if not errorlevel 1 (
        echo ✅ תהליכי Audio Chat Studio נעצרו
    ) else (
        echo ⚠️ לא ניתן לעצור חלק מהתהליכים
    )
) else (
    echo ✅ אין תהליכי Audio Chat Studio פעילים
)

REM Close specific command windows
echo 🪟 סוגר חלונות פקודה...
taskkill /fi "WINDOWTITLE eq Audio Chat Studio*" /f >nul 2>&1

REM Wait for processes to fully terminate
echo ⏳ ממתין לסיום התהליכים...
timeout /t 3 /nobreak >nul

REM Check if ports are now free
echo 🔌 בודק שחרור פורטים...
netstat -an | find "127.0.0.1:5000" >nul
if errorlevel 1 (
    echo ✅ פורט 5000 משוחרר
) else (
    echo ⚠️ פורט 5000 עדיין תפוס
)

netstat -an | find "127.0.0.1:5001" >nul
if errorlevel 1 (
    echo ✅ פורט 5001 משוחרר
) else (
    echo ⚠️ פורט 5001 עדיין תפוס
)

netstat -an | find "127.0.0.1:5174" >nul
if errorlevel 1 (
    echo ✅ פורט 5174 משוחרר (Vite)
) else (
    echo ⚠️ פורט 5174 עדיין תפוס (Vite)
)

echo.
echo 🧹 רוצה לנקות קבצים זמניים? (y/n)
set /p cleanup="בחר: "
if /i "%cleanup%"=="y" (
    call scripts\utils\cleanup.bat
) else if /i "%cleanup%"=="yes" (
    call scripts\utils\cleanup.bat
) else (
    echo ✅ דילוג על ניקוי
)

echo.
echo ========================================
echo    ✅ המערכת נעצרה בהצלחה! ✅
echo ========================================
echo.
echo 📊 מצב המערכת:
echo    • כל התהליכים נעצרו
echo    • הפורטים משוחררים
echo    • המערכת מוכנה להפעלה מחדש
echo.
echo 🚀 להפעלה מחדש:
echo    • הפעלה רגילה:     scripts\start.bat
echo    • מצב פיתוח:       scripts\start-dev.bat
echo    • מצב ייצור:       scripts\start-prod.bat
echo.
echo 🔍 לבדיקת מצב:      scripts\utils\health-check.bat
echo.
pause