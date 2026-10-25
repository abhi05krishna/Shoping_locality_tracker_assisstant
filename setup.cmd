@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python 3.13 or newer is required. Install Python and try again.
  exit /b 1
)
python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,13) else 1)"
if errorlevel 1 (
  echo Python 3.13 or newer is required. Install a supported Python version and try again.
  exit /b 1
)
python -m venv .venv
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
  echo Setup failed while installing dependencies. Check your internet connection and retry setup.cmd.
  exit /b 1
)
echo Setup complete. Run run.cmd to start the local app.
