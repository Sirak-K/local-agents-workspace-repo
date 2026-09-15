@echo off
setlocal
set "REPO_ROOT=%~dp0.."
call "%REPO_ROOT%\SillyTavern_UI\harness\Test-Guide1.cmd" %*
exit /b %errorlevel%
