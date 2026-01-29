@echo off
echo ============================================================
echo Deep Research Assistant - Setup Script
echo ============================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo [1/6] Python found
echo.

REM Create virtual environment
echo [2/6] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo [4/6] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
echo.

REM Create .env file if not exists
echo [5/6] Setting up environment configuration...
if not exist .env (
    copy .env.example .env
    echo .env file created from template
    echo IMPORTANT: Edit .env and add your TAVILY_API_KEY
) else (
    echo .env file already exists
)
echo.

REM Create necessary directories
echo [6/6] Creating directories...
if not exist data\chromadb mkdir data\chromadb
if not exist outputs mkdir outputs
if not exist temp mkdir temp
echo Directories created
echo.

echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Edit .env file and add your TAVILY_API_KEY
echo    Get free API key from: https://tavily.com
echo.
echo 2. Make sure Ollama is running:
echo    ollama serve
echo.
echo 3. Pull a model (if not already done):
echo    ollama pull llama3.2
echo.
echo 4. Run the application:
echo    python main.py
echo.
echo 5. Open browser to:
echo    http://localhost:5000
echo.
echo ============================================================
pause
