$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

$python = Join-Path ".venv" "Scripts/python.exe"
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements-dev.txt

Write-Host "Setup complete. Run: .venv\Scripts\python -m password_toolkit --help"
