# Activation script for Windows PowerShell
Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host "Python location: $env:VIRTUAL_ENV\Scripts\python.exe"
Write-Host ""
Write-Host "To deactivate, type: deactivate" -ForegroundColor Yellow
