@echo off
cd /d "%~dp0\.."
python -m ruff check app tests --fix
python -m ruff format app tests
