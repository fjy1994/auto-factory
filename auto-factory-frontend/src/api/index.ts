/**
 * API 请求封装
 */

const API_BASE = 'http://localhost:8000'

// 通用请求方法
async function request(url: string, options: RequestInit = {}) {
  const fullUrl = url.startsWith('http') ? url : API_BASE + url
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  }
  
  try {
    const response = await fetch(fullUrl, defaultOptions)
    const data = await response.json()
    return data
  } catch (error) {
    console.error('API请求失败:', error)
    throw error
  }
}

// GET请求
function get(url: string) {
  return request(url, { method: 'GET' })
}

// POST请求
function post(url: string, data: any) {
  return request(url, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

// PUT请求
function put(url: string, data: any) {
  return request(url, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

// DELETE请求
function del(url: string) {
  return request(url, { method: 'DELETE' })
}

// ==================== 设备相关 API ====================

export const deviceApi = {
  // 获取设备列表
  getDevices: (status?: string) => {
    const url = status ? `/api/v1/devices?status=${status}` : '/api/v1/devices'
    return get(url)
  },
  
  // 更新设备备注
  updateRemark: (serial: string, remark: string) => {
    return put(`/api/v1/devices/${serial}`, { remark })
  },
  
  // 重启设备
  reboot: (serial: string) => {
    return post(`/api/v1/devices/${serial}/reboot`, {})
  },
}

// ==================== 分支相关 API ====================

export const branchApi = {
  // 获取分支列表
  getBranches: () => get('/api/v1/branches'),
  
  // 创建分支
  create: (data: { name: string; versionPattern: string; disabled?: boolean }) => {
    return post('/api/v1/branches', data)
  },
  
  // 更新分支
  update: (id: number, data: { name: string; versionPattern: string; disabled?: boolean }) => {
    return put(`/api/v1/branches/${id}`, data)
  },
  
  // 删除分支
  delete: (id: number) => del(`/api/v1/branches/${id}`),
  
  // 获取分支下的任务配置列表
  getTaskConfigs: (branchId: number) => {
    return get(`/api/v1/task-configs?branch_id=${branchId}`)
  },
  
  // 创建分支任务配置
  createTaskConfig: (data: any) => post('/api/v1/task-configs', data),
  
  // 更新分支任务配置
  updateTaskConfig: (id: number, data: any) => put(`/api/v1/task-configs/${id}`, data),
  
  // 删除分支任务配置
  deleteTaskConfig: (id: number) => del(`/api/v1/task-configs/${id}`),
}

// ==================== 任务相关 API ====================

export const taskApi = {
  // 获取任务列表
  getTasks: (params?: { status?: string; branchId?: number }) => {
    let url = '/api/v1/tasks'
    if (params) {
      const query = new URLSearchParams()
      if (params.status) query.append('status', params.status)
      if (params.branchId) query.append('branchId', String(params.branchId))
      const queryStr = query.toString()
      if (queryStr) url += '?' + queryStr
    }
    return get(url)
  },
  
  // 创建任务
  create: (data: any) => post('/api/v1/tasks', data),
  
  // 获取任务详情
  getDetail: (id: number) => get(`/api/v1/tasks/${id}`),
  
  // 取消任务
  cancel: (id: number) => put(`/api/v1/tasks/${id}/cancel`, {}),
  
  // 重跑任务
  rerun: (id: number) => put(`/api/v1/tasks/${id}/rerun`, {}),
}

// ==================== 待执行队列 API ====================

export const queueApi = {
  // 获取队列列表
  getQueue: () => get('/api/v1/version-queue'),
  
  // 添加版本到队列
  add: (data: any) => post('/api/v1/version-queue', data),
  
  // 创建任务
  createTasks: (id: number) => post(`/api/v1/version-queue/${id}/create-tasks`, {}),
  
  // 忽略/删除
  delete: (id: number) => del(`/api/v1/version-queue/${id}`),
}

// ==================== 测试用例 API ====================

export const testCaseApi = {
  // 获取用例列表
  getCases: (params?: { module?: string; priority?: string; keyword?: string }) => {
    let url = '/api/v1/test-cases'
    if (params) {
      const query = new URLSearchParams()
      if (params.module) query.append('module', params.module)
      if (params.priority) query.append('priority', params.priority)
      if (params.keyword) query.append('keyword', params.keyword)
      const queryStr = query.toString()
      if (queryStr) url += '?' + queryStr
    }
    return get(url)
  },
  
  // 获取模块列表
  getModules: () => get('/api/v1/test-cases/modules'),
  
  // 创建用例
  create: (data: any) => post('/api/v1/test-cases', data),
  
  // 更新用例
  update: (id: number, data: any) => put(`/api/v1/test-cases/${id}`, data),
  
  // 删除用例
  delete: (id: number) => del(`/api/v1/test-cases/${id}`),
}

// ==================== 执行机 API ====================

export const executorApi = {
  // 获取执行机列表
  getExecutors: () => get('/api/v1/executors'),
  
  // 下发指令
  sendCommand: (executorId: string, command: any) => {
    return post(`/api/v1/agent/${executorId}/command`, command)
  },
}

export default {
  deviceApi,
  branchApi,
  taskApi,
  queueApi,
  testCaseApi,
  executorApi,
}
