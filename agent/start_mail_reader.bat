@echo off
chcp 65001 >nul
title 自动化工厂 - 极简邮件扫描器

echo ========================================
echo    极简邮件扫描器 (守护模式)
echo ========================================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python
    pause
    exit /b 1
)

:: 检查依赖
echo [信息] 检查依赖...
python -c "import win32com.client, requests" >nul 2>&1
if errorlevel 1 (
    echo [警告] 正在安装依赖...
    pip install pywin32 requests
)

:: 检查Outlook
echo [信息] 检查Outlook...
tasklist /FI "IMAGENAME eq OUTLOOK.EXE" 2>NUL | find /I /N "OUTLOOK.EXE">NUL
if errorlevel 1 (
    echo [警告] Outlook未运行，正在启动...
    start outlook.exe
    timeout /t 5 /nobreak >nul
)

echo.
echo [信息] 启动邮件扫描器...
echo.
echo 提示: 每300秒扫描一次最近1小时的邮件
echo 按 Ctrl+C 停止
echo.

python mail_reader.py

pause
