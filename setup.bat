@echo off
REM NetGuard DNS Monitor - Windows Setup Script
REM Automated installation for Windows

echo.
echo ================================================================
echo.
echo        NetGuard DNS Monitor - Windows Setup
echo.
echo ================================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [1/4] Python detected successfully
echo.

REM Create virtual environment
echo [2/4] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)
echo.

REM Activate virtual environment and install dependencies
echo [3/4] Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

REM Setup complete
echo [4/4] Setup complete!
echo.
echo ================================================================
echo.
echo  Setup Complete! Next Steps:
echo.
echo  1. Activate virtual environment:
echo     venv\Scripts\activate
echo.
echo  2. Run NetGuard (as Administrator):
echo     python main.py
echo.
echo  3. Configure device DNS settings
echo     - Set Primary DNS to your computer's IP
echo     - Set Secondary DNS to 8.8.8.8
echo.
echo  Read QUICK_SETUP.md for more details
echo.
echo ================================================================
echo.

pause