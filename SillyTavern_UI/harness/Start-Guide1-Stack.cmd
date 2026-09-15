@echo off
setlocal
set "SCRIPT_DIR=%~dp0"

where pwsh.exe >nul 2>&1
if %errorlevel%==0 (
    pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%Start-Guide1-Stack.ps1" %*
    exit /b %errorlevel%
)

where powershell.exe >nul 2>&1
if %errorlevel%==0 (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%Start-Guide1-Stack.ps1" %*
    exit /b %errorlevel%
)

echo ERROR: Neither pwsh.exe nor powershell.exe was found in PATH.
exit /b 1
