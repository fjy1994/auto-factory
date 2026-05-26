# 自动化工厂 - 设备Agent

## 功能说明

设备Agent部署在每台执行机器上，负责：
- 定时扫描本地USB连接的Android设备
- 通过ADB获取设备详细信息（ROM版本、浏览器版本等）
- 上报设备信息到主服务
- 通过WebSocket接收并执行主服务下发的指令（重启、刷机等）

## 环境要求

- Python 3.8+
- ADB (Android Debug Bridge)
- Windows/Linux/macOS

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 配置ADB环境

确保ADB已正确安装并配置到环境变量中。

验证ADB：
```bash
adb version
adb devices
```

### 3. 修改主服务地址（可选）

如果主服务不是本机，修改 `device_agent.py` 中以下配置：

```python
# 第43-45行左右
self.server_url = 'http://你的服务器IP:8000'
self.ws_url = 'ws://你的服务器IP:8000/ws/agent'
```

**注：执行机ID自动使用本机IP地址，无需手动配置。**

## 运行方式

### Windows

**方式一：直接运行（推荐）**
```bash
python device_agent.py
```

**方式二：使用启动脚本（推荐后台运行）**
```batch
start_agent.bat
```

**方式三：隐藏窗口运行（后台）**
```batch
start_agent_hidden.vbs
```

### Linux/macOS

```bash
python3 device_agent.py
```

## 上报数据格式

Agent每N秒向主服务上报一次设备信息：

```json
{
  "executorId": "executor_001",
  "executorIp": "192.168.1.100",
  "reportTime": "2024-01-15T10:30:00.000000",
  "devices": [
    {
      "serial": "ABC123DEF456",
      "romVersion": "Pixel 7 - TQ3A.230605.010",
      "browserVersion": "Chrome 118.0.5993.70",
      "executorIp": "192.168.1.100",
      "status": "idle",
      "lastReportTime": "2024-01-15T10:30:00.000000",
      "remark": ""
    }
  ]
}
```

## 支持的指令

Agent通过WebSocket接收以下指令：

| 指令 | 说明 |
|------|------|
| `ping` | 心跳检测 |
| `reboot` | 重启指定设备 |
| `flash_rom` | 执行刷机操作 |

## 日志说明

运行日志会输出到：
- 控制台（实时显示）
- `device_agent.log` 文件

## API接口

### 设备上报接口

**POST** `/api/v1/agent/report`

**请求体**：
```json
{
  "executorId": "192.168.1.100",       // 执行机ID = IP地址
  "executorIp": "192.168.1.100",
  "reportTime": "2024-01-15T10:30:00.000000",
  "devices": [...]
}
```

### WebSocket接口

**连接地址**：`ws://your-server:8000/ws/agent`

**注册消息（连接建立后发送）**：
```json
{
  "type": "register",
  "executorId": "executor_001",
  "executorIp": "192.168.1.100"
}
```

**接收指令格式**：
```json
{
  "command": "reboot",
  "deviceSerial": "ABC123DEF456",
  "taskId": 123
}
```

**上报进度格式**：
```json
{
  "type": "task_progress",
  "taskId": 123,
  "deviceSerial": "ABC123DEF456",
  "status": "running",
  "progress": 50,
  "message": "刷机中..."
}
```

## 常见问题

### Q: ADB无法识别设备？
A: 请检查：
1. 设备是否开启了USB调试
2. 数据线是否正常
3. 是否授权了该电脑的RSA指纹
4. 执行 `adb kill-server && adb start-server`

### Q: 上报失败？
A: 检查：
1. 主服务是否正常运行
2. 网络连接是否正常
3. `config.json` 中的 `server_url` 是否正确

### Q: 如何查看Agent是否正常运行？
A: 
1. 查看日志文件 `device_agent.log`
2. 检查主服务上是否有该执行机的设备数据
3. 观察控制台是否有定时上报的日志

## 目录结构

```
agent/
├── device_agent.py          # 主程序（所有配置已写在代码中）
├── requirements.txt         # Python依赖
├── start_agent.bat          # Windows启动脚本
├── start_agent_hidden.vbs   # Windows后台启动脚本
├── stop_agent.bat           # 停止Agent脚本
├── test_agent.py            # 环境检测脚本
├── device_agent.log         # 运行日志（自动生成）
└── README.md                # 说明文档
```

## 扩展开发

### 添加新的设备信息采集

在 `get_device_info` 方法中添加新的采集逻辑：

```python
def get_device_info(self, serial: str) -> Dict:
    return {
        'serial': serial,
        'romVersion': self.get_device_rom_version(serial),
        'browserVersion': self.get_device_browser_version(serial),
        'newField': self.get_new_field(serial),  # 新增字段
        'executorIp': self.executor_ip,
        'status': 'idle',
        'lastReportTime': datetime.now().isoformat(),
        'remark': ''
    }
```

### 添加新的指令处理

在 `on_message` 方法中添加新的指令分支：

```python
def on_message(self, ws, message):
    data = json.loads(message)
    command = data.get('command')
    
    if command == 'new_command':
        self._handle_new_command(data)
    # ... 其他指令
```
