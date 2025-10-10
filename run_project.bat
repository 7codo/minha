@echo off
REM ANEM Automation Project Runner
REM This batch file sets up and runs the ANEM automation script

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo ================================================
echo ANEM Automation Project Runner
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo Python found: 
python --version

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
    REM Activate virtual environment
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo ERROR: Failed to activate virtual environment
        pause
        exit /b 1
    )

    REM Install/update dependencies
    echo Installing dependencies...
    uv pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists
    REM Activate virtual environment
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo ERROR: Failed to activate virtual environment
        pause
        exit /b 1
    )
    
    REM Install/update dependencies
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)



REM Check if .env file exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Creating .env template file...
    echo.
    echo # ANEM Automation Environment Variables > .env
    echo # Replace the values below with your actual numbers >> .env
    echo N1=your_wassit_number_here >> .env
    echo N2=your_piece_identite_number_here >> .env
    echo.
    echo Please edit the .env file and add your actual N1 and N2 values
    echo N1 = Your Wassit number
    echo N2 = Your Piece Identite number
    echo.
    echo After editing .env file, run this batch file again
    pause
    exit /b 0
)

REM Check if sound.mp3 exists
if not exist "sound.mp3" (
    echo WARNING: sound.mp3 file not found!
    echo The script will work without it, but won't play notification sounds
    echo.
)

REM Activate virtual environment before running script
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Run the main script
echo.
echo Starting ANEM automation script...
echo ================================================
python anem_automation.py

REM Keep window open to see results
echo.
echo ================================================
echo Script execution completed
echo ================================================
