// ======== 设备管理 ========

export interface Device {
  id: number
  serial: string
  model?: string
  romVersion?: string
  browserVersion?: string
  executorIp?: string
  status: 'idle' | 'busy' | 'flashing' | 'offline'
  remark?: string
  lastReportTime?: string
  createdAt?: string
}

// ======== 分支管理 ========

export interface Branch {
  id: number
  name: string
  versionPattern?: string
  mailTitlePattern?: string
  disabled?: boolean
  createdAt?: string
}

// ======== 任务定义（TaskDef，分支下挂的任务模板）========

export interface TaskDef {
  id: number
  branchId: number
  name: string
  scriptPath?: string
  deviceSelectType: 'auto' | 'manual'
  deviceQuantity: number
  deviceModels: string[]
  deviceIds: number[]
  caseSetIds: number[]
  batchSize: number
  createdAt: string
}

// ======== 刷机管理 ========

export interface FlashingStep {
  name: string
  status: 'pending' | 'running' | 'success' | 'failed'
  retryCount?: number
  errorMessage?: string
}

export interface FlashingProcess {
  id: number
  deviceId: number
  deviceSerial: string
  deviceModel?: string
  versionLabel?: string
  rom?: string
  status: 'pending' | 'running' | 'success' | 'failed'
  steps: FlashingStep[]
  retryCount?: number
  errorMessage?: string
  createdAt: string
  updatedAt: string
}

// ======== 版本跟踪 ========

export interface VersionTask {
  id: number
  name: string
  status: 'queued' | 'running' | 'completed'
  progress?: number
  passCount?: number
  failCount?: number
  totalCount?: number
  passRate?: number
}

export interface Version {
  id: number
  branchId: number
  branchName: string
  version: string
  /** 0=NO_DEVICE / 1=QUEUED / 2=FLASHING / 3=FLASH_FAILED / 4=TESTING / 5=COMPLETED / 6=OBSOLETED */
  status: number
  flashingTaskIds?: number[]
  passCount?: number
  failCount?: number
  totalCount?: number
  passRate?: number
  tasks?: VersionTask[]
  createdAt: string
}

// ======== 任务中心 ========

export interface CaseResult {
  caseId: string
  status: 'passed' | 'failed'
  errorMessage?: string
  duration?: number
  startTime?: string
  endTime?: string
}

export interface Task {
  id: number
  name: string
  versionLabel?: string
  branchName?: string
  status: 'queued' | 'running' | 'completed'
  progress: number
  passRate?: number
  totalCount?: number
  passCount?: number
  failCount?: number
  startTime?: string
  endTime?: string
  createdAt: string
}

// ======== 用例管理 ========

export interface TestCase {
  id: number
  caseId: string
  name: string
  module: string
  priority: 'L0' | 'L1' | 'L2' | 'L3' | 'L4'
  precondition?: string
  steps: string
  expected: string
  creator: string
  createdAt?: string
}

// ======== 用例集管理 ========

export interface CaseSet {
  id: number
  name: string
  description: string
  caseIds: number[]
  caseCount: number
  createdAt: string
}

// ======== 仪表盘 ========

export interface DashboardStats {
  deviceStats: {
    total: number
    idle: number
    busy: number
    offline: number
  }
  versionCoverage: {
    completed: number
    testing: number
    queued: number
    noDevice: number
    flashFailed: number
    obsoleted: number
  }
  recentTasks: {
    todayCompleted: number
    todayFailed: number
    running: number
  }
}

// ======== 通用分页/响应 ========

export interface ApiResponse {
  code: number
  message: string
  id?: number
}
