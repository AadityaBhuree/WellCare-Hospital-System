@echo off
echo ========================================================
echo   WellCare Hospital System Setup (Windows)
echo ========================================================

echo 1. Creating Virtual Environment (.venv)...
python -m venv .venv

echo 2. Activating Virtual Environment...
call .venv\Scripts\activate

echo 3. Upgrading pip...
python -m pip install --upgrade pip

echo 4. Installing Dependencies from requirements.txt...
pip install -r requirements.txt

echo 5. Setup Complete!
echo.
echo To run the application, type: 
echo python main.py
echo.
pause
