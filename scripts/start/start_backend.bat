@echo off

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found. Please run install_backend_dependencies.bat first.
    pause
    exit /b 1
)

REM Run the Python script to start Uvicorn
python run_uvicorn.py

pause