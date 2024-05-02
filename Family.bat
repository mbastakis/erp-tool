@echo off

echo Running Family
python3 ./scripts/main.py family

if %ERRORLEVEL% equ 0 (
    exit
) else (
    echo Error encountered. Press any key to continue...
    pause
)
