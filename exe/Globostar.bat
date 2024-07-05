@echo off

echo Running Globostar
python3 ./scripts/main.py globostar

if %ERRORLEVEL% equ 0 (
    exit
) else (
    echo Error encountered. Press any key to continue...
    pause
)