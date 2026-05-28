<template>
  <div class="task-page">
    <!-- 头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-icon :size="22" color="#409eff"><List /></el-icon>
        <span class="header-title">任务中心</span>
        <el-tag size="small" type="primary" effect="plain" round>
          {{ tasks.length }} 个任务
        </el-tag>
      </div>
      <div class="header-right">
        <el-select v-model="statusFilter" placeholder="状态" clearable size="small" style="width: 120px">
          <el-option label="全部" value="" />
          <el-option label="排队中" value="queued" />
          <el-option label="运行中" value="running" />
          <el-option label="已完成" value="success" />
          <el-option label="失败" value="failed" />
        </el-select>
        <el-button type="primary" size="small" :icon="Plus" @click="createTask">
          新建任务
        </el-button>
      </div>
    </div>

    <!-- 统计行 -->
    <div class="stats-row">
      <div v-for="s in taskStats" :key="s.key" class="stat-item" :style="{ borderLeftColor: s.color }">
        <div class="stat-value" :style="{ color: s.color }">{{ s.count }}</div>
        <div class="stat-label">{{ s.label }}</div>
      </div>
    </div>

    <!-- 任务列表 -->
    <div class="task-list">
      <div v-for="task in pagedTasks" :key="task.id" class="task-item" :id="'task-item-' + task.id" :class="{ 'task-item-selected': task.id === selectedId }" @click="showDetail(task)">
        <div class="task-main">
          <div class="task-indicator" :class="task.status">
            <span v-if="task.status === 'running'" class="running-dot"></span>
          </div>
          <div class="task-content">
            <div class="task-header">
              <span class="task-name">{{ task.name }}</span>
              <el-tag
                :type="statusType(task.status)"
                size="small"
                effect="light"
              >
                <span v-if="task.status === 'running'" class="tag-spinner">
                  <el-icon :size="12" style="margin-right: 2px;"><Refresh /></el-icon>
                </span>
                {{ statusText(task.status) }}
              </el-tag>
            </div>
            <div class="task-meta">
              <span class="meta-chip">
                <el-icon :size="12"><Monitor /></el-icon>
                {{ task.deviceSerial || '-' }}
              </span>
              <span class="meta-divider">|</span>
              <span class="meta-chip">
                <el-icon :size="12"><Share /></el-icon>
                {{ task.branchName || '-' }}
              </span>
              <span class="meta-divider">|</span>
              <span class="meta-chip">
                <el-icon :size="12"><Clock /></el-icon>
                {{ formatTime(task.createdAt) }}
              </span>
            </div>
          </div>
          <div class="task-progress" v-if="task.status === 'running'">
            <el-progress
              :percentage="task.progress || 0"
              :stroke-width="6"
              color="#409eff"
              :width="40"
              type="circle"
            />
          </div>
          <div class="task-duration" v-else-if="task.duration">
            <div class="duration-value">{{ task.duration }}</div>
            <div class="duration-label">耗时</div>
          </div>
        </div>

        <!-- 详情展开 -->
        <Transition name="slide">
          <div v-if="selectedId === task.id" class="task-detail">
            <el-divider style="margin: 10px 0;" />
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">设备</span>
                <span class="detail-value">{{ task.model }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">分支</span>
                <span class="detail-value">{{ task.branchName || '-' }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">创建时间</span>
                <span class="detail-value">{{ task.createdAt }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">版本</span>
                <span class="detail-value">{{ task.version || '-' }}</span>
              </div>
              <div class="detail-item full-width" v-if="task.log">
                <span class="detail-label">执行日志</span>
                <div class="log-box">{{ task.log }}</div>
              </div>
            </div>
            <div class="detail-actions">
              <el-button size="small" type="success" plain @click="startTaskExec(task)" v-if="task.status === 'queued'">
                <el-icon :size="14"><VideoPlay /></el-icon> 开始执行
              </el-button>
              <el-button size="small" type="primary" plain @click="rerunTask(task)" v-if="task.status === 'failed'">
                <el-icon :size="14"><Refresh /></el-icon> 重新运行
              </el-button>
              <el-button size="small" type="danger" plain @click="cancelTask(task)" v-if="task.status === 'queued' || task.status === 'running'">
                <el-icon :size="14"><CircleClose /></el-icon> 取消任务
              </el-button>
            </div>

            <!-- 用例执行结果 -->
            <div v-if="task.caseResults && task.caseResults.length > 0" class="case-results-section">
              <el-divider style="margin: 10px 0;" />
              <div class="section-title">用例执行结果</div>
              <div class="case-result-grid">
                <div
                  v-for="r in task.caseResults"
                  :key="r.caseId"
                  class="case-result-item"
                  :class="'status-' + r.status"
                >
                  <div class="cr-top">
                    <el-tag :type="r.status === 'passed' ? 'success' : r.status === 'failed' ? 'danger' : 'warning'" size="small" effect="dark" round>
                      {{ r.status === 'passed' ? '通过' : r.status === 'failed' ? '失败' : '错误' }}
                    </el-tag>
                    <span class="cr-id">{{ r.caseId }}</span>
                  </div>
                  <div class="cr-meta" v-if="r.duration">
                    耗时: {{ r.duration.toFixed(1) }}s
                  </div>
                  <div class="cr-error" v-if="r.error">
                    {{ r.error.slice(0, 200) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </div>

      <!-- 分页 -->
      <div v-if="filteredTasks.length > pageSize" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredTasks.length"
          :pager-count="5"
          layout="prev, pager, next"
          size="small"
          background
        />
      </div>

      <div v-if="!filteredTasks.length" class="empty-state">
        <el-empty :image-size="100" description="暂无任务数据">
          <template #image>
            <div class="empty-icon"><el-icon :size="48" color="#c0c4cc"><List /></el-icon></div>
          </template>
          <el-button type="primary" size="small" :icon="Plus" @click="createTask">新建任务</el-button>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  List, Plus, Refresh, Monitor, Share, Clock, CircleClose, VideoPlay
} from '@element-plus/icons-vue'
import type { Task } from '@/types'
import { startTask } from '@/api'

const appStore = useAppStore()
const route = useRoute()

const statusFilter = ref('')
const selectedId = ref<number | null>(null)

const tasks = computed(() => appStore.tasks)

const filteredTasks = computed(() => {
  let result = tasks.value
  if (statusFilter.value) {
    result = result.filter(t => t.status === statusFilter.value)
  }
  return result
})

const currentPage = ref(1)
const pageSize = 20
const pagedTasks = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredTasks.value.slice(start, start + pageSize)
})

watch(statusFilter, () => { currentPage.value = 1 })

const taskStats = computed(() => [
  { key: 'total', label: '总任务', count: tasks.value.length, color: '#409eff' },
  { key: 'queued', label: '排队中', count: tasks.value.filter(t => t.status === 'queued').length, color: '#e6a23c' },
  { key: 'running', label: '运行中', count: tasks.value.filter(t => t.status === 'running').length, color: '#409eff' },
  { key: 'success', label: '已完成', count: tasks.value.filter(t => t.status === 'success').length, color: '#67c23a' },
  { key: 'failed', label: '失败', count: tasks.value.filter(t => t.status === 'failed').length, color: '#f56c6c' }
])

const statusType = (s: string) => {
  const map: Record<string, string> = { queued: 'warning', running: 'primary', success: 'success', failed: 'danger' }
  return map[s] || 'info'
}

const statusText = (s: string) => {
  const map: Record<string, string> = { queued: '排队中', running: '运行中', success: '已完成', failed: '失败' }
  return map[s] || s
}

const formatTime = (t: string) => {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', {
    month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
  })
}

