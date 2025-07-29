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
    if errorlevel 1 (
        echo ⚠️ לא ניתן לעצור חלק מתהליכי Python
    ) else (
        echo ✅ תהליכי Python נעצרו
    )
) else (
    echo ℹ️ אין תהליכי Python פעילים
)

REM Stop Node.js processes (Frontend)
echo 🌐 עוצר תהליכי Node.js...
tasklist | find "node.exe" >nul
if not errorlevel 1 (
    taskkill /f /im node.exe >nul 2>&1
    if errorlevel 1 (
        echo ⚠️ לא ניתן לעצור חלק מתהליכי Node.js
    ) else (
        echo ✅ תהליכי Node.js נעצרו
    )
) else (
    echo ℹ️ אין תהליכי Node.js פעילים
)

REM Stop Electron processes
echo 🖥️ עוצר תהליכי Electron...
tasklist | find "electron.exe" >nul
if not errorlevel 1 (
    taskkill /f /im electron.exe >nul 2>&1
    if errorlevel 1 (
        echo ⚠️ לא ניתן לעצור חלק מתהליכי Electron
    ) else (
        echo ✅ תהליכי Electron נעצרו
    )
) else (
    echo ℹ️ אין תהליכי Electron פעילים
)

REM Stop any remaining Audio Chat Studio processes
echo 🎵 עוצר תהליכי Audio Chat Studio...
tasklist | find "audio-chat-studio" >nul
if not errorlevel 1 (
    taskkill /f /im "audio-chat-studio*" >nul 2>&1
    echo ✅ תהליכי Audio Chat Studio נעצרו
) else (
    echo ℹ️ אין תהליכי Audio Chat Studio פעילים
)

REM Close specific command windows
echo 🪟 סוגר חלונות פקודה...
taskkill /fi "WindowTitle eq Audio Chat Studio*" /f >nul 2>&1

REM Wait for processes to fully terminate
echo ⏳ ממתין לסיום תהליכים...
timeout /t 3 /nobreak >nul

REM Check if ports are now free
echo 🔍 בודק שחרור פורטים...
netstat -an | find "127.0.0.1:5000" >nul
if errorlevel 1 (
    echo ✅ פורט 5000 שוחרר
) else (
    echo ⚠️ פורט 5000 עדיין תפוס
)

netstat -an | find "127.0.0.1:5001" >nul
if errorlevel 1 (
    echo ✅ פורט 5001 שוחרר
) else (
    echo ⚠️ פורט 5001 עדיין תפוס
)

netstat -an | find "127.0.0.1:5174" >nul
if errorlevel 1 (
    echo ✅ פורט 5174 שוחרר
) else (
    echo ⚠️ פורט 5174 עדיין תפוס
)

echo.
echo 🧹 מנקה קבצים זמניים...

REM Clean temporary files
if exist "data\temp\*" (
    del /q "data\temp\*" >nul 2>&1
    echo ✅ קבצים זמניים נוקו
) else (
    echo ℹ️ אין קבצים זמניים לניקוי
)

REM Clean cache files (optional)
echo 🗑️ רוצה לנקות גם קבצי cache? (y/n)
set /p clean_cache="בחר: "
if /i "%clean_cache%"=="y" (
    if exist "data\cache\*" (
        del /q "data\cache\*" >nul 2>&1
        echo ✅ קבצי cache נוקו
    ) else (
        echo ℹ️ אין קבצי cache לניקוי
    )
) else if /i "%clean_cache%"=="yes" (
    if exist "data\cache\*" (
        del /q "data\cache\*" >nul 2>&1
        echo ✅ קבצי cache נוקו
    ) else (
        echo ℹ️ אין קבצי cache לניקוי
    )
)

REM Clean old log files (optional)
echo 📋 רוצה לנקות לוגים ישנים? (y/n)
set /p clean_logs="בחר: "
if /i "%clean_logs%"=="y" (
    forfiles /p logs /m *.log /d -7 /c "cmd /c del @path" >nul 2>&1
    echo ✅ לוגים ישנים (מעל 7 ימים) נוקו
) else if /i "%clean_logs%"=="yes" (
    forfiles /p logs /m *.log /d -7 /c "cmd /c del @path" >nul 2>&1
    echo ✅ לוגים ישנים (מעל 7 ימים) נוקו
)

echo.
echo ========================================
echo    ✅ המערכת נעצרה בהצלחה! ✅
echo ========================================
echo.
echo 📊 סיכום:
echo    • כל התהליכים נעצרו
echo    • הפורטים שוחררו
echo    • קבצים זמניים נוקו
echo.
echo 🚀 להפעלה מחדש:
echo    • הפעלה רגילה:     scripts\start.bat
echo    • מצב פיתוח:       scripts\start-dev.bat
echo    • מצב ייצור:       scripts\start-prod.bat
echo.
echo 🔍 לבדיקת מצב:      scripts\utils\health-check.bat
echo.
pause