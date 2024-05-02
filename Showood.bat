@echo off

echo Running Showood
python3 ./scripts/main.py showood

if %ERRORLEVEL% equ 0 (
    exit
) else (
    echo Error encountered. Press any key to continue...
    pause
)