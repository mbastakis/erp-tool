@echo off

echo Running Beautyhome
python3 ./scripts/main.py beautyhome

if %ERRORLEVEL% equ 0 (
    exit
) else (
    echo Error encountered. Press any key to continue...
    pause
)
