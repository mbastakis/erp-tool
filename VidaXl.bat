@echo off

echo Running VidaXl
python3 ./scripts/main.py vidaxl

if %ERRORLEVEL% equ 0 (
    exit
) else (
    echo Error encountered. Press any key to continue...
    pause
)