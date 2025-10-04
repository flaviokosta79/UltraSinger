@echo off
setlocal
cd ..
cd ..
py -3.10 -m venv .venv
SET VenvPythonPath=%CD%\.venv\Scripts\python.exe
call %VenvPythonPath% -m pip install -r requirements-windows.txt
call %VenvPythonPath% -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
endlocal