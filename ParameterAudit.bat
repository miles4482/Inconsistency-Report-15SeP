@echo off
setlocal
cd /d "%~dp0"
if exist "%~dp0dist\ParameterAudit\ParameterAudit.exe" (
  start "" "%~dp0dist\ParameterAudit\ParameterAudit.exe"
) else if exist "%~dp0dist\ParameterAudit.exe" (
  start "" "%~dp0dist\ParameterAudit.exe"
) else (
  python "%~dp0scripts\parameter_audit_app.py"
)
