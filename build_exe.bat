@echo off
setlocal
cd /d "%~dp0"
python -m venv "%~dp0.venv"
call "%~dp0.venv\Scripts\activate.bat"
python -m pip install -r "%~dp0requirements.txt" pyinstaller
python -m PyInstaller --noconfirm --clean "%~dp0ParameterAudit.spec"
echo.
echo Built: %~dp0dist\ParameterAudit.exe
echo Double-click dist\ParameterAudit.exe then select several input files.
pause

