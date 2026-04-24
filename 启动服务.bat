@echo off
chcp 65001 >nul
title 天垣本地服务

echo ═══════════════════════════════════════════════════════════
echo              天垣本地服务 - 启动中...
echo ═══════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查依赖
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装依赖...
    pip install flask flask-cors psutil -q
)

REM 启动服务
echo [启动] 服务正在运行...
echo.
python server.py

pause
