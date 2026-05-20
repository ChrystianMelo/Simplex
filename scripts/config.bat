@echo off
cd /d "%~dp0.."

echo Creating virtual environment...
py -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Upgrading pip and installing requirements...
pip install -e .
pip install -r requirements.txt

echo Deleting previous results...
rmdir /s /q "data\result"

echo Setup complete!
pause