const showDetail = (task: Task) => {
  selectedId.value = selectedId.value === task.id ? null : task.id
}

const createTask = () => {
  ElMessage.success('新建任务功能已打开')
}

const rerunTask = (task: Task) => {
  ElMessage.success(`任务 "${task.name}" 已重新提交`)
}

const cancelTask = (task: Task) => {
  ElMessage.warning(`任务 "${task.name}" 已取消`)
}

const startTaskExec = async (task: Task) => {
  // 弹出输入框让用户输入 Agent 地址
  const { value: agentUrl } = await ElMessageBox.prompt(
    '请输入 Agent 服务地址（如 http://192.168.1.100:8000）',
    '启动任务执行',
    {
      confirmButtonText: '启动',
      cancelButtonText: '取消',
      inputValue: task.agentUrl || '',
      inputPlaceholder: 'http://192.168.1.100:8000',
    }
  ).catch(() => ({ value: null }))

  if (!agentUrl) return

  try {
    await startTask(task.id, agentUrl)
    ElMessage.success('任务调度已启动')
    task.status = 'running'
    task.agentUrl = agentUrl
    task.startTime = new Date().toISOString()
    appStore.fetchAll() // 刷新数据
  } catch (e: any) {
    ElMessage.error('启动失败: ' + (e.response?.data?.error || e.message))
  }
}

