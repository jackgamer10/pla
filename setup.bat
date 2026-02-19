@echo off
title MagxxicVOT SMS Setup
echo ==========================================
echo       MagxxicVOT SMS Setup Wizard
echo ==========================================
echo.

set "PYTHON_CMD=python"
%PYTHON_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    set "PYTHON_CMD=py"
    %PYTHON_CMD% --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [!] Python not found. Starting automatic installation...
        echo [+] Downloading Python installer...
        curl -L -o python_installer.exe https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe
        if %errorlevel% neq 0 (
            echo [!] Failed to download Python installer. Please install it manually from https://www.python.org/
            pause
            exit /b 1
        )
        echo [+] Installing Python (this may take a minute, please wait)...
        start /wait python_installer.exe /quiet PrependPath=1
        del python_installer.exe
        echo [+] Python installation attempted.
        echo [!] IMPORTANT: Please restart this setup script to detect the new Python installation.
        pause
        exit /b 0
    )
)

echo [+] Using Python command: %PYTHON_CMD%
echo [+] Creating virtual environment...
%PYTHON_CMD% -m venv venv
if %errorlevel% neq 0 (
    echo [!] Warning: Failed to create virtual environment. Installing to global scope...
    %PYTHON_CMD% -m pip install -r requirements.txt
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
