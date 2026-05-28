/**
 * API 客户端
 * 与 auto-factory-backend REST API 通信
 */

import axios from 'axios'
import type {
  Device, Branch, Task, TestCase, CaseSet,
  FlashingProcess, BranchTaskConfig, RomRecord, FlashingStep, CaseResult
} from '@/types'

// 开发时通过 Vite proxy 转发到 Django，生产环境通过 gateway 路由
const BASE_URL = import.meta.env.PROD ? '/api' : '/api'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
})

// ==================== 字段映射工具 ====================

/** 将 snake_case 键名转为 camelCase */
function toCamelKey(key: string): string {
  return key.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
}

/** 转换对象键名为 camelCase */
function toCamel(obj: Record<string, unknown>): Record<string, unknown> {
  const result: Record<string, unknown> = {}
  for (const key of Object.keys(obj)) {
    result[toCamelKey(key)] = obj[key]
  }
  return result
}

// ==================== 实体映射器 ====================

/** 转换 API 设备 → 前端 Device */
function mapDevice(d: Record<string, unknown>): Device {
  const c = toCamel(d)
  return {
    id: c.id as number,
    serial: c.serial as string,
    deviceName: c.deviceName as string || '',
    model: c.model as string || '',
    romVersion: c.romVersion as string,
    status: (c.status as string) as Device['status'],
    executorIp: c.executorIp as string || '',
    browserVersion: c.browserVersion as string || '',
    remark: c.remark as string || '',
    lastReportTime: c.lastReportTime as string || '',
  }
}

/** 转换 API 分支 → 前端 Branch */
function mapBranch(b: Record<string, unknown>): Branch {
  const c = toCamel(b)
  return {
    id: c.id as number,
    name: c.name as string,
    versionPattern: c.versionPattern as string || '',
    mailTitlePattern: c.mailTitlePattern as string || '',
    disabled: c.disabled as boolean || false,
    createdAt: c.createdAt as string || '',
  }
}

/** 转换 API 任务 → 前端 Task */
function mapTask(t: Record<string, unknown>): Task {
  const c = toCamel(t)
  return {
    id: c.id as number,
    name: c.name as string,
    branchId: c.branch as number || 0,
    branchName: c.branchName as string || '',
    version: c.version as string || '',
    model: c.model as string || '',
    taskType: c.taskType as string || '',
    status: (c.status as string) as Task['status'],
    progress: c.progress as number || 0,
    deviceId: c.deviceId as number || 0,
    deviceSerial: c.deviceSerial as string || '',
    agentUrl: c.agentUrl as string || '',
    caseIds: (c.caseIds as string[]) || [],
    batchSize: c.batchSize as number || 10,
    currentBatch: c.currentBatch as number || 0,
    caseResults: (c.caseResults as CaseResult[]) || [],
    startTime: c.startTime as string || '',
    endTime: c.endTime as string || '',
    createdAt: c.createdAt as string || '',
    passRate: c.passRate as number | undefined,
    totalCount: c.totalCount as number || 0,
    passCount: c.passCount as number || 0,
    failCount: c.failCount as number || 0,
  }
}

/** 转换 API 测试用例 → 前端 TestCase */
function mapTestCase(tc: Record<string, unknown>): TestCase {
  const c = toCamel(tc)
  return {
    id: c.id as number,
    caseId: c.caseId as string,
    name: c.name as string,
    module: c.module as string || '',
    priority: (c.priority as string) as TestCase['priority'],
    scriptPath: c.scriptPath as string || '',
    steps: c.steps as string || '',
    expected: c.expected as string || '',
    creator: c.creator as string || '',
    createTime: c.createdAt as string || '',
  }
}

/** 转换 API 用例集 → 前端 CaseSet */
function mapCaseSet(cs: Record<string, unknown>): CaseSet {
  const c = toCamel(cs)
  return {
    id: c.id as number,
    name: c.name as string,
    description: c.description as string || '',
    caseIds: (c.caseIds as number[]) || [],
    createdAt: c.createdAt as string || '',
  }
}

/** 转换 API 刷机过程 → 前端 FlashingProcess */
function mapFlashingProcess(fp: Record<string, unknown>): FlashingProcess {
  const c = toCamel(fp)
  const rawSteps = (c.steps || []) as Array<Record<string, unknown>>
  // 后端步骤字段: { name, status, progress, retries, error? }
  const stepKeyMap: Record<string, string> = {
    '下载ROM': 'download_rom',
    '刷机': 'flash',
    '开机引导': 'boot_setup',
    '登录WiFi': 'wifi_login',
  }
  // 后端状态 → 前端状态
  const stepStatusMap: Record<string, string> = {
    'pending': 'pending',
    'running': 'running',
    'completed': 'success',
    'success': 'success',
    'failed': 'failed',
    'skipped': 'skipped',
  }
  const steps: FlashingStep[] = rawSteps.map((s, i) => ({
        key: ((s.key as string) || stepKeyMap[s.name as string] || `step_${i}`) as FlashingStep['key'],
    name: s.name as string,
    status: (stepStatusMap[s.status as string] || s.status) as FlashingStep['status'],
    message: s.message as string || undefined,
    errorMessage: s.error as string || s.errorMessage as string || undefined,
    startedAt: s.startedAt as string || undefined,
    endedAt: s.endedAt as string || undefined,
    retryCount: (s.retries as number) || (s.retryCount as number) || 0,
  }))
  // 后端总体状态 → 前端状态
  const statusMap: Record<string, FlashingProcess['status']> = {
    'pending': 'pending',
    'running': 'flashing',
    'completed': 'success',
    'success': 'success',
    'failed': 'failed',
  }
  return {
    id: c.id as number,
    branchId: c.branch as number || 0,
    branchName: c.branchName as string || '',
    deviceId: c.device as number || 0,
    deviceSerial: c.deviceSerial as string || c.serial as string || '',
    model: c.model as string || '',
    romVersion: c.version as string || '',
    status: statusMap[c.status as string] || 'pending',
    steps,
    currentStepIndex: steps.findIndex(s => s.status === 'running'),
    createdAt: c.createdAt as string || '',
    updatedAt: c.updatedAt as string || '',
  }
}

