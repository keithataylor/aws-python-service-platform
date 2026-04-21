$ErrorActionPreference = "Stop"

& "$PSScriptRoot\run-test-db-setup.ps1"
& ".\venv\Scripts\python.exe" -m pytest -m integration