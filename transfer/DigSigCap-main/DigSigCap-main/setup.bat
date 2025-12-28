@echo off
REM DigitalSignalCapture Windows Setup Script

echo Creating virtual environment...
python -m venv .venv

echo Activating virtual environment...
call .\.venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt

echo Installing system dependencies...
echo Please install these manually:
echo 1. Npcap: https://npcap.com/ (select "WinPcap API-compatible mode")
echo 2. Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
echo    (make sure to check "Add to PATH" during installation)

echo Initializing database...
python -c "from storage.database import init_db; init_db()"

echo Creating desktop shortcut...
set SCRIPT_PATH=%~dp0
set SHORTCUT_PATH="%USERPROFILE%\Desktop\DigitalSignalCapture.lnk"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut(%SHORTCUT_PATH%); $s.TargetPath = 'powershell.exe'; $s.Arguments = '-NoExit -Command \"cd ''%SCRIPT_PATH%''; .\.venv\Scripts\activate; python main.py\"'; $s.IconLocation = '%SCRIPT_PATH%app.ico,0'; $s.Save()"

echo Setup complete! Virtual environment activated.
echo Use the shortcut on your desktop to launch the application.