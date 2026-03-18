# Format and fix lint (PowerShell)
Set-Location (Join-Path $PSScriptRoot "..")

python -m ruff check app tests --fix
python -m ruff format app tests
