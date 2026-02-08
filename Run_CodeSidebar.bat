@echo off
title CodeSidebar Launcher
:start
echo Starting CodeSidebar...
"%~dp0venv\Scripts\python.exe" "%~dp0main.py"
if %errorlevel% neq 0 (
    echo App crashed with exit code %errorlevel%. Restarting in 2 seconds...
    timeout /t 2 >nul
    goto start
)
echo Application closed normally.
pause
