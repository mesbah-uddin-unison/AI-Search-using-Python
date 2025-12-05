@echo off
REM Activation script for Windows Command Prompt
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Virtual environment activated!
echo Python location: %VIRTUAL_ENV%\Scripts\python.exe
echo.
echo To deactivate, type: deactivate
