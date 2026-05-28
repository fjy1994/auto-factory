"""
自动化工厂 - 设备 Agent 服务

部署在连接 Android 设备的 Ubuntu 机器上，提供 HTTP 接口接收工厂下发的测试批次。
每收到一个批次，逐个执行各用例对应的 Python 测试脚本，收集结果返回给工厂。

启动:
    pip install fastapi uvicorn
    python agent_server.py --port 8000 --base-dir /home/user/test_scripts

配置环境变量:
    export AGENT_BASE_DIR=/home/user/test_scripts   # 测试脚本根目录
    export AGENT_PORT=8000                          # 监听端口
"""

import sys
import os
import subprocess
import time
import json
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("错误: 需要安装 fastapi 和 uvicorn")
    print("  pip install fastapi uvicorn")
    sys.exit(1)


# ============================================================
# 配置
# ============================================================
BASE_DIR = os.environ.get('AGENT_BASE_DIR', '/home/user/test_scripts')
HOST = os.environ.get('AGENT_HOST', '0.0.0.0')
PORT = int(os.environ.get('AGENT_PORT', '8000'))


# ============================================================
# 数据模型
# ============================================================
class CaseInfo(BaseModel):
    case_id: str
    script_path: str
    name: str = ""


class BatchRequest(BaseModel):
    task_id: int
    batch_index: int
    cases: list[CaseInfo]
    params: dict = {}


class BatchResponse(BaseModel):
    task_id: int
    batch_index: int
    results: list[dict]


# ============================================================
# FastAPI 应用
# ============================================================
app = FastAPI(
    title="Auto-Factory Agent",
    description="自动化工厂设备 Agent - 接收并执行测试批次",
    version="1.0.0",
)


def execute_script(script_path: str, case_id: str, params: dict) -> dict:
    """
    执行单个测试脚本，返回结果。

    执行逻辑:
        1. 拼接完整脚本路径 (BASE_DIR + script_path)
        2. 用 subprocess 运行 python <script_path>
        3. 捕获 stdout/stderr 和退出码
        4. 记录执行耗时

    Args:
        script_path: 脚本相对路径（如 tests/test_login.py）
        case_id: 用例编号（用于结果记录）
        params: 额外参数（会作为环境变量传递给脚本）

    Returns:
        dict: {case_id, status, error, duration}
    """
    full_path = os.path.join(BASE_DIR, script_path) if not os.path.isabs(script_path) else script_path

    if not os.path.exists(full_path):
        return {
            'case_id': case_id,
            'status': 'error',
            'error': f'脚本文件不存在: {full_path}',
            'duration': 0,
        }

    # 构建环境变量（传入用例参数）
    env = os.environ.copy()
    env['CASE_ID'] = case_id
    env['AGENT_BASE_DIR'] = BASE_DIR
    for key, value in params.items():
        env[f'TEST_PARAM_{key.upper()}'] = str(value)

    start_time = time.time()
    try:
        result = subprocess.run(
            ['python', full_path],
            capture_output=True,
            text=True,
            timeout=1800,  # 每个脚本最长执行 30 分钟
            env=env,
        )
        elapsed = round(time.time() - start_time, 2)

        if result.returncode == 0:
            return {
                'case_id': case_id,
                'status': 'passed',
                'error': '',
                'duration': elapsed,
                'output': result.stdout[-500:],  # 保留最后 500 字符
            }
        else:
            return {
                'case_id': case_id,
                'status': 'failed',
                'error': result.stderr[-1000:] or result.stdout[-1000:],
                'duration': elapsed,
            }

    except subprocess.TimeoutExpired:
        elapsed = round(time.time() - start_time, 2)
        return {
            'case_id': case_id,
            'status': 'error',
            'error': f'脚本执行超时（30分钟）',
            'duration': elapsed,
        }
    except Exception as e:
        elapsed = round(time.time() - start_time, 2)
        return {
            'case_id': case_id,
            'status': 'error',
            'error': str(e),
            'duration': elapsed,
        }


# ============================================================
# API 端点
# ============================================================
@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok", "base_dir": BASE_DIR}


@app.post("/execute_batch", response_model=BatchResponse)
def execute_batch(request: BatchRequest):
    """
    接收工厂下发的批次，逐个执行测试脚本，返回结果。

    工厂端调用示例:
    ```
    POST /execute_batch
    {
        "task_id": 1,
        "batch_index": 0,
        "cases": [
            {"case_id": "TC-001", "script_path": "tests/test_login.py", "name": "用户登录"},
            {"case_id": "TC-002", "script_path": "tests/test_register.py", "name": "用户注册"}
        ],
        "params": {
            "device_serial": "0123456789ABCDEF",
            "rom_version": "V2.0.1"
        }
    }
    ```
    """
    results = []
    total = len(request.cases)

    for i, case in enumerate(request.cases):
        print(f"[任务 {request.task_id}] 批次 {request.batch_index} - "
              f"执行 {i+1}/{total}: {case.case_id} ({case.name or case.script_path})")
        result = execute_script(case.script_path, case.case_id, request.params)
        results.append(result)
        print(f"  -> {result['status']} ({result['duration']}s)")

    return BatchResponse(
        task_id=request.task_id,
        batch_index=request.batch_index,
        results=results,
    )


@app.post("/execute_batch_async")
def execute_batch_async(request: BatchRequest):
    """
    异步模式：接收批次后立即返回受理，通过回调提交结果。
    工厂端需提供回调地址（通过 params.callback_url 传入）。
    """
    import threading
    callback_url = request.params.get('callback_url', '')

    def _run_and_callback():
        result = execute_batch(request)
        if callback_url:
            try:
                import requests as req
                req.post(callback_url, json=result.dict(), timeout=30)
            except Exception as e:
                print(f"回调失败: {e}")

    thread = threading.Thread(target=_run_and_callback, daemon=True)
    thread.start()

    return {
        "message": "已受理，结果将通过回调返回",
        "task_id": request.task_id,
        "batch_index": request.batch_index,
        "callback_url": callback_url,
    }


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    print(f"启动 Auto-Factory Agent")
    print(f"  脚本根目录: {BASE_DIR}")
    print(f"  监听地址:   http://{HOST}:{PORT}")
    print(f"  健康检查:   http://{HOST}:{PORT}/health")
    print(f"  执行端点:   POST http://{HOST}:{PORT}/execute_batch")
    uvicorn.run(app, host=HOST, port=PORT)
