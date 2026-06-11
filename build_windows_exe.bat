@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating build virtual environment...
    py -3 -m venv .venv || goto :error
)

call ".venv\Scripts\activate.bat" || goto :error
python -m pip install --upgrade pip || goto :error
python -m pip install pyinstaller || goto :error
pyinstaller --clean --noconfirm "auto_url_fixer.spec" || goto :error

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
