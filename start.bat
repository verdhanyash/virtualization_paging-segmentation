    
    @echo off
setlocal

REM Run from the repository root (directory containing this file).
cd /d "%~dp0"

if not exist "app.py" (
    echo [ERROR] app.py not found in %CD%
    pause
    exit /b 1
)

REM Prefer project virtual environment Python when available.
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    echo [WARN] .venv not found. Falling back to system Python.
    set "PYTHON_EXE=python"
)

echo Starting Virtual Memory Simulator...
"%PYTHON_EXE%" app.py

if errorlevel 1 (
    echo.
    echo [ERROR] App failed to start.
    pause
)

endlocal
