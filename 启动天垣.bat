@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   天垣 TianYuan - 启动
echo ========================================
echo.
echo 正在检查 Ollama 状态...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] Ollama 未运行，正在启动...
    start "" ollama serve
    timeout /t 3 >nul
)
echo.
echo Ollama 状态: 运行中
echo.
echo 正在打开天垣首页...
start "" "%~dp0docs\index.html"
echo.
echo ========================================
echo   天垣已启动！
echo   本地大脑: http://localhost:11434
echo   按 Ctrl+C 关闭
echo ========================================
echo.
pause
