@echo off
setlocal
cd /d "%~dp0"

python -c "import openpyxl, pyxlsb" >nul 2>&1
if errorlevel 1 (
  echo Installing Python dependencies...
  python -m pip install -r "%~dp0requirements.txt"
)

python "%~dp0scripts/compare_reference_parameters.py" --input-folder "%~dp0input" --reference-folder "%~dp0reference" --output-folder "%~dp0reports" %*
exit /b %ERRORLEVEL%
