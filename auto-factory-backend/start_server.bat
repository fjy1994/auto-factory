@echo off
chcp 65001 >nul
title 自动化工厂后端 (Django)

echo ========================================
echo    自动化工厂后端服务启动脚本
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
python -c "import django; import rest_framework; import channels; import corsheaders" >nul 2>&1
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

:: 检查MySQL连接
echo [信息] 检查MySQL连接...
python -c "import MySQLdb; MySQLdb.connect(host='127.0.0.1', user='root', passwd='123456', db='mysql')" >nul 2>&1
if errorlevel 1 (
    echo [警告] MySQL连接失败，请检查:
    echo   1. MySQL服务是否启动
    echo   2. 用户名/密码是否正确 (root/123456)
    echo   3. 是否已创建数据库: auto_factory
    echo.
    echo 提示: 如果MySQL密码不对，请修改 backend/settings.py 中的数据库密码
    echo.
    set /p answer="是否继续？(y/n): "
    if /i not "%answer%"=="y" (
        pause
        exit /b 1
    )
)

:: 执行数据库迁移
echo.
echo [信息] 执行数据库迁移...
python manage.py makemigrations
python manage.py migrate

echo.
echo =====================================================
echo   后端服务启动成功！
echo =====================================================
echo.
echo 服务地址:  http://localhost:8000
echo API文档:   http://localhost:8000/api/v1/
echo 管理后台:  http://localhost:8000/admin/
echo.
echo 提示: 首次使用请创建管理员账号:
echo   python manage.py createsuperuser
echo.
echo 按 Ctrl+C 停止服务
echo =====================================================
echo.

python manage.py runserver 0.0.0.0:8000

if errorlevel 1 (
    echo.
    echo [错误] 服务异常退出
    pause
)
