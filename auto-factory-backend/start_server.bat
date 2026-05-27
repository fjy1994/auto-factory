@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo 启动后端服务...
python manage.py runserver 18789 --noreload
pause
