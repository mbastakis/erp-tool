@echo off

echo Running Lino
python3 ./scripts/main.py lino

if %ERRORLEVEL% equ 0 (
    exit
) else (
    echo Error encountered. Press any key to continue...
    pause
)