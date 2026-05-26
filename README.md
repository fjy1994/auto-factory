# 自动化工厂系统

一套完整的自动化测试工厂系统，包含前端、后端和设备Agent。

## 系统架构

```
┌─────────────────────┐
│   前端管理界面      │  Vue3 + Element Plus
│   (auto-factory-frontend)
└──────────┬──────────┘
           │  HTTP / WebSocket
           ▼
┌─────────────────────┐
│   后端服务          │  FastAPI + SQLite
│   (backend)
└──────────┬──────────┘
           │  WebSocket 控制
           ▼
┌─────────────────────┐
│   设备Agent         │  Python + ADB
│   (agent)           │  ↓ ↓ ↓
│      ┌───────────────────────┐
│      │  Android 设备集群     │
│      │  ┌─────┐ ┌─────┐     │
│      │  │设备1│ │设备2│ ...  │
│      │  └─────┘ └─────┘     │
│      └───────────────────────┘
└─────────────────────┘
```

## 目录结构

```
auto-factory/
├── auto-factory-frontend/    # 前端项目
│   ├── src/
│   │   ├── views/            # 页面组件
│   │   │   ├── Device/       # 设备管理页
│   │   │   ├── Branch/       # 分支管理页
│   │   │   ├── Task/         # 任务中心
│   │   │   └── TestCase/     # 用例管理页
│   │   ├── types/            # TS类型定义
│   │   └── api/              # API接口封装
│   └── package.json
│
├── backend/                   # 后端服务
│   ├── main.py               # 主程序（所有接口和逻辑）
│   ├── requirements.txt      # Python依赖
│   ├── start_server.bat      # Windows一键启动
│   ├── factory.db            # SQLite数据库（自动创建）
│   └── README.md
│
└── agent/                     # 设备Agent
    ├── device_agent.py       # Agent主程序
    ├── requirements.txt      # Python依赖
    ├── start_agent.bat       # 一键启动脚本
    └── README.md
```

## 快速启动

### 1. 启动后端服务

```bash
cd auto-factory-backend
pip install -r requirements.txt
python main.py
```

**或者双击：** `backend/start_server.bat`

启动后访问：
- API地址: http://localhost:8000
- 接口文档: http://localhost:8000/docs

### 2. 启动前端

```bash
cd auto-factory-backend-frontend
npm install
npm run dev
```

启动后访问: http://localhost:5173

### 3. 启动设备Agent

在连接Android设备的机器上运行：

```bash
cd agent
pip install -r requirements.txt
python device_agent.py
```

**或者双击：** `agent/start_agent.bat`

## 功能模块

### 📱 设备管理
- 设备自动发现和注册
- 设备状态实时监控
- 支持多执行机分布式部署
- 设备远程控制（重启等）
- 统计信息展示（空闲/忙碌/离线/异常）

### 🌿 分支管理
- 分支配置管理
- 版本号正则匹配规则
- 禁用/启用分支开关
- 分支下任务类型配置

### 📋 任务中心
- 待执行版本队列
- 任务全生命周期管理
- 实时任务进度展示
- 支持任务取消、重跑
- 按版本维度聚合展示

### 📝 测试用例管理
- 用例库管理
- 支持按模块、优先级筛选
- 支持Excel批量导入
- 用例详情查看和编辑

### 🔌 WebSocket实时通信
- Agent与后端长连接
- 实时下发控制指令
- 任务进度实时上报
- 执行机在线状态感知

## 技术栈

### 前端
- Vue 3 (Composition API)
- TypeScript
- Element Plus
- Pinia 状态管理
- Vue Router

### 后端
- FastAPI 高性能异步框架
- SQLite 轻量数据库（无需安装）
- WebSocket 实时通信
- Uvicorn ASGI 服务器

### Agent
- Python 3
- ADB 设备控制
- WebSocket 客户端
- 定时任务调度

## 数据库设计

后端使用 SQLite 单文件数据库，包含以下表：

| 表名 | 说明 |
|------|------|
| devices | 设备信息表 |
| executors | 执行机信息表 |
| branches | 分支配置表 |
| tasks | 任务表 |
| version_queue | 待执行版本队列表 |
| test_cases | 测试用例表 |

## API接口预览

### 核心接口

| 模块 | 接口 | 说明 |
|------|------|------|
| 设备 | GET /api/v1/devices | 获取设备列表 |
| 设备 | POST /api/v1/devices/{serial}/reboot | 重启设备 |
| 分支 | GET /api/v1/branches | 获取分支列表 |
| 分支 | POST /api/v1/branches | 创建分支 |
| 任务 | GET /api/v1/tasks | 获取任务列表 |
| 任务 | POST /api/v1/tasks | 创建任务 |
| 队列 | GET /api/v1/version-queue | 待执行队列 |
| 用例 | GET /api/v1/test-cases | 用例列表 |
| Agent | POST /api/v1/agent/report | 设备上报接口 |
| WS | /ws/agent | Agent WebSocket连接 |

完整接口文档见: http://localhost:8000/docs

## 部署说明

### 单机部署（推荐）

后端、前端、Agent都在同一台机器上运行：

1. 启动后端服务
2. 启动前端
3. 连接Android设备，启动Agent

### 分布式部署

```
机器A: 后端 + 前端
机器B: Agent + 设备1, 设备2, ...
机器C: Agent + 设备3, 设备4, ...
```

**修改Agent配置:**

编辑 `agent/device_agent.py`:
```python
self.server_url = 'http://机器A的IP:8000'
self.ws_url = 'ws://机器A的IP:8000/ws/agent'
```

## 常见问题

### Q: 后端启动失败？
A: 检查 8000 端口是否被占用，或修改 main.py 中的端口号。

### Q: Agent上报失败？
A: 检查 backend 的 server_url 地址是否正确，网络是否连通。

### Q: 设备不显示？
A: 确认设备已开启USB调试，ADB能识别设备（执行 `adb devices` 查看）。

### Q: 数据库数据丢了？
A: 删除 factory.db 文件，重启后端会自动重建。

## 开发说明

### 添加新的API接口

在 `backend/main.py` 中添加新的路由函数即可。

### 修改前端API地址

编辑 `auto-factory-frontend/src/api/index.ts`:
```typescript
const API_BASE = 'http://你的后端IP:8000'
```

## License

MIT
