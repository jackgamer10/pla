@echo off
title MagxxicVOT SMS Setup
echo ==========================================
echo       MagxxicVOT SMS Setup Wizard
echo ==========================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Error: Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [+] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo [!] Warning: Failed to create virtual environment. Installing to global scope...
    pip install -r requirements.txt
) else (
    echo [+] Activating virtual environment...
    call venv\Scripts\activate
    echo [+] Installing dependencies...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
)

if not exist .env (
    echo [+] Creating .env file from template...
    copy .env.example .env
)

echo.
echo ==========================================
echo       Setup finished successfully!
echo ==========================================
echo.
echo To start the tool, run 'python app.py'
echo (make sure your venv is activated).
echo.
pause
