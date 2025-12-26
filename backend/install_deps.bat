@echo off
REM ISW Backend 依赖安装脚本 (Windows CMD/Batch)
REM 此脚本会自动处理 PowerShell 执行策略问题并运行 PowerShell 安装脚本
REM 使用方法: install_deps.bat

echo 正在启动依赖安装脚本...
echo.

REM 使用 PowerShell 运行脚本，并绕过执行策略
powershell -ExecutionPolicy Bypass -File "%~dp0install_deps.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 安装过程中出现错误！
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo 安装完成！
pause


