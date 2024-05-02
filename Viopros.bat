@echo off

echo Running Viopros
python3 ./scripts/viopros.py 

if %ERRORLEVEL% equ 0 (
    exit
) else (
    echo Error encountered. Press any key to continue...
    pause
)