/** 转换 API 任务配置 → 前端 BranchTaskConfig */
function mapTaskConfig(tc: Record<string, unknown>): BranchTaskConfig {
  const c = toCamel(tc)
  return {
    id: c.id as number,
    branchId: c.branch as number || 0,
    name: c.name as string,
    scriptPath: c.scriptPath as string || '',
    deviceLimit: c.deviceLimit as string || '',
    caseSets: (c.caseSets as number[]) || (c.caseSetIds as number[]) || [],
    batchSize: c.batchSize as number || 10,
    order: c.order as number || 0,
    createdAt: c.createdAt as string || '',
  }
}

/** 转换 API ROM 记录 → 前端 RomRecord */
function mapRomRecord(r: Record<string, unknown>): RomRecord {
  const c = toCamel(r)
  const rec = {
    id: c.id as number,
    romVersion: c.version as string || c.romVersion as string || '',
    model: c.model as string || '',
    branchId: c.branch as number || 0,
    branchName: c.branchName as string || '',
    branchType: c.branchType as string || c.type as string || '',
    deviceSerial: c.deviceSerial as string || '',
    status: (c.status as string) as RomRecord['status'],
    reason: c.reason as string || c.errorMessage as string || '',
    emailTitle: c.emailTitle as string || '',
    emailReceivedAt: c.emailReceivedAt as string || c.createdAt as string || '',
    flashingProcessId: c.flashingProcessId as number || undefined,
    updatedAt: c.updatedAt as string || c.createdAt as string || '',
    tasksStatus: c.tasksStatus as RomRecord['tasksStatus'] || undefined,
    taskResults: c.taskResults as RomRecord['taskResults'] || undefined,
  }
  // 推断覆盖状态
  if (!rec.status && c.coverageStatus) {
    const covMap: Record<string, string> = {
      'covered': 'success',
      'partial': 'flashing',
      'uncovered': 'no_device',
    }
    rec.status = (covMap[c.coverageStatus as string] || 'no_match') as RomRecord['status']
  }
  return rec
}

// ==================== 工具函数 ====================

/** 从 Axios 响应体中提取数组（处理分页包装） */
function extractList(data: unknown): Record<string, unknown>[] {
  if (Array.isArray(data)) return data as Record<string, unknown>[]
  // 分页格式: { count, next, previous, results }
  if (data && typeof data === 'object' && 'results' in (data as Record<string, unknown>)) {
    const results = (data as Record<string, unknown>).results
    if (Array.isArray(results)) return results as Record<string, unknown>[]
  }
  console.warn('API 响应格式异常，期望数组或分页对象', data)
  return []
}

function mapList<T>(raw: unknown, mapper: (item: Record<string, unknown>) => T): T[] {
  return extractList(raw).map(mapper)
}

// ==================== 设备 ====================

export async function fetchDevices(): Promise<Device[]> {
  const { data } = await api.get('/devices/')
  return mapList<Device>(data, mapDevice)
}

export async function createDevice(device: Partial<Device>): Promise<Device> {
  const { data } = await api.post('/devices/', device)
  return mapDevice(data)
}

export async function updateDevice(id: number, device: Partial<Device>): Promise<Device> {
  const { data } = await api.put(`/devices/${id}/`, device)
  return mapDevice(data)
}

export async function deleteDevice(id: number): Promise<void> {
  await api.delete(`/devices/${id}/`)
}

// ==================== 分支 ====================

export async function fetchBranches(): Promise<Branch[]> {
  const { data } = await api.get('/branches/')
  return mapList<Branch>(data, mapBranch)
}

export async function createBranch(branch: Partial<Branch>): Promise<Branch> {
  const { data } = await api.post('/branches/', branch)
  return mapBranch(data)
}

export async function updateBranch(id: number, branch: Partial<Branch>): Promise<Branch> {
  const { data } = await api.put(`/branches/${id}/`, branch)
  return mapBranch(data)
}

export async function deleteBranch(id: number): Promise<void> {
  await api.delete(`/branches/${id}/`)
}

// ==================== 任务 ====================

