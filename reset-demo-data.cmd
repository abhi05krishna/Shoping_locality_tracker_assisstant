@echo off
setlocal
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe -m app.reset_demo_data
) else (
  python -m app.reset_demo_data
)
