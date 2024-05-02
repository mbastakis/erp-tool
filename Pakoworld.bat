@echo off

echo Running PakoWorld
python3 ./scripts/main.py pakoworld

if %ERRORLEVEL% equ 0 (
    exit
) else (
    echo Error encountered. Press any key to continue...
    pause
)