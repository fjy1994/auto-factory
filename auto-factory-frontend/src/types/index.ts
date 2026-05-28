// 刷机步骤定义
export interface FlashingStep {
  key: 'download_rom' | 'flash' | 'boot_setup' | 'wifi_login'
  name: string
  status: 'pending' | 'running' | 'success' | 'failed'
  message?: string
  errorMessage?: string
  startedAt?: string
  endedAt?: string
  retryCount?: number
  progress?: number
}

// 刷机过程
export interface FlashingProcess {
  id: number
  branchId: number
  branchName: string
  deviceId: number
  deviceSerial: string
  model: string
  romVersion: string
  status: 'pending' | 'flashing' | 'success' | 'failed'
  steps: FlashingStep[]
  currentStepIndex: number
  retryCount?: number
  errorMessage?: string
  createdAt: string
  updatedAt: string
}

// 分支任务配置
export interface BranchTaskConfig {
  id: number
  branchId: number
  name: string
  scriptPath?: string
  deviceLimit?: string
  caseSets: number[]
  batchSize: number
  order: number
  createdAt: string
}

// 用例执行结果
export interface CaseResult {
  caseId: string
  status: 'passed' | 'failed' | 'error'
  error?: string
  duration?: number
  output?: string
}

// 设备相关
export interface Device {
  id: number
  serial: string
  deviceName?: string
  model?: string
  romVersion: string
  status: 'idle' | 'busy' | 'flashing' | 'offline' | 'error'
  executorIp: string
  browserVersion: string
  remark: string
  lastReportTime: string
  currentFlashingId?: number  // 当前刷机过程ID
  createdAt?: string
}

// 分支相关（ROM分支）
export interface Branch {
  id: number
  name: string
  type?: 'DEV' | '主干' | '商分'
  version?: string
  model?: string
  versionPattern?: string
  mailTitlePattern?: string
  disabled?: boolean
  createdAt?: string
}

export interface CaseSet {
  id: number
  name: string
  description: string
  caseIds: number[]
  createdAt: string
}

export interface TaskConfig {
  id: number
  name: string
  scriptPath: string
  deviceLimit: number
  caseSets: number[]
}

// 任务相关
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
  agentUrl?: string
  caseIds?: string[]
  batchSize?: number
  currentBatch?: number
  caseResults?: CaseResult[]
  startTime?: string
  endTime?: string
  createdAt: string
  // 报告相关字段（已完成任务才有）
  passRate?: number
  totalCount?: number
  passCount?: number
  failCount?: number
  skipCount?: number
  errorCount?: number
  duration?: number
  log?: string
}

// ROM 版本记录（邮件转测来的版本在系统中的生命周期）
export interface RomRecord {
  id: number
  romVersion: string          // 版本号，如 207.0.0.25(SP1XX)
  model: string               // 设备型号，如 ALN-00
  branchId: number
  branchName: string          // 匹配到的分支名
  branchType: string          // DEV / 主干 / 商分
  deviceSerial?: string       // 分配的设备序列号
  status: 'matched' | 'waiting' | 'no_device' | 'no_match' | 'flashing' | 'success' | 'failed'
  reason?: string             // 状态说明（未匹配原因、等待原因等）
  emailTitle: string          // 原始邮件标题
  emailReceivedAt: string     // 邮件接收时间
  flashingProcessId?: number  // 关联刷机过程 ID
  updatedAt: string
  // 任务执行结果（刷机完成后执行分支配置的任务）
  tasksStatus?: 'pending' | 'running' | 'completed'
  taskResults?: RomTaskResult[]
}

// ROM 版本的任务执行结果
export interface RomTaskResult {
  taskConfigId: number
  name: string
  status: 'queued' | 'running' | 'success' | 'failed' | 'error'
  passRate?: number
  totalCount?: number
  passCount?: number
  failCount?: number
  errorCount?: number
  duration?: number
  startedAt?: string
  endedAt?: string
}

// 测试用例
export interface TestCase {
  id: number
  caseId: string
  name: string
  module: string
  priority: 'L0' | 'L1' | 'L2' | 'L3' | 'L4'
  scriptPath?: string
  steps: string
  expected: string
  creator: string
  createTime: string
  createdAt?: string
}
