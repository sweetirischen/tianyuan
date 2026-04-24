@echo off
chcp 65001 >nul
title 天垣完整服务

cd /d "%~dp0"

echo ═══════════════════════════════════════════════════════════
echo              天垣服务启动器
echo ═══════════════════════════════════════════════════════════
echo.
echo 请选择启动模式:
echo.
echo   [1] 本地模式 - 仅本地访问 (localhost:5000)
echo   [2] 远程模式 - 可外网访问 (Cloudflare Tunnel)
echo   [3] 退出
echo.
set /p choice="请输入选项 (1/2/3): "

if "%choice%"=="1" goto local
if "%choice%"=="2" goto remote
if "%choice%"=="3" exit
goto end

:local
echo.
echo [本地模式] 启动中...
python server.py
goto end

:remote
echo.
echo [远程模式] 启动中...
echo.
echo 启动本地服务...
start /b python server.py
timeout /t 2 /nobreak >nul
echo.
echo 建立Cloudflare隧道...
echo.
echo ═══════════════════════════════════════════════════════════
echo   远程地址将在下方显示，格式:
echo   https://xxx.trycloudflare.com
echo   
echo   密码: aheng
echo ═══════════════════════════════════════════════════════════
echo.
cloudflared.exe tunnel --url http://localhost:5000
goto end

:end
pause
