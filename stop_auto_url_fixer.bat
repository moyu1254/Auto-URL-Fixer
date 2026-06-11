@echo off
setlocal

set "RUNTIME_DIR=%LOCALAPPDATA%\AutoURLFixer"
set "PID_FILE=%RUNTIME_DIR%\auto_url_fixer.pid"
set "STOP_FILE=%RUNTIME_DIR%\stop.flag"

if not exist "%RUNTIME_DIR%" (
    mkdir "%RUNTIME_DIR%" >nul 2>nul
)

type nul >"%STOP_FILE%"

if not exist "%PID_FILE%" (
    echo Stop request sent. PID file was not found.
    exit /b 0
)

set /p PID=<"%PID_FILE%"
if "%PID%"=="" (
    echo Stop request sent. PID file was empty.
    exit /b 0
)

timeout /t 2 /nobreak >nul
tasklist /FI "PID eq %PID%" | find "%PID%" >nul
if errorlevel 1 (
    echo Auto URL Fixer has stopped.
    del "%PID_FILE%" >nul 2>nul
    del "%STOP_FILE%" >nul 2>nul
    exit /b 0
)

taskkill /PID %PID% /T /F >nul
if errorlevel 1 (
    echo Failed to stop PID %PID%.
    exit /b 1
)

del "%PID_FILE%" >nul 2>nul
del "%STOP_FILE%" >nul 2>nul
echo Auto URL Fixer was force-stopped. PID: %PID%
