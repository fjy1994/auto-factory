# 自动化工厂 - 前端

自动化工厂前端项目，基于 Vue 3 + TypeScript + Element Plus 构建。

## 功能模块

- 📊 **仪表盘**：系统概览、统计数据、图表展示
- 📱 **设备管理**：设备列表、设备详情、设备状态监控
- 🔀 **分支管理**：分支配置、任务类型配置
- 📋 **任务管理**：任务列表、任务详情、实时日志、任务操作
- 📈 **报告中心**：测试报告列表、报告下载
- ⚙️ **系统设置**：邮件服务配置

## 技术栈

- Vue 3 (Composition API)
- TypeScript
- Vite
- Element Plus
- Vue Router
- Pinia
- ECharts
- Axios

## 快速开始

### 安装依赖

```bash
cd auto-factory-backend-frontend
npm install
```

### 开发模式

```bash
npm run dev
```

### 生产构建

```bash
npm run build
```

## 项目结构

```
src/
├── views/              # 页面组件
│   ├── Dashboard/      # 仪表盘
│   ├── Device/         # 设备管理
│   ├── Branch/         # 分支管理
│   ├── Task/           # 任务管理
│   ├── Report/         # 报告中心
│   └── Settings/       # 系统设置
├── components/         # 公共组件
├── stores/             # Pinia 状态管理
├── router/             # 路由配置
├── types/              # TypeScript 类型定义
├── utils/              # 工具函数
├── App.vue             # 根组件
└── main.ts             # 入口文件
```

## 接口代理

开发环境接口代理配置在 `vite.config.ts` 中，默认代理 `/api` 到 `http://localhost:8000`。
