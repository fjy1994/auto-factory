// 设备相关
export interface Device {
  id: number
  serial: string
  romVersion: string
  status: 'idle' | 'busy' | 'flashing' | 'offline' | 'error'
  executorIp: string
  browserVersion: string
  remark: string
  lastReportTime: string
}

// 分支相关
export interface Branch {
  id: number
  name: string
  versionPattern: string
  disabled: boolean
  createdAt: string
  tasks: TaskConfig[]
}

export interface TaskConfig {
  id: number
  name: string
  scriptPath: string
  minDeviceCount: number
  maxDeviceCount: number
  casePattern: string
}

// 转测版本队列
export interface VersionQueue {
  id: number
  branchId: number
  branchName: string
  version: string
  models: string[]
  status: 'waiting_rom' | 'waiting_device' | 'pending'
  reason: string
  receivedAt: string
  expectedTasks: string[]
}

// 任务相关（已整合报告数据）
export interface Task {
  id: number
  name: string
  branchId: number
  branchName: string
  version: string
  model: string
  taskType: string
  status: 'queued' | 'running' | 'success' | 'failed' | 'error' | 'cancelled'
  progress: number
  deviceId: number
  deviceSerial: string
  startTime: string
  endTime: string
  createdAt: string
  // 报告相关字段（已完成任务才有）
  passRate?: number
  totalCount?: number
  passCount?: number
  failCount?: number
  skipCount?: number
  errorCount?: number
  duration?: number
}

// 邮件服务状态
export interface MailServiceStatus {
  running: boolean
  connected: boolean
  email: string
  pollInterval: number
  lastHeartbeat: string
}

// 测试用例
export interface TestCase {
  id: number
  caseId: string
  name: string
  module: string
  priority: 'high' | 'medium' | 'low'
  steps: string
  expected: string
  creator: string
  createTime: string
}

// 邮件配置
export interface MailConfig {
  email: string
  username: string
  password: string
  server?: string
  pollInterval: number
}
