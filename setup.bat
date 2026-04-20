@echo off
setlocal
title MagxxicVOT Email Sorter Setup

echo =======================================================
echo     MagxxicVOT Advanced Email Sorter - Setup
echo =======================================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Installing dependencies (aiodns, pycares)...
python -m pip install aiodns pycares --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies. Check your internet connection.
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully.
echo.

echo [2/3] Verifying files...
if not exist "magxxic_sorter_gui.py" (
    echo [ERROR] magxxic_sorter_gui.py not found in the current directory.
    pause
    exit /b 1
)
echo [OK] All files verified.
echo.

echo [3/3] Launching MagxxicVOT Advanced Email Sorter GUI...
echo.
python magxxic_sorter_gui.py

if %errorlevel% neq 0 (
    echo.
    echo [INFO] Application closed with errors or manually stopped.
)

pause
endlocal
