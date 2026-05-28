import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Device, Task, Branch, TestCase, CaseSet, FlashingProcess, BranchTaskConfig, RomRecord } from '@/types'
import * as api from '@/api'

export const useAppStore = defineStore('app', () => {
  // 设备列表
  const devices = ref<Device[]>([])
  
  // 任务列表
  const tasks = ref<Task[]>([])
  
  // 分支列表
  const branches = ref<Branch[]>([])
  
  // 用例列表
  const testCases = ref<TestCase[]>([])

  // 用例集
  const caseSets = ref<CaseSet[]>([])

  // 刷机过程列表
  const flashingProcesses = ref<FlashingProcess[]>([])

  // 分支任务配置
  const branchTaskConfigs = ref<BranchTaskConfig[]>([])

  // ROM 版本记录
  const romRecords = ref<RomRecord[]>([])

  // 是否已加载
  const loaded = ref(false)
  const loading = ref(false)

  // Mock 数据开关（默认开启）
  const useMock = ref(true)

  // ==================== 数据加载 ====================

  /** 从后端 API 加载所有数据（根据 useMock 开关自动选择数据源） */
  const fetchAll = async () => {
    if (loading.value) return
    loading.value = true
    try {
      if (useMock.value) {
        // Mock 模式：直接使用模拟数据
        initMockData()
      } else {
        // 真实模式：从后端 API 获取
        const data = await api.fetchAll()
        devices.value = data.devices
        branches.value = data.branches
        tasks.value = data.tasks
        testCases.value = data.testCases
        caseSets.value = data.caseSets
        flashingProcesses.value = data.flashingProcesses
        romRecords.value = data.romRecords
        branchTaskConfigs.value = data.branchTaskConfigs
        loaded.value = true
      }
    } catch (e) {
      console.warn('API 加载失败', e)
      // 真实模式下失败也不回退到 mock，保持空数据
    } finally {
      loading.value = false
    }
  }

  /** 切换 Mock/真实数据源 */
  const toggleMock = (val: boolean) => {
    if (val === useMock.value) return
    useMock.value = val
    // 清空旧数据后重新加载
    loaded.value = false
    devices.value = []
    tasks.value = []
    branches.value = []
    testCases.value = []
    caseSets.value = []
    flashingProcesses.value = []
    romRecords.value = []
    branchTaskConfigs.value = []
    fetchAll()
  }

  // ==================== 模拟数据（备用） ====================

  const initMockData = () => {
    if (loaded.value) return
    devices.value = [
      {
        id: 1,
        serial: 'ABC123DEF456',
        deviceName: 'Pixel 7 Pro',
        model: 'GP4BC',
        romVersion: 'TQ3A.230605.010',
        status: 'idle',
        executorIp: '192.168.1.101',
        browserVersion: 'Chrome 118.0.5993.70',
        remark: '测试机-01 常用功能测试',
        lastReportTime: '2026-05-27T10:30:00',
        createdAt: '2026-04-01T08:00:00'
      },
      {
        id: 2,
        serial: 'DEF789GHI012',
        deviceName: 'Pixel 7',
        model: 'GE2AE',
        romVersion: 'TQ3A.230605.010',
        status: 'busy',
        executorIp: '192.168.1.102',
        browserVersion: 'Chrome 117.0.5938.62',
        remark: '测试机-02 性能测试',
        lastReportTime: '2026-05-27T12:30:00',
        createdAt: '2026-04-01T08:00:00'
      },
      {
        id: 3,
        serial: 'GHI345JKL678',
        deviceName: 'Mi 13 Pro',
        model: '2210132C',
        romVersion: 'MIUI 14.0.5',
        status: 'idle',
        executorIp: '192.168.1.103',
        browserVersion: 'Chrome 118.0.5993.70',
        remark: '测试机-03 兼容性测试',
        lastReportTime: '2026-05-26T18:00:00',
        createdAt: '2026-04-05T08:00:00'
      },
      {
        id: 4,
        serial: 'JKL901MNO234',
        deviceName: 'OnePlus 11',
        model: 'PHB110',
        romVersion: 'ColorOS 13.0',
        status: 'offline',
        executorIp: '',
        browserVersion: '',
        remark: '测试机-04 待维修',
        lastReportTime: '2026-05-20T09:00:00',
        createdAt: '2026-04-10T08:00:00'
      },
      {
        id: 5,
        serial: 'MNO567PQR890',
        deviceName: 'Samsung S23',
        model: 'SM-S9110',
        romVersion: 'One UI 5.1',
        status: 'idle',
        executorIp: '192.168.1.105',
        browserVersion: 'Samsung Internet 21.0',
        remark: '测试机-05 新到',
        lastReportTime: '2026-05-27T12:00:00',
        createdAt: '2026-04-15T08:00:00'
      },
      {
        id: 6,
        serial: 'STU123VWX456',
        deviceName: 'Xiaomi 14',
        model: '23127PN0CC',
        romVersion: 'HyperOS 1.0.2',
        status: 'idle',
        executorIp: '192.168.1.106',
        browserVersion: 'Chrome 120.0.6099.43',
        remark: '测试机-06 日常测试',
        lastReportTime: '2026-05-27T13:00:00',
        createdAt: '2026-04-20T08:00:00'
      },
      {
        id: 7,
        serial: 'YZA789BCD012',
        deviceName: 'Oppo Find X7',
        model: 'PHZ110',
        romVersion: 'ColorOS 14.0',
        status: 'busy',
        executorIp: '192.168.1.107',
        browserVersion: 'Chrome 120.0.6099.43',
        remark: '测试机-07 性能压测',
        lastReportTime: '2026-05-27T14:00:00',
        createdAt: '2026-04-22T08:00:00'
      },
      {
        id: 8,
        serial: 'CDE345FGH678',
        deviceName: 'Vivo X100 Pro',
        model: 'V2324A',
        romVersion: 'OriginOS 4.0',
        status: 'idle',
        executorIp: '192.168.1.108',
        browserVersion: 'Chrome 119.0.6045.163',
        remark: '测试机-08 兼容性验证',
        lastReportTime: '2026-05-27T09:00:00',
        createdAt: '2026-04-25T08:00:00'
      },
      {
        id: 9,
        serial: 'IJK901LMN234',
        deviceName: 'Honor Magic6',
        model: 'BVL-AN00',
        romVersion: 'MagicOS 8.0',
        status: 'offline',
        executorIp: '',
        browserVersion: '',
        remark: '测试机-09 网络故障排查',
        lastReportTime: '2026-05-26T15:00:00',
        createdAt: '2026-04-28T08:00:00'
      },
      {
        id: 10,
        serial: 'OPQ567RST890',
        deviceName: 'OnePlus 12',
        model: 'PJD110',
        romVersion: 'ColorOS 14.0',
        status: 'idle',
        executorIp: '192.168.1.110',
        browserVersion: 'Chrome 120.0.6099.43',
        remark: '测试机-10 回归测试',
        lastReportTime: '2026-05-27T11:00:00',
        createdAt: '2026-05-01T08:00:00'
      },
      {
        id: 11,
        serial: 'TUV234WXY567',
        deviceName: 'Pixel 8 Pro',
        model: 'G1MNW',
        romVersion: 'AP1A.240305.019',
        status: 'idle',
        executorIp: '192.168.1.111',
        browserVersion: 'Chrome 121.0.6167.85',
        remark: '测试机-11 自动化脚本调试',
        lastReportTime: '2026-05-27T16:00:00',
        createdAt: '2026-05-03T08:00:00'
      },
      {
        id: 12,
        serial: 'ZAB890CDE123',
        deviceName: 'Redmi K70 Pro',
        model: '23113RKC6C',
        romVersion: 'HyperOS 1.0.3',
        status: 'flashing',
        executorIp: '192.168.1.112',
        browserVersion: 'Chrome 120.0.6099.43',
        remark: '测试机-12 正在刷机',
        lastReportTime: '2026-05-27T17:00:00',
        createdAt: '2026-05-05T08:00:00'
      },
      {
        id: 13,
        serial: 'FGH456IJK789',
        deviceName: 'Samsung S24 Ultra',
        model: 'SM-S9280',
        romVersion: 'One UI 6.1',
        status: 'idle',
        executorIp: '192.168.1.113',
        browserVersion: 'Samsung Internet 22.0',
        remark: '测试机-13 旗舰机型适配',
        lastReportTime: '2026-05-27T15:30:00',
        createdAt: '2026-05-08T08:00:00'
      },
      {
        id: 14,
        serial: 'LMN012OPQ345',
        deviceName: 'iPhone 15 Pro',
        model: 'A3104',
        romVersion: 'iOS 17.4',
        status: 'busy',
        executorIp: '192.168.1.114',
        browserVersion: 'Safari 17.4',
        remark: '测试机-14 iOS测试机',
        lastReportTime: '2026-05-27T16:30:00',
        createdAt: '2026-05-10T08:00:00'
      },
      {
        id: 15,
        serial: 'RST678UVW901',
        deviceName: '小米14 Ultra',
        model: '24031PN0DC',
        romVersion: 'HyperOS 1.0.4',
        status: 'idle',
        executorIp: '192.168.1.115',
        browserVersion: 'Chrome 121.0.6167.85',
        remark: '测试机-15 主力测试机',
        lastReportTime: '2026-05-27T17:15:00',
        createdAt: '2026-05-12T08:00:00'
      },
      {
        id: 16,
        serial: 'UVW234XYZ567',
        deviceName: 'Google Pixel 7a',
        model: 'GHL1X',
        romVersion: 'TQ3A.230805.001',
        status: 'idle',
        executorIp: '192.168.1.116',
        browserVersion: 'Chrome 121.0.6167.85',
        remark: '测试机-16 中端测试',
        lastReportTime: '2026-05-27T10:00:00',
        createdAt: '2026-05-15T08:00:00'
      },
      {
        id: 17,
        serial: 'XYZ890ABC123',
        deviceName: 'Xiaomi 13T Pro',
        model: '23078PND5G',
        romVersion: 'HyperOS 1.0.1',
        status: 'busy',
        executorIp: '192.168.1.117',
        browserVersion: 'Chrome 120.0.6099.43',
        remark: '测试机-17 持续集成',
        lastReportTime: '2026-05-27T14:20:00',
        createdAt: '2026-05-16T08:00:00'
      },
      {
        id: 18,
        serial: 'BCD234EFG567',
        deviceName: 'Oppo Reno11 Pro',
        model: 'PJH110',
        romVersion: 'ColorOS 14.0',
        status: 'idle',
        executorIp: '192.168.1.118',
        browserVersion: 'Chrome 119.0.6045.163',
        remark: '测试机-18 拍照测试',
        lastReportTime: '2026-05-27T08:30:00',
        createdAt: '2026-05-18T08:00:00'
      },
      {
        id: 19,
        serial: 'HIJ789KLM012',
        deviceName: 'vivo X Fold3',
        model: 'V2337A',
        romVersion: 'OriginOS 4.0',
        status: 'offline',
        executorIp: '',
        browserVersion: '',
        remark: '测试机-19 折叠屏适配',
        lastReportTime: '2026-05-25T17:00:00',
        createdAt: '2026-05-20T08:00:00'
      },
      {
        id: 20,
        serial: 'NOP345QRS678',
        deviceName: 'Honor 100 Pro',
        model: 'MAA-AN00',
        romVersion: 'MagicOS 7.2',
        status: 'idle',
        executorIp: '192.168.1.120',
        browserVersion: 'Chrome 120.0.6099.43',
        remark: '测试机-20 中端回归',
        lastReportTime: '2026-05-27T12:10:00',
        createdAt: '2026-05-22T08:00:00'
      },
      {
        id: 21,
        serial: 'TUV890WXY123',
        deviceName: 'Samsung S23 FE',
        model: 'SM-S7110',
        romVersion: 'One UI 6.0',
        status: 'flashing',
        executorIp: '192.168.1.121',
        browserVersion: 'Samsung Internet 21.0',
        remark: '测试机-21 刷机测试中',
        lastReportTime: '2026-05-27T17:30:00',
        createdAt: '2026-05-23T08:00:00'
      },
      {
        id: 22,
        serial: 'ZAB123CDE456',
        deviceName: 'Redmi Note 13 Pro+',
        model: '23090RA98C',
        romVersion: 'HyperOS 1.0.2',
        status: 'idle',
        executorIp: '192.168.1.122',
        browserVersion: 'Chrome 120.0.6099.43',
        remark: '测试机-22 入门级测试',
        lastReportTime: '2026-05-27T11:45:00',
        createdAt: '2026-05-24T08:00:00'
      },
      {
        id: 23,
        serial: 'FGH789IJK012',
        deviceName: 'OnePlus Ace 3',
        model: 'PJE110',
        romVersion: 'ColorOS 14.0',
        status: 'busy',
        executorIp: '192.168.1.123',
        browserVersion: 'Chrome 121.0.6167.85',
        remark: '测试机-23 游戏性能测试',
        lastReportTime: '2026-05-27T16:50:00',
        createdAt: '2026-05-25T08:00:00'
      },
      {
        id: 24,
        serial: 'LMN456OPQ789',
        deviceName: 'iPhone 16',
        model: 'A3293',
        romVersion: 'iOS 18.0',
        status: 'idle',
        executorIp: '192.168.1.124',
        browserVersion: 'Safari 18.0',
        remark: '测试机-24 iOS 18测试',
        lastReportTime: '2026-05-27T15:00:00',
        createdAt: '2026-05-26T08:00:00'
      },
      {
        id: 25,
        serial: 'RST123UVW456',
        deviceName: 'Google Pixel 9 Pro',
        model: 'G1MNW',
        romVersion: 'AP2A.240605.024',
        status: 'idle',
        executorIp: '192.168.1.125',
        browserVersion: 'Chrome 122.0.6261.64',
        remark: '测试机-25 最新旗舰测试',
        lastReportTime: '2026-05-27T17:45:00',
        createdAt: '2026-05-27T08:00:00'
      }
    ]

    branches.value = [
      { id: 1, name: 'DEV-V14.0.1', type: 'DEV', version: 'V14.0.1', model: '小米14', mailTitlePattern: '[DEV] V14.0.*', disabled: false, createdAt: '2026-04-01T08:00:00' },
      { id: 2, name: '主干-V15.0', type: '主干', version: 'V15.0.0', model: 'Redmi K70', mailTitlePattern: '[主干] V15.0.*', disabled: false, createdAt: '2026-04-02T08:00:00' },
      { id: 3, name: '商分-V14.0.5', type: '商分', version: 'V14.0.5', model: '小米13', mailTitlePattern: '[商分] V14.0.*', disabled: false, createdAt: '2026-04-03T08:00:00' },
    ]

    tasks.value = [
      {
        id: 1, name: '小米14 V14.0.1 稳定性压力测试', branchName: 'DEV-V14.0.1', branchId: 1, version: 'V14.0.1', model: '小米14',
        taskType: '稳定性', status: 'running', progress: 65, deviceId: 1, deviceSerial: 'SN001',
        agentUrl: 'http://192.168.1.100:8000', caseIds: ['TC-001','TC-002','TC-004','TC-003','TC-005'],
        batchSize: 3, currentBatch: 2,
        caseResults: [
          { caseId: 'TC-001', status: 'passed', duration: 12.3 },
          { caseId: 'TC-002', status: 'passed', duration: 8.7 },
          { caseId: 'TC-004', status: 'failed', error: 'AssertionError: 搜索结果与实际不符', duration: 15.1 },
          { caseId: 'TC-003', status: 'passed', duration: 5.2 },
        ],
        passRate: 75.0, totalCount: 100, passCount: 3, failCount: 1,
        startTime: '2026-05-27T08:00:00', endTime: undefined, createdAt: '2026-05-27T07:00:00'
      },
      {
        id: 2, name: 'Redmi K70 V15.0 功能回归', branchName: '主干-V15.0', branchId: 2, version: 'V15.0.0', model: 'Redmi K70',
        taskType: '功能回归', status: 'success', progress: 100, deviceId: 3, deviceSerial: 'SN003',
        agentUrl: 'http://192.168.1.101:8000', caseIds: ['TC-001','TC-002','TC-003','TC-004','TC-005','TC-006'],
        batchSize: 5, currentBatch: 2,
        caseResults: [
          { caseId: 'TC-001', status: 'passed', duration: 10.2 },
          { caseId: 'TC-002', status: 'passed', duration: 9.5 },
          { caseId: 'TC-003', status: 'passed', duration: 7.8 },
          { caseId: 'TC-004', status: 'passed', duration: 11.3 },
          { caseId: 'TC-005', status: 'failed', error: 'Timeout: 主题切换超时', duration: 30.1 },
          { caseId: 'TC-006', status: 'passed', duration: 6.4 },
        ],
        passRate: 83.3, totalCount: 200, passCount: 5, failCount: 1,
        startTime: '2026-05-27T05:00:00', endTime: '2026-05-27T07:00:00', createdAt: '2026-05-27T04:00:00'
      },
      {
        id: 3, name: '小米13 V14.0.5 兼容性测试', branchName: '商分-V14.0.5', branchId: 3, version: 'V14.0.5', model: '小米13',
        taskType: '兼容性', status: 'queued', progress: 0, deviceId: 5, deviceSerial: 'SN005',
        agentUrl: '', caseIds: ['TC-005','TC-006','TC-007'],
        batchSize: 10, currentBatch: 0, caseResults: [],
        passRate: undefined, totalCount: 150, passCount: 0, failCount: 0,
        startTime: undefined, endTime: undefined, createdAt: '2026-05-27T06:00:00'
      },
      {
        id: 4, name: '小米14 V14.0.1 性能测试', branchName: 'DEV-V14.0.1', branchId: 1, version: 'V14.0.1', model: '小米14',
        taskType: '性能', status: 'failed', progress: 30, deviceId: 2, deviceSerial: 'SN002',
        agentUrl: 'http://192.168.1.100:8000', caseIds: ['TC-003','TC-006'],
        batchSize: 2, currentBatch: 1,
        caseResults: [
          { caseId: 'TC-003', status: 'passed', duration: 5.1 },
          { caseId: 'TC-006', status: 'error', error: 'Agent 连接超时，设备离线', duration: 0 },
        ],
        passRate: 50.0, totalCount: 80, passCount: 1, failCount: 1,
        startTime: '2026-05-27T09:00:00', endTime: undefined, createdAt: '2026-05-27T07:30:00'
      },
      {
        id: 5, name: 'Redmi K70 V15.0 压力测试', branchName: '主干-V15.0', branchId: 2, version: 'V15.0.0', model: 'Redmi K70',
        taskType: '压力', status: 'queued', progress: 0, deviceId: 3, deviceSerial: 'SN003',
        agentUrl: '', caseIds: ['TC-001','TC-002','TC-003','TC-004','TC-005'],
        batchSize: 5, currentBatch: 0, caseResults: [],
        passRate: undefined, totalCount: 500, passCount: 0, failCount: 0,
        startTime: undefined, endTime: undefined, createdAt: '2026-05-27T08:00:00'
      },
    ]

    testCases.value = [
      { id: 1, caseId: 'TC-001', name: '用户登录功能验证', module: '登录模块', priority: 'L0', scriptPath: 'scripts/test_login.py', steps: '1. 打开应用\n2. 输入用户名密码\n3. 点击登录', expected: '成功登录进入主页', creator: '张三', createTime: '2026-04-01T08:00:00', createdAt: '2026-04-01T08:00:00' },
      { id: 2, caseId: 'TC-002', name: '用户注册功能验证', module: '登录模块', priority: 'L0', scriptPath: 'scripts/test_register.py', steps: '1. 打开注册页面\n2. 填写必填项\n3. 提交注册', expected: '注册成功并自动登录', creator: '张三', createTime: '2026-04-01T08:00:00', createdAt: '2026-04-01T08:00:00' },
      { id: 3, caseId: 'TC-003', name: '首页加载性能', module: '性能测试', priority: 'L2', scriptPath: 'scripts/test_homepage.py', steps: '1. 打开应用\n2. 记录首页加载时间', expected: '首页在3秒内加载完成', creator: '李四', createTime: '2026-04-02T08:00:00', createdAt: '2026-04-02T08:00:00' },
      { id: 4, caseId: 'TC-004', name: '搜索功能测试', module: '搜索', priority: 'L0', scriptPath: 'scripts/test_search.py', steps: '1. 进入搜索页面\n2. 输入关键词\n3. 查看搜索结果', expected: '搜索结果准确相关', creator: '李四', createTime: '2026-04-02T08:00:00', createdAt: '2026-04-02T08:00:00' },
      { id: 5, caseId: 'TC-005', name: '主题切换功能', module: 'UI', priority: 'L4', scriptPath: 'scripts/test_theme.py', steps: '1. 进入设置\n2. 切换主题\n3. 验证UI显示', expected: '主题切换成功，UI显示正常', creator: '王五', createTime: '2026-04-03T08:00:00', createdAt: '2026-04-03T08:00:00' },
      { id: 6, caseId: 'TC-006', name: '消息推送验证', module: '消息', priority: 'L2', scriptPath: 'scripts/test_push.py', steps: '1. 触发推送事件\n2. 检查通知栏', expected: '收到正确推送消息', creator: '王五', createTime: '2026-04-03T08:00:00', createdAt: '2026-04-03T08:00:00' },
      { id: 7, caseId: 'TC-007', name: '文件下载功能', module: '文件管理', priority: 'L2', scriptPath: 'scripts/test_download.py', steps: '1. 点击下载按钮\n2. 等待下载完成\n3. 检查文件', expected: '文件成功下载到本地', creator: '张三', createTime: '2026-04-04T08:00:00', createdAt: '2026-04-04T08:00:00' },
    ]

    caseSets.value = [
      { id: 1, name: '基础功能回归集', description: '涵盖登录、注册、搜索等核心功能的回归用例集', caseIds: [1, 2, 4], createdAt: '2026-04-05T08:00:00' },
      { id: 2, name: '性能测试用例集', description: '首页加载、列表滑动等性能测试用例', caseIds: [3], createdAt: '2026-04-06T08:00:00' },
      { id: 3, name: 'UI 兼容性用例集', description: '主题切换、布局适配等 UI 相关用例', caseIds: [5], createdAt: '2026-04-07T08:00:00' },
    ]

    branchTaskConfigs.value = [
      { id: 1, branchId: 1, name: '稳定性压力测试', scriptPath: 'scripts/stress_test.py', deviceLimit: 'SN001,SN002', caseSets: [1], batchSize: 5, order: 1, createdAt: '2026-05-26T08:00:00' },
      { id: 2, branchId: 1, name: '功能回归测试', scriptPath: 'scripts/regression.py', deviceLimit: 'SN001', caseSets: [1, 3], batchSize: 10, order: 2, createdAt: '2026-05-26T08:00:00' },
      { id: 3, branchId: 2, name: '主干全量回归', scriptPath: 'scripts/full_regression.py', deviceLimit: '', caseSets: [1, 2, 3], batchSize: 8, order: 1, createdAt: '2026-05-26T08:00:00' },
    ]

    // 刷机过程模拟数据
    flashingProcesses.value = [
      {
        id: 1, deviceId: 1, deviceSerial: 'ABC123DEF456', branchId: 1, branchName: 'DEV-V14.0.1',
        model: '小米14', romVersion: 'TQ3A.230605.010', status: 'flashing', retryCount: 0, currentStepIndex: 2,
        steps: [
          { name: '下载ROM', key: 'download_rom', status: 'success', progress: 100, retryCount: 0 },
          { name: '刷机', key: 'flash', status: 'success', progress: 100, retryCount: 0 },
          { name: '开机引导', key: 'boot_setup', status: 'running', progress: 60, retryCount: 0 },
          { name: '登录WiFi', key: 'wifi_login', status: 'pending', progress: 0, retryCount: 0 },
        ],
        createdAt: '2026-05-27T10:00:00',
        updatedAt: '2026-05-27T12:00:00'
      },
      {
        id: 2, deviceId: 2, deviceSerial: 'DEF789GHI012', branchId: 1, branchName: 'DEV-V14.0.1',
        model: '小米14', romVersion: 'TQ3A.230605.010', status: 'failed', retryCount: 2, errorMessage: '刷机失败：设备断开连接', currentStepIndex: 1,
        steps: [
          { name: '下载ROM', key: 'download_rom', status: 'success', progress: 100, retryCount: 0 },
          { name: '刷机', key: 'flash', status: 'failed', progress: 45, retryCount: 2, errorMessage: '刷机失败：设备断开连接' },
          { name: '开机引导', key: 'boot_setup', status: 'pending', progress: 0, retryCount: 0 },
          { name: '登录WiFi', key: 'wifi_login', status: 'pending', progress: 0, retryCount: 0 },
        ],
        createdAt: '2026-05-27T08:00:00',
        updatedAt: '2026-05-27T09:30:00'
      },
      {
        id: 3, deviceId: 3, deviceSerial: 'GHI345JKL678', branchId: 2, branchName: '主干-V15.0',
        model: 'Redmi K70', romVersion: 'MIUI 14.0.5', status: 'success', retryCount: 1, currentStepIndex: 4,
        steps: [
          { name: '下载ROM', key: 'download_rom', status: 'success', progress: 100, retryCount: 0 },
          { name: '刷机', key: 'flash', status: 'success', progress: 100, retryCount: 1 },
          { name: '开机引导', key: 'boot_setup', status: 'success', progress: 100, retryCount: 0 },
          { name: '登录WiFi', key: 'wifi_login', status: 'success', progress: 100, retryCount: 0 },
        ],
        createdAt: '2026-05-26T10:00:00',
        updatedAt: '2026-05-26T12:00:00'
      },
    ]

    // ROM 版本记录模拟数据
    romRecords.value = [
      // ── 已覆盖 - 全部通过 ──
      {
        id: 1, romVersion: 'TQ3A.230605.010', model: 'ALN-00',
        branchId: 1, branchName: 'DEV-0.1.0', branchType: 'DEV',
        deviceSerial: 'ABC123DEF456', status: 'success', emailTitle: '版本 TQ3A.230605.010 构建完成',
        emailReceivedAt: '2026-05-27T10:00:00', updatedAt: '2026-05-27T11:00:00', flashingProcessId: 1,
        tasksStatus: 'completed',
        taskResults: [
          { taskConfigId: 1, name: '稳定性压力测试', status: 'success', passRate: 98, totalCount: 200, passCount: 196, failCount: 2, errorCount: 2, duration: 3600, startedAt: '2026-05-27T10:05:00', endedAt: '2026-05-27T11:00:00' },
          { taskConfigId: 2, name: '兼容性测试', status: 'success', passRate: 97, totalCount: 150, passCount: 145, failCount: 3, errorCount: 2, duration: 2400, startedAt: '2026-05-27T10:05:00', endedAt: '2026-05-27T10:50:00' },
          { taskConfigId: 3, name: '性能基准测试', status: 'success', passRate: 100, totalCount: 50, passCount: 50, failCount: 0, errorCount: 0, duration: 1800, startedAt: '2026-05-27T10:05:00', endedAt: '2026-05-27T10:35:00' },
        ],
      },
      // ── 已覆盖 - 有失败项 ──
      {
        id: 2, romVersion: 'TQ3A.230425.005', model: 'ALN-00',
        branchId: 1, branchName: 'DEV-0.1.0', branchType: 'DEV',
        deviceSerial: 'ABC123DEF456', status: 'success', emailTitle: '版本 TQ3A.230425.005 构建通知',
        emailReceivedAt: '2026-05-25T10:00:00', updatedAt: '2026-05-25T11:30:00', flashingProcessId: 2,
        tasksStatus: 'completed',
        taskResults: [
          { taskConfigId: 1, name: '稳定性压力测试', status: 'failed', passRate: 72, totalCount: 200, passCount: 144, failCount: 45, errorCount: 11, duration: 3200, startedAt: '2026-05-25T10:05:00', endedAt: '2026-05-25T10:59:00' },
          { taskConfigId: 2, name: '兼容性测试', status: 'success', passRate: 95, totalCount: 150, passCount: 142, failCount: 5, errorCount: 3, duration: 2200, startedAt: '2026-05-25T10:05:00', endedAt: '2026-05-25T10:45:00' },
        ],
      },
      // ── 已覆盖 - 全部通过 ──
      {
        id: 3, romVersion: 'TQ3A.230410.001', model: 'ALN-00',
        branchId: 1, branchName: 'DEV-0.1.0', branchType: 'DEV',
        deviceSerial: 'ABC123DEF456', status: 'success', emailTitle: '版本 TQ3A.230410.001 构建完成',
        emailReceivedAt: '2026-05-23T10:00:00', updatedAt: '2026-05-23T11:15:00', flashingProcessId: 3,
        tasksStatus: 'completed',
        taskResults: [
          { taskConfigId: 1, name: '稳定性压力测试', status: 'success', passRate: 96, totalCount: 200, passCount: 192, failCount: 5, errorCount: 3, duration: 3500, startedAt: '2026-05-23T10:05:00', endedAt: '2026-05-23T11:00:00' },
          { taskConfigId: 3, name: '性能基准测试', status: 'success', passRate: 100, totalCount: 50, passCount: 50, failCount: 0, errorCount: 0, duration: 1500, startedAt: '2026-05-23T10:05:00', endedAt: '2026-05-23T10:30:00' },
        ],
      },
      // ── 覆盖中：刷机完成，任务执行中 ──
      {
        id: 4, romVersion: 'V15.0.0.240501', model: 'PHZ110',
        branchId: 2, branchName: '主干-0.2.5', branchType: '主干',
        deviceSerial: 'YZA789BCD012', status: 'success', emailTitle: '版本 V15.0.0.240501 构建完成',
        emailReceivedAt: '2026-05-27T10:30:00', updatedAt: '2026-05-27T12:00:00', flashingProcessId: 4,
        tasksStatus: 'running',
        taskResults: [
          { taskConfigId: 4, name: '稳定性压力测试', status: 'running', passRate: 55, totalCount: 100, passCount: 55, failCount: 0, errorCount: 0, duration: 1800, startedAt: '2026-05-27T11:00:00' },
          { taskConfigId: 5, name: '兼容性测试', status: 'queued', passRate: 0, totalCount: 0, passCount: 0, failCount: 0, errorCount: 0 },
        ],
      },
      // ── 覆盖中：刷机中（尚未执行任务） ──
      {
        id: 5, romVersion: 'V15.0.0.240425', model: 'PHZ110',
        branchId: 2, branchName: '主干-0.2.5', branchType: '主干',
        deviceSerial: 'YZA789BCD012', status: 'flashing', emailTitle: '版本 V15.0.0.240425 已释放',
        emailReceivedAt: '2026-05-25T10:00:00', updatedAt: '2026-05-25T10:30:00', flashingProcessId: 5,
        tasksStatus: 'pending',
        taskResults: [],
      },
      // ── 未覆盖：未匹配分支 ──
      {
        id: 6, romVersion: 'V14.0.5.240428', model: 'BVL-AN00',
        branchId: 0, branchName: '-', branchType: '-',
        status: 'no_match', reason: '版本 V14.0.5.240428 未匹配到任何分支规则', emailTitle: '版本 V14.0.5.240428 发布',
        emailReceivedAt: '2026-05-24T10:00:00', updatedAt: '2026-05-24T10:05:00',
      },
      // ── 未覆盖：无对应设备 ──
      {
        id: 7, romVersion: 'OneUI 6.1.240520', model: 'SM-S9280',
        branchId: 3, branchName: '商分-3.0.1', branchType: '商分',
        status: 'no_device', reason: '未找到可用设备（型号 SM-S9280）', emailTitle: '版本 OneUI 6.1.240520 可用',
        emailReceivedAt: '2026-05-26T09:00:00', updatedAt: '2026-05-26T09:02:00',
      },
      // ── 未覆盖：等待排队中 ──
      {
        id: 8, romVersion: 'V14.0.6.240515', model: '23127PN0CC',
        branchId: 3, branchName: '商分-3.0.1', branchType: '商分',
        status: 'waiting', reason: '设备已被其他刷机任务占用，排在第 2 位', emailTitle: '版本 V14.0.6.240515 准备就绪',
        emailReceivedAt: '2026-05-27T08:00:00', updatedAt: '2026-05-27T08:10:00',
      },
      // ── 未覆盖：刷机失败（可跳转重试） ──
      {
        id: 9, romVersion: 'HyperOS 1.0.5.240510', model: '23113RKC6C',
        branchId: 4, branchName: 'DEV-0.3.0', branchType: 'DEV',
        status: 'failed', reason: '下载 ROM 文件超时（已重试 3 次）', emailTitle: '版本 HyperOS 1.0.5.240510 构建完成',
        emailReceivedAt: '2026-05-22T14:00:00', updatedAt: '2026-05-22T15:30:00', flashingProcessId: 9,
      },
      // ── 覆盖中：刷机完成等待执行任务 ──
      {
        id: 10, romVersion: 'TQ3A.230515.008', model: 'ALN-00',
        branchId: 1, branchName: 'DEV-0.1.0', branchType: 'DEV',
        deviceSerial: 'ABC123DEF456', status: 'success', emailTitle: '版本 TQ3A.230515.008 构建成功',
        emailReceivedAt: '2026-05-21T09:00:00', updatedAt: '2026-05-21T10:00:00', flashingProcessId: 10,
        tasksStatus: 'pending',
        taskResults: [],
      },
      // ── 未覆盖：待分配设备 ──
      {
        id: 11, romVersion: 'ColorOS 14.1.240520', model: 'PJH110',
        branchId: 5, branchName: '商分-2.4.0', branchType: '商分',
        status: 'matched', emailTitle: '版本 ColorOS 14.1.240520 准备测试',
        emailReceivedAt: '2026-05-20T11:00:00', updatedAt: '2026-05-20T11:05:00',
      },
    ]

    loaded.value = true
  }

  return {
    devices,
    tasks,
    branches,
    testCases,
    caseSets,
    flashingProcesses,
    branchTaskConfigs,
    romRecords,
    loaded,
    loading,
    useMock,
    fetchAll,
    toggleMock,
    initMockData,
  }
})
