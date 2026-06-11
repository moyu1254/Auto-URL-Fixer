@echo off
setlocal

set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "REMOVED="

if exist "%STARTUP_DIR%\Auto URL Fixer.vbs" (
    del "%STARTUP_DIR%\Auto URL Fixer.vbs" >nul 2>nul
    set "REMOVED=1"
)

if exist "%STARTUP_DIR%\Auto URL Fixer.bat" (
    del "%STARTUP_DIR%\Auto URL Fixer.bat" >nul 2>nul
    set "REMOVED=1"
)

if defined REMOVED (
    echo Disabled startup entry.
) else (
    echo No startup entry was found.
)
