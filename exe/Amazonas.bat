@echo off

echo Running Amazonas
python3 ./scripts/main.py amazonas

if %ERRORLEVEL% equ 0 (
    exit
) else (
    echo Error encountered. Press any key to continue...
    pause
)
