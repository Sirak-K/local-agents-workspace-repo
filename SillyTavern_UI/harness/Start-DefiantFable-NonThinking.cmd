@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PS_EXE="

for /f "delims=" %%I in ('where pwsh.exe 2^>nul') do if not defined PS_EXE set "PS_EXE=%%I"
if not defined PS_EXE if exist "%ProgramFiles%\PowerShell\7\pwsh.exe" set "PS_EXE=%ProgramFiles%\PowerShell\7\pwsh.exe"
if not defined PS_EXE if exist "%LocalAppData%\Microsoft\WindowsApps\pwsh.exe" set "PS_EXE=%LocalAppData%\Microsoft\WindowsApps\pwsh.exe"
for /f "delims=" %%I in ('where powershell.exe 2^>nul') do if not defined PS_EXE set "PS_EXE=%%I"
if not defined PS_EXE if exist "%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" set "PS_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"

if not defined PS_EXE (
    echo ERROR: No usable PowerShell executable was found.
    exit /b 1
)

echo Using PowerShell: "%PS_EXE%"
echo Starting DefiantFable/Qwen3.5 with backend Jinja and enable_thinking=false...
echo SillyTavern path for this profile: Chat Completion ^> Custom (OpenAI-compatible) ^> http://127.0.0.1:5001/v1
echo After KoboldCpp is ready, verify from another terminal with: .\scripts\Test-DefiantFable-NonThinking.cmd
echo.
"%PS_EXE%" -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%Start-KoboldCpp-TextBaseline.ps1" -Jinja -DisableThinking %*
exit /b %errorlevel%
