@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -m venv .venv
  call .venv\Scripts\activate.bat
  python -m pip install --upgrade pip
  pip install -r studio\requirements.txt
) else (
  call .venv\Scripts\activate.bat
)
python -m studio.desktop