export async function fetchTasks(): Promise<Task[]> {
  const { data } = await api.get('/tasks/')
  return mapList<Task>(data, mapTask)
}

export async function createTask(task: Partial<Task>): Promise<Task> {
  const { data } = await api.post('/tasks/', task)
  return mapTask(data)
}

export async function updateTask(id: number, task: Partial<Task>): Promise<Task> {
  const { data } = await api.put(`/tasks/${id}/`, task)
  return mapTask(data)
}

export async function deleteTask(id: number): Promise<void> {
  await api.delete(`/tasks/${id}/`)
}

/** 启动任务调度 */
export async function startTask(id: number, agentUrl: string): Promise<{ message: string; taskId: number }> {
  const { data } = await api.post(`/tasks/${id}/start/`, { agent_url: agentUrl })
  return data as { message: string; taskId: number }
}

/** 提交批次执行结果（Agent 回调） */
export async function reportBatch(
  taskId: number, batchIndex: number, results: CaseResult[]
): Promise<{ message: string; progress: number; status: string }> {
  const { data } = await api.post('/tasks/report_batch/', {
    task_id: taskId,
    batch_index: batchIndex,
    results,
  })
  return data as { message: string; progress: number; status: string }
}

// ==================== 测试用例 ====================

export async function fetchTestCases(): Promise<TestCase[]> {
  const { data } = await api.get('/test-cases/')
  return mapList<TestCase>(data, mapTestCase)
}

export async function createTestCase(tc: Partial<TestCase>): Promise<TestCase> {
  const { data } = await api.post('/test-cases/', tc)
  return mapTestCase(data)
}

export async function updateTestCase(id: number, tc: Partial<TestCase>): Promise<TestCase> {
  const { data } = await api.put(`/test-cases/${id}/`, tc)
  return mapTestCase(data)
}

export async function deleteTestCase(id: number): Promise<void> {
  await api.delete(`/test-cases/${id}/`)
}

// ==================== 用例集 ====================

export async function fetchCaseSets(): Promise<CaseSet[]> {
  const { data } = await api.get('/case-sets/')
  return mapList<CaseSet>(data, mapCaseSet)
}

export async function createCaseSet(cs: Partial<CaseSet>): Promise<CaseSet> {
  const { data } = await api.post('/case-sets/', cs)
  return mapCaseSet(data)
}

export async function updateCaseSet(id: number, cs: Partial<CaseSet>): Promise<CaseSet> {
  const { data } = await api.put(`/case-sets/${id}/`, cs)
  return mapCaseSet(data)
}

export async function deleteCaseSet(id: number): Promise<void> {
  await api.delete(`/case-sets/${id}/`)
}

// ==================== 刷机过程 ====================

export async function fetchFlashingProcesses(): Promise<FlashingProcess[]> {
  const { data } = await api.get('/flashing-processes/')
  return mapList<FlashingProcess>(data, mapFlashingProcess)
}

export async function createFlashingProcess(fp: Partial<FlashingProcess>): Promise<FlashingProcess> {
  const { data } = await api.post('/flashing-processes/', fp)
  return mapFlashingProcess(data)
}

// ==================== ROM 版本记录 ====================

export async function fetchRomRecords(): Promise<RomRecord[]> {
  const { data } = await api.get('/rom-records/')
  return mapList<RomRecord>(data, mapRomRecord)
}

// ==================== 分支任务配置 ====================

export async function fetchTaskConfigs(): Promise<BranchTaskConfig[]> {
  const { data } = await api.get('/task-configs/')
  return mapList<BranchTaskConfig>(data, mapTaskConfig)
}

export async function createTaskConfig(tc: Partial<BranchTaskConfig>): Promise<BranchTaskConfig> {
  const { data } = await api.post('/task-configs/', tc)
  return mapTaskConfig(data)
}

export async function updateTaskConfig(id: number, tc: Partial<BranchTaskConfig>): Promise<BranchTaskConfig> {
  const { data } = await api.put(`/task-configs/${id}/`, tc)
  return mapTaskConfig(data)
}

export async function deleteTaskConfig(id: number): Promise<void> {
  await api.delete(`/task-configs/${id}/`)
}

// ==================== 批量加载 ====================

export async function fetchAll(): Promise<{
  devices: Device[]
  branches: Branch[]
  tasks: Task[]
  testCases: TestCase[]
  caseSets: CaseSet[]
  flashingProcesses: FlashingProcess[]
  romRecords: RomRecord[]
  branchTaskConfigs: BranchTaskConfig[]
}> {
  const [
    devices,
    branches,
    tasks,
    testCases,
    caseSets,
    flashingProcesses,
    romRecords,
    branchTaskConfigs,
  ] = await Promise.all([
    fetchDevices(),
    fetchBranches(),
    fetchTasks(),
    fetchTestCases(),
    fetchCaseSets(),
    fetchFlashingProcesses(),
    fetchRomRecords(),
    fetchTaskConfigs(),
  ])

  return {
    devices,
    branches,
    tasks,
    testCases,
    caseSets,
    flashingProcesses,
    romRecords,
    branchTaskConfigs,
  }
}
