@echo off
title CodeSidebar Launcher
:start
echo Starting CodeSidebar...
start "" "%~dp0venv\Scripts\pythonw.exe" "%~dp0main.py"
exit
