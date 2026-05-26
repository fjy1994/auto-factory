<template>
  <div class="task-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span>任务中心</span>
            <el-tabs v-model="activeTab" class="header-tabs">
              <el-tab-pane name="queue">
                <span class="tab-with-badge">
                  待执行队列
                  <el-badge v-if="versionQueue.length" :value="versionQueue.length" class="item" />
                </span>
              </el-tab-pane>
              <el-tab-pane label="版本测试概览" name="versions" />
            </el-tabs>
          </div>
          <el-button type="primary" @click="openCreateTaskDialog">
            <el-icon><Plus /></el-icon>
            手动创建
          </el-button>
        </div>
      </template>

      <!-- 待执行队列 -->
      <div v-if="activeTab === 'queue'" class="queue-section">
        <el-alert
          title="以下版本已收到转测通知，但尚未创建执行任务"
          type="info"
          :closable="false"
          style="margin-bottom: 20px;"
        />
        <el-table :data="versionQueue" style="width: 100%">
          <el-table-column prop="branchName" label="分支" width="100" />
          <el-table-column prop="version" label="版本号" width="130" />
          <el-table-column prop="models" label="目标机型" width="150">
            <template #default="{ row }">
              <el-tag v-for="model in row.models" :key="model" size="small" style="margin-right: 4px;">
                {{ model }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="队列状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getQueueStatusType(row.status)" size="small">
                {{ getQueueStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="原因说明" min-width="180" show-overflow-tooltip />
          <el-table-column prop="receivedAt" label="收到时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.receivedAt) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="createTasksFromQueue(row)">
                立即创建
              </el-button>
              <el-button link type="danger" size="small" @click="ignoreQueueItem(row)">
                忽略
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!versionQueue.length" description="暂无待执行版本" style="margin-top: 40px;" />
      </div>

      <!-- 版本测试概览 -->
      <div v-if="activeTab === 'versions'" class="versions-section">
        <!-- 筛选栏 -->
        <div class="filter-bar">
          <el-select v-model="versionFilters.branch" placeholder="筛选分支" clearable style="width: 130px; margin-right: 10px;">
            <el-option label="开发7.1" :value="1" />
            <el-option label="主干7.0" :value="2" />
          </el-select>
          <el-input v-model="versionFilters.version" placeholder="搜索版本" clearable style="width: 150px; margin-right: 10px;" />
          <el-button type="primary" @click="fetchTasks">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>

        <!-- 按分支分组的版本列表 -->
        <div class="branch-group" v-for="branch in groupedVersions" :key="branch.branchId">
          <div class="branch-header">
            <h3>{{ branch.branchName }}</h3>
            <span class="branch-stats">共 {{ branch.versions.length }} 个版本</span>
          </div>
          
          <div class="version-cards">
            <div 
              class="version-card" 
              v-for="version in branch.versions" 
              :key="version.version"
              @click="expandVersion(version)"
            >
              <div class="version-header">
                <div class="version-info">
                  <span class="version-name">{{ version.version }}</span>
                  <span class="version-time">{{ formatTime(version.firstTaskTime) }}</span>
                </div>
                <div class="version-status">
                  <el-tag :type="getVersionStatusType(version)" size="small">
                    {{ getVersionStatusText(version) }}
                  </el-tag>
                </div>
              </div>
              
              <div class="version-progress">
                <div class="progress-item">
                  <span class="progress-label">整体进度</span>
                  <el-progress :percentage="version.avgProgress" :stroke-width="8" />
                </div>
                <div v-if="version.avgPassRate !== null" class="progress-item">
                  <span class="progress-label">平均通过率</span>
                  <el-progress :percentage="version.avgPassRate" :stroke-width="8" status="success" />
                </div>
              </div>
              
              <div class="version-stats">
                <div class="stat-item">
                  <span class="stat-value">{{ version.taskCount }}</span>
                  <span class="stat-label">任务数</span>
                </div>
                <div class="stat-item success">
                  <span class="stat-value">{{ version.successCount }}</span>
                  <span class="stat-label">成功</span>
                </div>
                <div class="stat-item danger">
                  <span class="stat-value">{{ version.failCount }}</span>
                  <span class="stat-label">失败</span>
                </div>
                <div class="stat-item info">
                  <span class="stat-value">{{ version.runningCount }}</span>
                  <span class="stat-label">执行中</span>
                </div>
              </div>

              <div class="version-expand">
                <el-icon class="expand-icon"><ArrowDown /></el-icon>
              </div>
            </div>
          </div>
        </div>

        <el-empty v-if="!groupedVersions.length" description="暂无版本数据" style="margin-top: 60px;" />
      </div>
    </el-card>

    <!-- 版本详情弹窗 -->
    <el-dialog
      v-model="versionDetailVisible"
      :title="`${currentVersionData?.branchName} - ${currentVersionData?.version}`"
      width="1000px"
      destroy-on-close
    >
      <div class="version-detail-header">
        <div class="version-summary">
          <div class="summary-item">
            <span class="summary-label">版本号</span>
            <span class="summary-value">{{ currentVersionData?.version }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">整体状态</span>
            <el-tag :type="getVersionStatusType(currentVersionData!)" size="small">
              {{ getVersionStatusText(currentVersionData!) }}
            </el-tag>
          </div>
          <div class="summary-item">
            <span class="summary-label">平均通过率</span>
            <span class="summary-value">{{ currentVersionData?.avgPassRate ?? '-' }}%</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">任务总数</span>
            <span class="summary-value">{{ currentVersionData?.tasks.length }}</span>
          </div>
        </div>
      </div>

      <div class="task-list-section">
        <h4>任务列表</h4>
        <el-table :data="currentVersionData?.tasks || []" style="width: 100%">
          <el-table-column prop="name" label="任务名称" width="180" />
          <el-table-column prop="model" label="机型" width="100" />
          <el-table-column prop="taskType" label="类型" width="100" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="进度/通过率" width="160">
            <template #default="{ row }">
              <el-progress :percentage="row.passRate ?? row.progress" :stroke-width="6" />
            </template>
          </el-table-column>
          <el-table-column prop="deviceSerial" label="执行设备" width="140">
            <template #default="{ row }">
              {{ row.deviceSerial || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="showTaskDetail(row)">
                查看详情
              </el-button>
              <el-button
                v-if="row.status === 'success' || row.status === 'failed'"
                link type="success"
                size="small"
                @click="downloadReport(row)"
              >
                报告
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 任务详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      title="任务详情"
      width="900px"
      destroy-on-close
    >
      <template v-if="currentTask">
        <el-descriptions :column="3" border size="small" style="margin-bottom: 20px;">
          <el-descriptions-item label="任务名称">{{ currentTask.name }}</el-descriptions-item>
          <el-descriptions-item label="分支">{{ currentTask.branchName }}</el-descriptions-item>
          <el-descriptions-item label="版本号">{{ currentTask.version }}</el-descriptions-item>
          <el-descriptions-item label="机型">{{ currentTask.model }}</el-descriptions-item>
          <el-descriptions-item label="任务类型">{{ currentTask.taskType }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentTask.status)">{{ getStatusText(currentTask.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="执行设备" :span="2">{{ currentTask.deviceSerial || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(currentTask.createdAt) }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatTime(currentTask.startTime) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ formatTime(currentTask.endTime) }}</el-descriptions-item>
        </el-descriptions>

        <div class="progress-section">
          <div class="progress-label">执行进度</div>
          <el-progress :percentage="currentTask.progress" :stroke-width="20" />
        </div>

        <div class="log-section">
          <div class="log-label">执行日志</div>
          <div class="log-content">
            <pre v-for="(log, index) in taskLogs" :key="index">{{ log }}</pre>
          </div>
        </div>
      </template>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button v-if="currentTask?.status === 'queued' || currentTask?.status === 'running'" type="danger" @click="cancelTask(currentTask)">
          取消任务
        </el-button>
      </template>
    </el-dialog>

    <!-- 手动创建任务弹窗 -->
    <el-dialog
      v-model="createTaskVisible"
      title="手动创建任务"
      width="500px"
    >
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="选择分支" required>
          <el-select v-model="taskForm.branchId" placeholder="请选择分支">
            <el-option v-for="branch in branches" :key="branch.id" :label="branch.name" :value="branch.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="版本号" required>
          <el-input v-model="taskForm.version" placeholder="如: B32SP21" />
        </el-form-item>
        <el-form-item label="机型" required>
          <el-input v-model="taskForm.model" placeholder="如: Pixel 7" />
        </el-form-item>
        <el-form-item label="任务类型" required>
          <el-select v-model="taskForm.taskType" placeholder="请选择任务类型">
            <el-option label="功能测试" value="功能测试" />
            <el-option label="稳定性测试" value="稳定性测试" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createTaskVisible = false">取消</el-button>
        <el-button type="primary" @click="createTask">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, ArrowDown } from '@element-plus/icons-vue'
import type { Task, VersionQueue } from '@/types'

const appStore = useAppStore()

const activeTab = ref('versions')
const loading = ref(false)
const detailVisible = ref(false)
const createTaskVisible = ref(false)
const versionDetailVisible = ref(false)
const currentTask = ref<Task | null>(null)
const currentVersionData = ref<any>(null)

const filters = ref({
  branch: null as number | null,
  version: '',
  taskType: '',
  status: '',
  dateRange: null as [Date, Date] | null
})

const versionFilters = ref({
  branch: null as number | null,
  version: ''
})

// 从 store 获取任务
const tasks = computed(() => appStore.tasks)

const filteredTasks = computed(() => {
  let result = tasks.value
  
  if (filters.value.branch) {
    result = result.filter(t => t.branchId === filters.value.branch)
  }
  if (filters.value.version) {
    result = result.filter(t => t.version.includes(filters.value.version))
  }
  if (filters.value.taskType) {
    result = result.filter(t => t.taskType === filters.value.taskType)
  }
  if (filters.value.status) {
    result = result.filter(t => t.status === filters.value.status)
  }
  
  return result
})

// 版本分组数据
interface VersionGroup {
  version: string
  branchId: number
  branchName: string
  tasks: Task[]
  taskCount: number
  successCount: number
  failCount: number
  runningCount: number
  avgProgress: number
  avgPassRate: number | null
  firstTaskTime: string
  overallStatus: string
}

// 待执行队列
const versionQueue = ref<VersionQueue[]>([
  {
    id: 101,
    branchId: 1,
    branchName: '开发7.1',
    version: 'B32SP22',
    models: ['Pixel 7', 'MI 12'],
    status: 'waiting_rom',
    reason: '暂无 Pixel 7 机型的对应 ROM 包',
    receivedAt: new Date(Date.now() - 1800000).toISOString(),
    expectedTasks: ['功能自动化用例', '稳定性自动化用例']
  },
  {
    id: 102,
    branchId: 2,
    branchName: '主干7.0',
    version: 'B30SP16',
    models: ['Pixel 7'],
    status: 'waiting_device',
    reason: '所有 Pixel 7 设备正在执行其他任务，等待空闲',
    receivedAt: new Date(Date.now() - 3600000).toISOString(),
    expectedTasks: ['功能自动化用例']
  }
])

// 显示报告相关列（当有已完成任务时显示）
const showReportColumns = computed(() => {
  return tasks.value.some(t => t.passRate !== undefined)
})

// 按分支和版本分组
const groupedVersions = computed(() => {
  const versionMap = new Map<string, VersionGroup>()
  
  // 按版本分组
  tasks.value.forEach(task => {
    const key = `${task.branchId}_${task.version}`
    if (!versionMap.has(key)) {
      versionMap.set(key, {
        version: task.version,
        branchId: task.branchId,
        branchName: task.branchName,
        tasks: [],
        taskCount: 0,
        successCount: 0,
        failCount: 0,
        runningCount: 0,
        avgProgress: 0,
        avgPassRate: null,
        firstTaskTime: task.createdAt,
        overallStatus: ''
      })
    }
    const group = versionMap.get(key)!
    group.tasks.push(task)
    group.taskCount++
    
    if (task.status === 'success') group.successCount++
    if (task.status === 'failed') group.failCount++
    if (task.status === 'running') group.runningCount++
    
    if (new Date(task.createdAt) < new Date(group.firstTaskTime)) {
      group.firstTaskTime = task.createdAt
    }
  })
  
  // 计算每个版本的平均进度和通过率
  versionMap.forEach(group => {
    const totalProgress = group.tasks.reduce((sum, t) => sum + t.progress, 0)
    group.avgProgress = Math.round(totalProgress / group.tasks.length)
    
    const completedTasks = group.tasks.filter(t => t.passRate !== undefined)
    if (completedTasks.length > 0) {
      const totalPassRate = completedTasks.reduce((sum, t) => sum + (t.passRate || 0), 0)
      group.avgPassRate = Math.round(totalPassRate / completedTasks.length)
    }
  })
  
  // 按分支分组
  const branchMap = new Map<number, { branchId: number; branchName: string; versions: VersionGroup[] }>()
  versionMap.forEach(group => {
    if (!branchMap.has(group.branchId)) {
      branchMap.set(group.branchId, {
        branchId: group.branchId,
        branchName: group.branchName,
        versions: []
      })
    }
    branchMap.get(group.branchId)!.versions.push(group)
  })
  
  // 筛选
  let result = Array.from(branchMap.values())
  
  if (versionFilters.value.branch) {
    result = result.filter(b => b.branchId === versionFilters.value.branch)
  }
  
  if (versionFilters.value.version) {
    result = result.map(branch => ({
      ...branch,
      versions: branch.versions.filter(v => v.version.includes(versionFilters.value.version!))
    })).filter(b => b.versions.length > 0)
  }
  
  // 按时间排序，最新的版本在前
  result.forEach(branch => {
    branch.versions.sort((a, b) => new Date(b.firstTaskTime).getTime() - new Date(a.firstTaskTime).getTime())
  })
  
  return result
})

const getVersionStatusType = (version: VersionGroup) => {
  if (version.runningCount > 0) return 'primary'
  if (version.failCount > 0) return 'danger'
  if (version.successCount === version.taskCount) return 'success'
  return 'info'
}

const getVersionStatusText = (version: VersionGroup) => {
  if (version.runningCount > 0) return '执行中'
  if (version.failCount > 0) return '有失败'
  if (version.successCount === version.taskCount) return '全部通过'
  if (version.successCount > 0) return '部分完成'
  return '排队中'
}

const expandVersion = (version: VersionGroup) => {
  currentVersionData.value = version
  versionDetailVisible.value = true
}

const taskForm = ref({
  branchId: null as number | null,
  version: '',
  model: '',
  taskType: ''
})

const taskLogs = ref([
  '[2024-01-15 10:00:00] 任务开始执行',
  '[2024-01-15 10:00:01] 正在更新代码仓库...',
  '[2024-01-15 10:00:15] 代码更新完成',
  '[2024-01-15 10:00:16] 准备测试环境...',
  '[2024-01-15 10:00:30] 开始执行用例 1/100',
  '[2024-01-15 10:00:45] 用例1: 通过',
  '[2024-01-15 10:01:00] 用例2: 通过',
  '[2024-01-15 10:01:15] 用例3: 通过',
  '[2024-01-15 10:01:30] 用例4: 通过',
  '[2024-01-15 10:01:45] 用例5: 通过'
])

const branches = ref([
  { id: 1, name: '开发7.1' },
  { id: 2, name: '主干7.0' },
  { id: 3, name: '商分6.1' }
])

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    queued: 'info',
    running: 'primary',
    success: 'success',
    failed: 'danger',
    error: 'danger',
    cancelled: 'info'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    queued: '排队中',
    running: '执行中',
    success: '成功',
    failed: '失败',
    error: '异常',
    cancelled: '已取消'
  }
  return map[status] || status
}

const formatTime = (time: string) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const fetchTasks = () => {
  ElMessage.success('任务列表已刷新')
}

const showTaskDetail = (task: Task) => {
  currentTask.value = task
  detailVisible.value = true
}

const cancelTask = (task: Task) => {
  ElMessageBox.confirm(
    `确定要取消任务 "${task.name}" 吗？`,
    '确认取消',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    task.status = 'cancelled'
    ElMessage.success('任务已取消')
    detailVisible.value = false
  }).catch(() => {})
}

const rerunTask = (task: Task) => {
  ElMessage.success('任务重跑指令已下发')
}

const downloadReport = (task: Task) => {
  ElMessage.success('报告下载中...')
}

const getQueueStatusType = (status: string) => {
  const map: Record<string, string> = {
    waiting_rom: 'warning',
    waiting_device: 'info',
    pending: ''
  }
  return map[status] || 'info'
}

const getQueueStatusText = (status: string) => {
  const map: Record<string, string> = {
    waiting_rom: '等待ROM',
    waiting_device: '等待设备',
    pending: '待执行'
  }
  return map[status] || status
}

const createTasksFromQueue = (item: VersionQueue) => {
  ElMessage.success(`已为版本 ${item.version} 创建 ${item.expectedTasks.length} 个任务`)
  const index = versionQueue.value.findIndex(v => v.id === item.id)
  if (index > -1) {
    versionQueue.value.splice(index, 1)
  }
  activeTab.value = 'tasks'
}

const ignoreQueueItem = (item: VersionQueue) => {
  ElMessageBox.confirm(
    `确定要忽略版本 ${item.version} 吗？忽略后将不再为该版本自动创建任务。`,
    '确认忽略',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const index = versionQueue.value.findIndex(v => v.id === item.id)
    if (index > -1) {
      versionQueue.value.splice(index, 1)
    }
    ElMessage.success('已忽略该版本')
  }).catch(() => {})
}

const openCreateTaskDialog = () => {
  taskForm.value = {
    branchId: null,
    version: '',
    model: '',
    taskType: ''
  }
  createTaskVisible.value = true
}

const createTask = () => {
  if (!taskForm.value.branchId || !taskForm.value.version || !taskForm.value.model || !taskForm.value.taskType) {
    ElMessage.warning('请填写所有必填项')
    return
  }

  const branchName = branches.value.find(b => b.id === taskForm.value.branchId)?.name || ''
  
  const newTask: Task = {
    id: Date.now(),
    name: `${taskForm.value.taskType}任务`,
    branchId: taskForm.value.branchId,
    branchName,
    version: taskForm.value.version,
    model: taskForm.value.model,
    taskType: taskForm.value.taskType,
    status: 'queued',
    progress: 0,
    deviceId: 0,
    deviceSerial: '',
    startTime: '',
    endTime: '',
    createdAt: new Date().toISOString()
  }
  
  appStore.tasks.unshift(newTask)
  ElMessage.success('任务创建成功')
  createTaskVisible.value = false
}

onMounted(() => {
  if (!appStore.tasks.length) {
    appStore.initMockData()
  }
})
</script>

<style scoped>
.task-page {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.progress-section {
  margin-bottom: 20px;
}

.progress-label {
  font-weight: 500;
  margin-bottom: 10px;
}

.log-section {
  margin-top: 20px;
}

.log-label {
  font-weight: 500;
  margin-bottom: 10px;
}

.log-content {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 15px;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.log-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 30px;
}

.header-tabs {
  margin-bottom: -15px;
}

.tab-with-badge {
  display: flex;
  align-items: center;
  gap: 6px;
}

.queue-section {
  padding-top: 10px;
}

.versions-section {
  padding-top: 10px;
}

.branch-group {
  margin-bottom: 30px;
}

.branch-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 6px;
  margin-bottom: 16px;
}

.branch-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.branch-stats {
  font-size: 13px;
  color: #909399;
}

.version-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.version-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
  background: #fff;
  position: relative;
}

.version-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.version-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.version-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.version-time {
  font-size: 12px;
  color: #909399;
}

.version-progress {
  margin-bottom: 12px;
}

.progress-item {
  margin-bottom: 8px;
}

.progress-label {
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
  display: block;
}

.version-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  text-align: center;
}

.stat-item .stat-value {
  display: block;
  font-size: 20px;
  font-weight: 600;
  color: #606266;
}

.stat-item.success .stat-value {
  color: #67c23a;
}

.stat-item.danger .stat-value {
  color: #f56c6c;
}

.stat-item.info .stat-value {
  color: #409eff;
}

.stat-item .stat-label {
  font-size: 12px;
  color: #909399;
}

.version-expand {
  position: absolute;
  bottom: 8px;
  right: 12px;
}

.expand-icon {
  color: #c0c4cc;
  font-size: 18px;
}

.version-detail-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.version-summary {
  display: flex;
  gap: 40px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-label {
  font-size: 12px;
  color: #909399;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.task-list-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}
</style>
