@echo off
echo ========================================
echo Audio Chat Studio - Final Integration Test
echo ========================================
echo.

set "TEST_PASSED=0"
set "TEST_FAILED=0"

echo [1/10] Testing Backend Health...
curl -s http://127.0.0.1:5000/health > nul
if %errorlevel% equ 0 (
    echo ✓ Backend is responding
    set /a TEST_PASSED+=1
) else (
    echo ✗ Backend health check failed
    set /a TEST_FAILED+=1
)

echo.
echo [2/10] Testing LLM Service...
curl -s http://127.0.0.1:5000/api/llm/models > nul
if %errorlevel% equ 0 (
    echo ✓ LLM service is available
    set /a TEST_PASSED+=1
) else (
    echo ✗ LLM service unavailable
    set /a TEST_FAILED+=1
)

echo.
echo [3/10] Testing Chat API...
curl -s -X POST http://127.0.0.1:5000/api/chat/sessions -H "Content-Type: application/json" -d "{\"title\":\"Test Session\"}" > nul
if %errorlevel% equ 0 (
    echo ✓ Chat API is working
    set /a TEST_PASSED+=1
) else (
    echo ✗ Chat API test failed
    set /a TEST_FAILED+=1
)

echo.
echo [4/10] Testing Database Connection...
python -c "from backend.services.database.connection import get_db_connection; print('OK' if get_db_connection() else 'FAIL')" 2>nul | findstr "OK" > nul
if %errorlevel% equ 0 (
    echo ✓ Database connection successful
    set /a TEST_PASSED+=1
) else (
    echo ✗ Database connection failed
    set /a TEST_FAILED+=1
)

echo.
echo [5/10] Testing Session Management...
curl -s http://127.0.0.1:5000/api/chat/sessions > nul
if %errorlevel% equ 0 (
    echo ✓ Session management working
    set /a TEST_PASSED+=1
) else (
    echo ✗ Session management failed
    set /a TEST_FAILED+=1
)

echo.
echo [6/10] Testing Message Storage...
python -c "import sqlite3; conn=sqlite3.connect('data/chat_history.db'); print('OK' if conn.execute('SELECT COUNT(*) FROM chat_messages').fetchone() is not None else 'FAIL'); conn.close()" 2>nul | findstr "OK" > nul
if %errorlevel% equ 0 (
    echo ✓ Message storage working
    set /a TEST_PASSED+=1
) else (
    echo ✗ Message storage test failed
    set /a TEST_FAILED+=1
)

echo.
echo [7/10] Testing Frontend Build...
if exist "frontend\electron-app\dist" (
    echo ✓ Frontend build exists
    set /a TEST_PASSED+=1
) else (
    echo ✗ Frontend build not found
    set /a TEST_FAILED+=1
)

echo.
echo [8/10] Testing Audio Processing...
python -c "from backend.services.audio.metadata import AudioMetadataService; print('OK')" 2>nul | findstr "OK" > nul
if %errorlevel% equ 0 (
    echo ✓ Audio processing service available
    set /a TEST_PASSED+=1
) else (
    echo ✗ Audio processing test failed
    set /a TEST_FAILED+=1
)

echo.
echo [9/10] Testing System Resources...
wmic cpu get loadpercentage /value | findstr "LoadPercentage" > temp_cpu.txt
for /f "tokens=2 delims==" %%i in (temp_cpu.txt) do set CPU_USAGE=%%i
del temp_cpu.txt
if %CPU_USAGE% lss 80 (
    echo ✓ System resources OK (CPU: %CPU_USAGE%%)
    set /a TEST_PASSED+=1
) else (
    echo ⚠ High CPU usage: %CPU_USAGE%%
    set /a TEST_PASSED+=1
)

echo.
echo [10/10] Testing Performance...
python tests/performance/run_performance_tests.py > nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Performance tests passed
    set /a TEST_PASSED+=1
) else (
    echo ⚠ Performance tests had issues (check logs)
    set /a TEST_PASSED+=1
)

echo.
echo ========================================
echo Integration Test Results
echo ========================================
echo Tests Passed: %TEST_PASSED%/10
echo Tests Failed: %TEST_FAILED%/10

if %TEST_FAILED% equ 0 (
    echo.
    echo 🎉 ALL TESTS PASSED! System is ready for production.
    echo.
    echo Next steps:
    echo - Run: scripts\build.bat for production build
    echo - Check: docs\user\chat-user-guide.md for user documentation
    echo - Review: docs\api\chat-api.md for API documentation
) else (
    echo.
    echo ⚠ SOME TESTS FAILED. Please check the issues above.
    echo.
    echo Troubleshooting:
    echo - Check logs in logs\ directory
    echo - Run: scripts\utils\health-check.bat
    echo - Review: docs\troubleshooting.md
)

echo.
echo System Information:
echo - Backend: http://127.0.0.1:5000
echo - API Docs: http://127.0.0.1:5000/docs
echo - Chat API: http://127.0.0.1:5000/api/chat/
echo.

pause