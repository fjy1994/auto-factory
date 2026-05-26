import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Device, Task, MailServiceStatus } from '@/types'

export const useAppStore = defineStore('app', () => {
  // 设备列表
  const devices = ref<Device[]>([])
  
  // 任务列表
  const tasks = ref<Task[]>([])
  
  // 邮件服务状态
  const mailStatus = ref<MailServiceStatus>({
    running: false,
    connected: false,
    email: '',
    pollInterval: 60,
    lastHeartbeat: ''
  })

  // 模拟数据初始化
  const initMockData = () => {
    devices.value = [
      {
        id: 1,
        serial: 'ABC123DEF456',
        romVersion: 'TQ3A.230605.010',
        status: 'idle',
        executorIp: '192.168.1.101',
        browserVersion: 'Chrome 118.0.5993.70',
        remark: '测试机-01 常用功能测试',
        lastReportTime: new Date().toISOString()
      },
      {
        id: 2,
        serial: 'DEF789GHI012',
        romVersion: 'TQ3A.230605.010',
        status: 'busy',
        executorIp: '192.168.1.102',
        browserVersion: 'Chrome 118.0.5993.70',
        remark: '测试机-02 稳定性测试专用',
        lastReportTime: new Date().toISOString()
      },
      {
        id: 3,
        serial: 'GHI345JKL678',
        romVersion: 'V14.0.1.0.SLACNXM',
        status: 'flashing',
        executorIp: '192.168.1.103',
        browserVersion: 'Chrome 117.0.5938.149',
        remark: '备用机',
        lastReportTime: new Date().toISOString()
      },
      {
        id: 4,
        serial: 'JKL901MNO234',
        romVersion: 'C.32',
        status: 'offline',
        executorIp: '192.168.1.104',
        browserVersion: 'Chrome 117.0.5938.149',
        remark: '',
        lastReportTime: new Date(Date.now() - 3600000).toISOString()
      }
    ]

    tasks.value = [
      {
        id: 1,
        name: '功能自动化用例',
        branchId: 1,
        branchName: '开发7.1',
        version: 'B32SP21',
        model: 'Pixel 7',
        taskType: '功能测试',
        status: 'running',
        progress: 65,
        deviceId: 2,
        deviceSerial: 'DEF789GHI012',
        startTime: new Date(Date.now() - 1800000).toISOString(),
        endTime: '',
        createdAt: new Date(Date.now() - 3600000).toISOString()
      },
      {
        id: 2,
        name: '稳定性自动化用例',
        branchId: 1,
        branchName: '开发7.1',
        version: 'B32SP21',
        model: 'Pixel 7',
        taskType: '稳定性测试',
        status: 'queued',
        progress: 0,
        deviceId: 0,
        deviceSerial: '',
        startTime: '',
        endTime: '',
        createdAt: new Date(Date.now() - 3600000).toISOString()
      },
      {
        id: 3,
        name: '功能自动化用例',
        branchId: 2,
        branchName: '主干7.0',
        version: 'B30SP15',
        model: 'MI 12',
        taskType: '功能测试',
        status: 'success',
        progress: 100,
        deviceId: 3,
        deviceSerial: 'GHI345JKL678',
        startTime: new Date(Date.now() - 7200000).toISOString(),
        endTime: new Date(Date.now() - 3600000).toISOString(),
        createdAt: new Date(Date.now() - 10800000).toISOString(),
        passRate: 92.5,
        totalCount: 200,
        passCount: 185,
        failCount: 12,
        skipCount: 3,
        errorCount: 0,
        duration: 3600
      },
      {
        id: 4,
        name: '兼容性测试用例',
        branchId: 2,
        branchName: '主干7.0',
        version: 'B30SP15',
        model: 'MI 12',
        taskType: '功能测试',
        status: 'failed',
        progress: 100,
        deviceId: 1,
        deviceSerial: 'ABC123DEF456',
        startTime: new Date(Date.now() - 14400000).toISOString(),
        endTime: new Date(Date.now() - 10800000).toISOString(),
        createdAt: new Date(Date.now() - 18000000).toISOString(),
        passRate: 65.0,
        totalCount: 150,
        passCount: 97,
        failCount: 48,
        skipCount: 5,
        errorCount: 0,
        duration: 3600
      }
    ]

    mailStatus.value = {
      running: true,
      connected: true,
      email: 'test@company.com',
      pollInterval: 60,
      lastHeartbeat: new Date().toISOString()
    }
  }

  return {
    devices,
    tasks,
    mailStatus,
    initMockData
  }
})
