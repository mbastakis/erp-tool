@echo off

echo Running Artelibre
python3 ./scripts/main.py artelibre

if %ERRORLEVEL% equ 0 (
    exit
) else (
    echo Error encountered. Press any key to continue...
    pause
)
