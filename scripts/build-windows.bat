@echo off
REM Build script for Windows
REM Creates executable in dist\OnlyCode\

setlocal

set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..

cd /d "%PROJECT_DIR%"

echo ==========================================
echo Building Only Code for Windows
echo ==========================================

REM Check for virtual environment
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install PyInstaller if not present
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Build
echo Building...
python build.py %*

if exist "dist\OnlyCode\OnlyCode.exe" (
    echo.
    echo Build successful!
    echo Run with: dist\OnlyCode\OnlyCode.exe
)

endlocal

