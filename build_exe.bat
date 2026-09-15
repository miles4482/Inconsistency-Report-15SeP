@echo off
setlocal
cd /d "%~dp0"
python -m venv "%~dp0.venv"
call "%~dp0.venv\Scripts\activate.bat"
python -m pip install -r "%~dp0requirements.txt" pyinstaller
python -m PyInstaller --noconfirm --clean "%~dp0ParameterAudit.spec"
echo.
echo Built folder: %~dp0dist\ParameterAudit\
echo Run: %~dp0dist\ParameterAudit\ParameterAudit.exe
pause
