@echo off
REM Orchestrator Toolkit Setup Script for Windows
REM This script sets up the development environment automatically

echo.
echo ===================================
echo  Orchestrator Toolkit Setup
echo ===================================
echo.

REM Check Python installation
echo Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python %PYTHON_VERSION% detected
echo.

REM Create virtual environment
set VENV_DIR=.otk-venv
if exist %VENV_DIR% (
    echo WARNING: Virtual environment already exists at %VENV_DIR%
    set /p RECREATE="Do you want to recreate it? (y/N): "
    if /i "%RECREATE%"=="y" (
        echo Removing old virtual environment...
        rmdir /s /q %VENV_DIR%
    ) else (
        echo Using existing virtual environment...
    )
)

if not exist %VENV_DIR% (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call %VENV_DIR%\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel --quiet

REM Install package
echo Installing Orchestrator Toolkit...
pip install -e . --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install package
    pause
    exit /b 1
)

echo Installation complete
echo.

REM Create ai_docs directory
if not exist ai_docs (
    echo Creating ai_docs directory...
    mkdir ai_docs\tasks
    mkdir ai_docs\plans
    echo Artifact directories created
)

REM Create activation script
echo @echo off > activate_otk.bat
echo call .otk-venv\Scripts\activate.bat >> activate_otk.bat
echo set OTK_ARTIFACT_ROOT=ai_docs >> activate_otk.bat
echo echo Orchestrator Toolkit environment activated >> activate_otk.bat
echo echo Artifacts will be stored in: ai_docs/ >> activate_otk.bat

echo.
echo ================================
echo  Setup Complete!
echo ================================
echo.
echo To activate the environment:
echo   activate_otk.bat
echo.
echo Available commands:
echo   task-new "Task title" --owner Name
echo   plan-new "Plan title" --task T-0001
echo   orchestrator-once
echo.
echo Quick test:
echo   task-new "My first task" --owner %USERNAME%
echo.
echo For more information, see README.md
echo.

REM Test installation
echo Running quick test...
python -c "from orchestrator_toolkit.settings import OrchSettings; OrchSettings.load()" >nul 2>&1
if %errorlevel% equ 0 (
    echo Installation verified successfully!
) else (
    echo WARNING: Installation test failed. Please check for errors.
)

echo.
pause