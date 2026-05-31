import request from '@/utils/request'

function extractList(data: any): any[] {
  if (Array.isArray(data)) return data
  if (data && data.results) return data.results
  return []
}

// ======== 仪表盘 ========
export async function fetchDashboardStats() {
  const { data } = await request.get('/dashboard/stats')
  return data
}

// ======== 设备管理 ========
export async function fetchDevices(params?: {
  status?: string
  executor_ip?: string
  model?: string
}) {
  const { data } = await request.get('/devices', { params })
  return extractList(data)
}

export async function updateDevice(id: number, body: {
  status?: string
  remark?: string
}) {
  const { data } = await request.put(`/devices/${id}`, body)
  return data
}

export async function deleteDevice(id: number) {
  const { data } = await request.delete(`/devices/${id}`)
  return data
}

// ======== 分支管理 ========
export async function fetchBranches() {
  const { data } = await request.get('/branches')
  return extractList(data)
}

export async function createBranch(body: {
  name: string
  version_pattern?: string
  mail_title_pattern?: string
  disabled?: boolean
}) {
  const { data } = await request.post('/branches', body)
  return data
}

export async function updateBranch(id: number, body: {
  name?: string
  version_pattern?: string
  mail_title_pattern?: string
  disabled?: boolean
}) {
  const { data } = await request.put(`/branches/${id}`, body)
  return data
}

export async function deleteBranch(id: number) {
  const { data } = await request.delete(`/branches/${id}`)
  return data
}

// ======== 任务定义 ========
export async function fetchTaskDefs(params?: { branch_id?: number }) {
  const { data } = await request.get('/task-defs', { params })
  const list = extractList(data)
  return list.map((item: Record<string, unknown>) => ({
    ...item,
    branchId: (item as any).branch ?? (item as any).branchId,
  }))
}

export async function createTaskDef(body: {
  branch_id: number
  name: string
  script_path?: string
  device_select_type?: string
  device_quantity?: number
  device_models?: string[]
  device_ids?: number[]
  case_ids?: number[]
  case_set_ids?: number[]
  batch_size?: number
}) {
  const { data } = await request.post('/task-defs', body)
  return data
}

export async function updateTaskDef(id: number, body: {
  name?: string
  script_path?: string
  device_select_type?: string
  device_quantity?: number
  device_models?: string[]
  device_ids?: number[]
  case_ids?: number[]
  case_set_ids?: number[]
  batch_size?: number
}) {
  const { data } = await request.put(`/task-defs/${id}`, body)
  return data
}

export async function deleteTaskDef(id: number) {
  const { data } = await request.delete(`/task-defs/${id}`)
  return data
}

// ======== 版本跟踪 ========
export async function fetchVersions(params?: {
  branch_name?: string
  version_label?: string
  status?: number
}) {
  const { data } = await request.get('/versions', { params })
  const list = extractList(data)
  return list.map((item: Record<string, unknown>) => ({
    ...item,
    branchId: (item as any).branch ?? (item as any).branchId,
  }))
}

// ======== 刷机管理 ========
export async function fetchFlashingProcesses(params?: {
  version_label?: string
}) {
  const { data } = await request.get('/flashing', { params })
  return extractList(data)
}

export async function dispatchFlashing(versionId: number) {
  const { data } = await request.post('/flashing/dispatch', { version_id: versionId })
  return data
}

export async function retryFlashingStep(id: number, stepName: string) {
  const { data } = await request.post(`/flashing/${id}/retry-step`, { step_name: stepName })
  return data
}

export async function retryAllFlashingSteps(id: number) {
  const { data } = await request.post(`/flashing/${id}/retry-all`)
  return data
}

// ======== 任务中心 ========
export async function fetchTasks(params?: {
  status?: string
  version_label?: string
}) {
  const { data } = await request.get('/tasks', { params })
  return extractList(data)
}

export async function fetchTaskResults(taskId: number, params?: {
  status?: string
}) {
  const { data } = await request.get(`/tasks/${taskId}/results`, { params })
  return extractList(data)
}

export async function startTask(taskId: number) {
  const { data } = await request.post(`/tasks/${taskId}/start`)
  return data
}

// ======== 用例管理 ========
export async function fetchTestCases(params?: {
  module?: string
  priority?: string
  keyword?: string
}) {
  const { data } = await request.get('/test-cases', { params })
  return extractList(data)
}

export async function fetchTestCaseDetail(id: number) {
  const { data } = await request.get(`/test-cases/${id}`)
  return data
}

export async function createTestCase(body: {
  case_id: string
  name: string
  module?: string
  priority?: string
  precondition?: string
  steps?: string
  expected?: string
  creator?: string
}) {
  const { data } = await request.post('/test-cases', body)
  return data
}

export async function updateTestCase(id: number, body: {
  case_id?: string
  name?: string
  module?: string
  priority?: string
  precondition?: string
  steps?: string
  expected?: string
  creator?: string
}) {
  const { data } = await request.put(`/test-cases/${id}`, body)
  return data
}

export async function deleteTestCase(id: number) {
  const { data } = await request.delete(`/test-cases/${id}`)
  return data
}

export async function importTestCases(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await request.post('/test-cases/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

// ======== 用例集管理 ========
export async function fetchTestCaseSets() {
  const { data } = await request.get('/case-sets')
  return extractList(data)
}

export async function fetchTestCaseSetDetail(id: number) {
  const { data } = await request.get(`/case-sets/${id}`)
  return data
}

export async function createTestCaseSet(body: {
  name: string
  description?: string
  case_ids?: number[]
}) {
  const { data } = await request.post('/case-sets', body)
  return data
}

export async function updateTestCaseSet(id: number, body: {
  name?: string
  description?: string
  case_ids?: number[]
}) {
  const { data } = await request.put(`/case-sets/${id}`, body)
  return data
}

export async function deleteTestCaseSet(id: number) {
  const { data } = await request.delete(`/case-sets/${id}`)
  return data
}
