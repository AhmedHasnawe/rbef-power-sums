@echo off
REM Run this on Windows with Python 3.8+ installed.
python -m pip install --upgrade pyinstaller
python -m PyInstaller --onefile --windowed --name RBEF_Calculator rbef_app.py
echo.
echo Done. The program is in the "dist" folder: dist\RBEF_Calculator.exe
pause
