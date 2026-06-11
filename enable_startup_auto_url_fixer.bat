@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "TARGET=%STARTUP_DIR%\Auto URL Fixer.bat"

if not exist "%STARTUP_DIR%" (
    echo Startup folder was not found.
    exit /b 1
)

(
    echo @echo off
    echo cd /d "%SCRIPT_DIR%"
    echo wscript //nologo "%SCRIPT_DIR%start_auto_url_fixer.vbs"
)>"%TARGET%"

echo Enabled startup: "%TARGET%"