// 从版本跟踪跳转过来时自动选中对应任务
onMounted(async () => {
  const focus = route.query.focus
  if (focus) {
    const id = parseInt(focus as string, 10)
    if (!isNaN(id) && tasks.value.some(t => t.id === id)) {
      selectedId.value = id
      await nextTick()
      setTimeout(() => {
        const el = document.getElementById(`task-item-${id}`)
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' })
          el.classList.add('task-item-highlight')
          setTimeout(() => el.classList.remove('task-item-highlight'), 2000)
        }
      }, 200)
    }
  }
})
</script>

<style scoped>
.task-page {
  display: flex;
  flex-direction: column;
  gap: 14px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== 头部 ==================== */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-radius: 12px;
  padding: 14px 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-title {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* ==================== 统计条 ==================== */
.stats-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}

.stat-item {
  background: #fff;
  border-radius: 10px;
  padding: 14px 16px;
  border-left: 4px solid;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  transition: transform 0.2s;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

/* ==================== 任务列表 ==================== */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item {
  background: #fff;
  border-radius: 12px;
  padding: 14px 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  cursor: pointer;
  transition: all 0.3s;
  overflow: hidden;
}

.task-item.task-item-selected {
  border: 2px solid #409eff;
  box-shadow: 0 2px 12px rgba(64,158,255,0.15);
}

.task-item-highlight {
  animation: taskPulse 1.5s ease 2;
}

@keyframes taskPulse {
  0%, 100% { box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
  50% { box-shadow: 0 0 0 3px rgba(64,158,255,0.3), 0 2px 12px rgba(64,158,255,0.15); }
}

.task-item:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

.task-main {
  display: flex;
  align-items: center;
  gap: 14px;
}

.task-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  position: relative;
}

.task-indicator.pending { background: #e6a23c; }
.task-indicator.running { background: #409eff; }
.task-indicator.success { background: #67c23a; }
.task-indicator.failed { background: #f56c6c; }

.running-dot {
  position: absolute;
  top: -3px;
  left: -3px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid #409eff;
  animation: pulse 2s ease-out infinite;
  opacity: 0;
}

@keyframes pulse {
  0% { transform: scale(0.5); opacity: 1; }
  100% { transform: scale(1.8); opacity: 0; }
}

.task-content {
  flex: 1;
  min-width: 0;
}

.task-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.task-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  color: #909399;
}

.meta-divider {
  font-size: 10px;
  color: #dcdfe6;
}

.task-progress {
  flex-shrink: 0;
}

.task-duration {
  text-align: center;
  flex-shrink: 0;
  padding: 4px 10px;
  background: #f5f7fa;
  border-radius: 8px;
}

.duration-value {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  font-variant-numeric: tabular-nums;
}

.duration-label {
  font-size: 10px;
  color: #c0c4cc;
}

/* ==================== 详情展开 ==================== */
.task-detail {
  animation: slideDown 0.25s ease;
}

@keyframes slideDown {
  from { opacity: 0; max-height: 0; }
  to { opacity: 1; max-height: 500px; }
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.detail-item {
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-label {
  display: block;
  font-size: 11px;
  color: #909399;
  margin-bottom: 3px;
}

.detail-value {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
}

.log-box {
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 12px;
  padding: 10px 12px;
  border-radius: 6px;
  max-height: 120px;
  overflow-y: auto;
  white-space: pre-wrap;
  margin-top: 4px;
}

.detail-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

/* ==================== 标签旋转动画 ==================== */
.tag-spinner {
  display: inline-flex;
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ==================== 空状态 ==================== */
.empty-state {
  background: #fff;
  border-radius: 12px;
  padding: 40px 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

/* ==================== 响应式 ==================== */
/* ==================== 用例执行结果 ==================== */
.case-results-section {
  margin-top: 4px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.case-result-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px;
  max-height: 300px;
  overflow-y: auto;
}

.case-result-item {
  background: #f8f9fb;
  border-radius: 8px;
  padding: 8px 10px;
  border-left: 3px solid #e0e0e0;
}

.case-result-item.status-passed {
  border-left-color: #67c23a;
}

.case-result-item.status-failed {
  border-left-color: #f56c6c;
}

.case-result-item.status-error {
  border-left-color: #e6a23c;
}

.cr-top {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 2px;
}

.cr-id {
  font-size: 12px;
  font-weight: 600;
  color: #303133;
}

.cr-meta {
  font-size: 11px;
  color: #909399;
  margin-top: 2px;
}

.cr-error {
  font-size: 11px;
  color: #f56c6c;
  margin-top: 2px;
  max-height: 60px;
  overflow-y: auto;
  background: #fff5f5;
  padding: 3px 6px;
  border-radius: 4px;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
}

@media (max-width: 1000px) {
  .stats-row {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 800px) {
  .page-header {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}
/* ==================== 分页 ==================== */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 12px 0 4px;
}
</style>
