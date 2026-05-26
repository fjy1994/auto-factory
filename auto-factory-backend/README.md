# 自动化工厂 - 后端服务 (Django + MySQL)

## 技术栈

- **Web框架**: Django 4.2
- **REST API**: Django REST Framework
- **数据库**: MySQL 8.0
- **WebSocket**: Django Channels
- **CORS**: django-cors-headers

## 环境要求

- Python 3.8+
- MySQL 5.7+ / 8.0+

## 快速启动

### 1. 配置MySQL

启动MySQL服务，创建数据库：

```sql
CREATE DATABASE IF NOT EXISTS auto_factory DEFAULT CHARACTER SET utf8mb4;
```

### 2. 配置数据库连接

编辑 `backend/settings.py`，修改数据库配置：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'auto_factory',
        'USER': 'root',          # 你的MySQL用户名
        'PASSWORD': '123456',   # 你的MySQL密码
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 执行数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 创建管理员账号（可选）

```bash
python manage.py createsuperuser
```

### 6. 启动服务

```bash
python manage.py runserver 0.0.0.0:8000
```

**或者双击：** `start_server.bat`

## 服务地址

启动成功后访问：

| 服务 | 地址 |
|------|------|
| API接口 | http://localhost:8000 |
| API文档 (Browsable API) | http://localhost:8000/api/v1/ |
| Django Admin 管理后台 | http://localhost:8000/admin/ |
| WebSocket | ws://localhost:8000/ws/agent/ |

## 数据库表结构

| 表名 | 说明 |
|------|------|
| devices | 设备表 |
| executors | 执行机表 |
| branches | 分支表 |
| tasks | 任务表 |
| version_queue | 待执行版本队列表 |
| test_cases | 测试用例表 |

## API接口列表

### 健康检查

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/health/` | 健康检查 |

### 设备管理 (RESTful)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/devices/` | 获取设备列表 |
| POST | `/api/v1/devices/` | 创建设备 |
| GET | `/api/v1/devices/{id}/` | 获取设备详情 |
| PUT | `/api/v1/devices/{id}/` | 更新设备 |
| DELETE | `/api/v1/devices/{id}/` | 删除设备 |
| POST | `/api/v1/devices/{serial}/reboot/` | 远程重启设备 |

### 分支管理 (RESTful)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/branches/` | 获取分支列表 |
| POST | `/api/v1/branches/` | 创建分支 |
| GET | `/api/v1/branches/{id}/` | 获取分支详情 |
| PUT | `/api/v1/branches/{id}/` | 更新分支 |
| DELETE | `/api/v1/branches/{id}/` | 删除分支 |

### 任务管理 (RESTful)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/tasks/` | 获取任务列表 |
| POST | `/api/v1/tasks/` | 创建任务 |
| GET | `/api/v1/tasks/{id}/` | 获取任务详情 |
| PUT | `/api/v1/tasks/{id}/` | 更新任务 |
| DELETE | `/api/v1/tasks/{id}/` | 删除任务 |
| PUT | `/api/v1/tasks/{id}/cancel/` | 取消任务 |
| PUT | `/api/v1/tasks/{id}/rerun/` | 重跑任务 |

### 待执行队列 (RESTful)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/version-queue/` | 获取队列列表 |
| POST | `/api/v1/version-queue/` | 添加版本到队列 |
| POST | `/api/v1/version-queue/{id}/create-tasks/` | 从队列创建任务 |
| DELETE | `/api/v1/version-queue/{id}/` | 删除队列项 |

### 测试用例管理 (RESTful)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/test-cases/` | 获取用例列表 |
| POST | `/api/v1/test-cases/` | 创建用例 |
| GET | `/api/v1/test-cases/{id}/` | 获取用例详情 |
| PUT | `/api/v1/test-cases/{id}/` | 更新用例 |
| DELETE | `/api/v1/test-cases/{id}/` | 删除用例 |
| GET | `/api/v1/test-cases/modules/` | 获取所有模块列表 |

### 执行机管理 (RESTful)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/executors/` | 获取执行机列表 |
| POST | `/api/v1/executors/{id}/command/` | 下发指令 |

### Agent上报接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/agent/report/` | Agent设备上报接口 |

## Agent上报数据格式

```json
{
  "executorId": "192.168.1.100",
  "executorIp": "192.168.1.100",
  "reportTime": "2024-01-15T10:30:00.000000",
  "devices": [
    {
      "serial": "ABC123DEF456",
      "romVersion": "TQ3A.230605.010",
      "browserVersion": "Chrome 118.0.5993.70",
      "executorIp": "192.168.1.100",
      "status": "idle",
      "remark": ""
    }
  ]
}
```

## WebSocket指令格式

### 注册消息（Agent连接后发送）
```json
{
  "type": "register",
  "executorId": "192.168.1.100"
}
```

### 重启设备指令
```json
{
  "command": "reboot",
  "deviceSerial": "ABC123DEF456",
  "taskId": 123
}
```

## 目录结构

```
backend/
├── manage.py              # Django入口文件
├── requirements.txt     # Python依赖
├── start_server.bat     # Windows一键启动脚本
├── init_db.sql          # 数据库初始化脚本
├── README.md            # 本文档
│
├── backend/             # Django项目配置
│   ├── __init__.py
│   ├── settings.py    # 配置文件（含数据库配置）
│   ├── urls.py        # 路由配置
│   ├── asgi.py        # ASGI配置（WebSocket）
│   └── wsgi.py        # WSGI配置
│
└── api/               # API应用
    ├── __init__.py
    ├── models.py      # 数据模型
    ├── serializers.py # 序列化器
    ├── views.py       # 视图函数
    ├── consumers.py   # WebSocket消费者
    ├── routing.py     # WebSocket路由
    ├── admin.py       # 管理后台配置
    └── apps.py        # 应用配置
```

## 常见问题

### Q: MySQL连接失败？
A: 检查：
1. MySQL服务是否启动
2. settings.py 中的用户名密码是否正确
3. 数据库 auto_factory 是否已创建
4. 防火墙是否允许3306端口

### Q: 端口被占用？
A: 修改启动命令的端口：
```bash
python manage.py runserver 0.0.0.0:8080
```

### Q: 如何访问管理后台？
A: 先创建超级管理员账号：
```bash
python manage.py createsuperuser
```
然后访问 http://localhost:8000/admin/

### Q: Agent连不上后端？
A: 检查：
1. Django服务正常启动
2. Agent中的 server_url 地址正确
3. 检查防火墙和端口

### Q: 如何重置数据库？
```bash
# 删除数据库
drop database auto_factory;
# 重新创建
create database auto_factory default character set utf8mb4;
# 重新迁移
python manage.py migrate
```
