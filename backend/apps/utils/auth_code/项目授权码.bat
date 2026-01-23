@echo off
cd ..\..\..
d:
call .venv\Scripts\activate.bat
cd apps\utils\auth_code
python generator.py --payload-file payload_project.json --wrap-base64
echo.
pause >nul
cmd /k
