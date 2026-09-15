@echo off
setlocal
set "REPO_ROOT=%~dp0.."
call "%REPO_ROOT%\SillyTavern_UI\harness\Start-SillyTavern.cmd" %*
exit /b %errorlevel%
