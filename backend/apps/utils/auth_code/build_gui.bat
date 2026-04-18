@echo off
setlocal
cd /d %~dp0
chcp 65001 >nul

set "BACKEND_DIR=%~dp0..\..\.."
set "VENV_ACTIVATE=%BACKEND_DIR%\.venv\Scripts\activate.bat"

if not exist "%VENV_ACTIVATE%" (
  echo 未找到虚拟环境：%BACKEND_DIR%\.venv
  echo 请先在 backend 目录创建 .venv 后再构建。
  pause
  exit /b 1
)

call "%VENV_ACTIVATE%"

python -m ensurepip --upgrade >nul 2>nul
if errorlevel 1 (
  echo 无法初始化 pip，请先修复 .venv 环境。
  pause
  exit /b 1
)

python -m pip install --upgrade pip
python -m pip install pyinstaller pycryptodome

python -m PyInstaller --noconfirm --onefile --windowed --name 授权码生成器 auth_code_gui.py

echo.
echo 构建完成，输出目录：%~dp0dist
pause
endlocal
