@echo off
cd ..\..\..
d:
call .venv\Scripts\activate.bat
cd apps\utils\auth_code
chcp 65001 >nul
for %%I in ("payload_project.json") do echo JSON路径: %%~fI
echo 授权信息:
python price_calc.py
type payload_project.json
echo.
python generator.py --payload-file payload_project.json --wrap-base64

echo.
pause >nul
cmd /k
