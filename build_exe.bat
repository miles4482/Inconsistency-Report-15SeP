@echo off
setlocal
cd /d "%~dp0"
python -m venv "%~dp0.venv"
call "%~dp0.venv\Scripts\activate.bat"
python -m pip install -r "%~dp0requirements.txt" pyinstaller
python -m PyInstaller --noconfirm --clean "%~dp0ParameterAudit.spec"
python -m PyInstaller --noconfirm "%~dp0LicenseGenerator.spec"
echo.
echo Built folder: %~dp0dist\ParameterAudit\
echo License generator: %~dp0dist\LicenseGenerator\
echo Run: %~dp0dist\ParameterAudit\ParameterAudit.exe
pause
