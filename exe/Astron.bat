@echo off

echo Running Astron
python3 ./scripts/main.py astron

if %ERRORLEVEL% equ 0 (
    exit
) else (
    echo Error encountered. Press any key to continue...
    pause
)