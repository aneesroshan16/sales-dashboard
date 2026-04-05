@echo off
title Sales Dashboard Launcher
echo 🔍 Checking environment...

:: Check if pandas is installed as a proxy for the env
python -c "import pandas" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python or Pandas not found. Please install requirements.txt first.
    pause
    exit /b
)

echo 🚀 Launching Streamlit Dashboard...
echo (If this is the first time, it may take a few seconds)
echo.

:: Use python -m to avoid PATH issues with the 'streamlit' command
python -m streamlit run app.py

pause
