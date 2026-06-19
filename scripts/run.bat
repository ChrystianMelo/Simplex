@echo off
cd /d "%~dp0.."

echo Activating virtual environment...
call venv\Scripts\activate

echo Running project...
py src\main.py %*
pause
