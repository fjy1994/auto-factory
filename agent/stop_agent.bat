@echo off
chcp 65001 >nul
title 停止设备Agent

echo ========================================
echo    停止设备Agent
echo ========================================
echo.

echo [信息] 正在查找并停止Agent进程...
taskkill /f /im python.exe /fi "windowtitle eq 自动化工厂设备Agent*" 2>nul

if errorlevel 1 (
    echo [提示] 未找到正在运行的Agent进程
) else (
    echo [成功] Agent进程已停止
)

echo.
pause
