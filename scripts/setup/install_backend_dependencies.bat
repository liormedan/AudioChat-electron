@echo off

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

REM Install/update pip
.venv\Scripts\python.exe -m pip install --upgrade pip

REM Install dependencies from requirements.txt
.venv\Scripts\python.exe -m pip install -r requirements.txt

echo Backend dependencies installed successfully.
pause