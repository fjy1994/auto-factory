import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { Device, Branch, TaskDef, FlashingProcess, Version, Task, TestCase, CaseSet } from '@/types'
import * as api from '@/api'

// 版本状态文字映射
export const VERSION_STATUS_TEXT: Record<number, string> = {
  0: '无设备',
  1: '等待中',
  2: '刷机中',
  3: '刷机失败',
  4: '测试中',
  5: '已完成',
  6: '已废弃'
}

export const VERSION_STATUS_TAG: Record<number, string> = {
  0: 'info',
  1: 'warning',
  2: 'primary',
  3: 'danger',
  4: 'warning',
  5: 'success',
  6: 'info'
}

// 版本状态枚举
export const VERSION_STATUS = {
  NO_DEVICE: 0,
  QUEUED: 1,
  FLASHING: 2,
  FLASH_FAILED: 3,
  TESTING: 4,
  COMPLETED: 5,
  OBSOLETED: 6
} as const

export const useAppStore = defineStore('app', () => {
  const devices = ref<Device[]>([])
  const branches = ref<Branch[]>([])
  const taskDefs = ref<TaskDef[]>([])
  const flashingProcesses = ref<FlashingProcess[]>([])
  const versions = ref<Version[]>([])
  const tasks = ref<Task[]>([])
  const testCases = ref<TestCase[]>([])
  const caseSets = ref<CaseSet[]>([])

  async function fetchDevicesData(params?: { status?: string; model?: string; executor_ip?: string }) {
    try {
      const d = await api.fetchDevices(params)
      devices.value = d as Device[]
    } catch (e) {
      console.error('获取设备列表失败:', e)
      devices.value = []
    }
  }

  async function fetchBranchesData() {
    try {
      const [b, td] = await Promise.all([
        api.fetchBranches(),
        api.fetchTaskDefs(),
      ])
      branches.value = b as Branch[]
      taskDefs.value = td as TaskDef[]
    } catch (e) {
      console.error('获取分支列表失败:', e)
      branches.value = []
    }
  }

  async function fetchTasksData() {
    try {
      const t = await api.fetchTasks()
      tasks.value = t as Task[]
    } catch (e) {
      console.error('获取任务列表失败:', e)
      tasks.value = []
    }
  }

  async function fetchFlashingProcessesData() {
    try {
      const f = await api.fetchFlashingProcesses()
      flashingProcesses.value = f as FlashingProcess[]
    } catch (e) {
      console.error('获取刷机记录失败:', e)
      flashingProcesses.value = []
    }
  }

  async function fetchVersionsData() {
    try {
      const r = await api.fetchVersions()
      versions.value = r as Version[]
    } catch (e) {
      console.error('获取版本列表失败:', e)
      versions.value = []
    }
  }

  async function fetchTestCasesData() {
    try {
      const tc = await api.fetchTestCases()
      testCases.value = tc as TestCase[]
    } catch (e) {
      console.error('获取测试用例失败:', e)
      testCases.value = []
    }
  }

  async function fetchCaseSetsData() {
    try {
      const cs = await api.fetchTestCaseSets()
      caseSets.value = cs as CaseSet[]
    } catch (e) {
      console.error('获取用例集失败:', e)
      caseSets.value = []
    }
  }

  return {
    devices,
    branches,
    taskDefs,
    flashingProcesses,
    versions,
    tasks,
    testCases,
    caseSets,
    fetchDevices: fetchDevicesData,
    fetchBranches: fetchBranchesData,
    fetchTasks: fetchTasksData,
    fetchFlashingProcesses: fetchFlashingProcessesData,
    fetchVersions: fetchVersionsData,
    fetchTestCases: fetchTestCasesData,
    fetchCaseSets: fetchCaseSetsData,
    VERSION_STATUS_TEXT,
    VERSION_STATUS_TAG,
    VERSION_STATUS,
  }
})
