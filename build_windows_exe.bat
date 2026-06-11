@echo off
setlocal

cd /d "%~dp0"
set "VENV_PY=.venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo Creating build virtual environment...
    py -3 -m venv .venv || goto :error
)

"%VENV_PY%" --version >nul 2>nul
if errorlevel 1 (
    echo Build virtual environment is broken. Delete the .venv folder and run this script again after installing Python.
    goto :error
)

"%VENV_PY%" -m pip install --upgrade pip || goto :error
"%VENV_PY%" -m pip install pyinstaller || goto :error

if exist "dist\Auto URL Fixer.exe" (
    echo Removing old onefile executable...
    del /F /Q "dist\Auto URL Fixer.exe" || goto :error
)

if exist "dist\Auto URL Fixer" (
    echo Removing old onedir build...
    rmdir /S /Q "dist\Auto URL Fixer" || goto :error
)

"%VENV_PY%" -m PyInstaller --clean --noconfirm "auto_url_fixer.spec" || goto :error

if not exist "dist\Auto URL Fixer\Auto URL Fixer.exe" (
    echo Built executable was not found.
    goto :error
)
copy /Y "config.example.json" "dist\Auto URL Fixer\" >nul || goto :error
copy /Y "README.md" "dist\Auto URL Fixer\" >nul || goto :error

echo Build complete: "%~dp0dist\Auto URL Fixer"
exit /b 0

:error
echo Build failed.
exit /b 1
