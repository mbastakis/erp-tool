@echo off

echo Running LittleBigThings...
python3 ./scripts/main.py littlebigthings

if %ERRORLEVEL% equ 0 (
    exit
) else (
    echo Error encountered. Press any key to continue...
    pause
)