@echo off
chcp 65001 >nul
title 自动化工厂设备Agent

echo ========================================
echo    自动化工厂设备Agent启动脚本
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

:: 检查依赖是否安装
echo [信息] 检查Python依赖...
python -c "import requests, schedule, websocket" >nul 2>&1
if errorlevel 1 (
    echo [警告] 检测到缺少依赖，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请手动执行: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo [成功] 依赖安装完成
)

:: 检查配置文件
if not exist config.json (
    echo [警告] 未找到config.json，使用默认配置
)

echo.
echo [信息] 启动设备Agent...
echo [提示] 按 Ctrl+C 停止Agent
echo.

python device_agent.py

if errorlevel 1 (
    echo.
    echo [错误] Agent异常退出
    pause
)
