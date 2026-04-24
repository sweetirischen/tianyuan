@echo off
chcp 65001 >nul
title 天垣远程服务 - Cloudflare Tunnel

echo ═══════════════════════════════════════════════════════════
echo              天垣远程服务 - 启动中...
echo ═══════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM 检查cloudflared
if not exist "cloudflared.exe" (
    echo [错误] 未找到 cloudflared.exe
    pause
    exit /b 1
)

echo [启动] 正在启动本地服务...
echo.

REM 后台启动Python服务
start /b python server.py

REM 等待服务启动
timeout /t 3 /nobreak >nul

echo [启动] 正在建立Cloudflare隧道...
echo.
echo ═══════════════════════════════════════════════════════════
echo   远程访问地址将在下方显示
echo   格式: https://xxx.trycloudflare.com
echo   
echo   密码: ADY0X9
echo ═══════════════════════════════════════════════════════════
echo.

REM 启动Cloudflare Tunnel
cloudflared.exe tunnel --url http://localhost:5000

pause
