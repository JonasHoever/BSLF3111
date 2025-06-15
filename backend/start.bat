@echo off
echo Lade updates
python.exe -m pip install --upgrade pip
timeout /t 10 /nobreak >nul
echo Alte virtuelle Umgebung wird gelöscht...
rmdir /s /q venv

echo Warte 2 Sekunden...
timeout /t 2 /nobreak >nul

echo Neue virtuelle Umgebung wird erstellt...
python -m venv venv

echo Warte 5 Sekunden für venv-Erstellung...
timeout /t 5 /nobreak >nul

echo venv wurde installiert.

REM → Neue Konsole mit aktivierter venv und Start von app.py
start cmd /k "venv\Scripts\activate.bat && python.exe -m pip install --upgrade pip && pip install flask && python app.py"
