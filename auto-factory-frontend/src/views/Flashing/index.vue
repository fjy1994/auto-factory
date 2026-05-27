<template>
  <div class="flash-page">
    <!-- 头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-icon :size="22" color="#409eff"><Opportunity /></el-icon>
        <span class="header-title">刷机管理</span>
        <el-tag size="small" type="primary" effect="plain" round>
          {{ flashingProcesses.length }} 个过程
        </el-tag>
      </div>
      <div class="header-right">
        <el-select v-model="statusFilter" placeholder="状态" clearable size="small" style="width: 120px">
          <el-option label="全部" value="" />
          <el-option label="排队中" value="pending" />
          <el-option label="刷机中" value="flashing" />
          <el-option label="已完成" value="success" />
          <el-option label="失败" value="failed" />
        </el-select>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索设备号/ROM版本..."
          clearable
          size="small"
          style="width: 220px"
          :prefix-icon="Search"
        />
      </div>
    </div>

    <!-- 统计行 -->
    <div class="stats-row">
      <div v-for="s in flashStats" :key="s.key" class="stat-card" :style="{ borderLeftColor: s.color }">
        <div class="stat-value" :style="{ color: s.color }">{{ s.count }}</div>
        <div class="stat-label">{{ s.label }}</div>
      </div>
    </div>

    <!-- 刷机列表 -->
    <div class="flash-list">
      <div
        v-for="process in pagedProcesses"
        :key="process.id"
        class="flash-card"
        :class="[process.status, { 'flash-card-highlight': process.id === focusId }]"
        :id="'flash-card-' + process.id"
      >
        <!-- 卡片头部 -->
        <div class="card-header" @click="toggleExpand(process.id)">
          <div class="card-main">
            <div class="card-icon" :class="process.status">
              <el-icon :size="18">
                <Opportunity v-if="process.status === 'pending'" />
                <Refresh v-else-if="process.status === 'flashing'" />
                <CircleCheck v-else-if="process.status === 'success'" />
                <CircleClose v-else />
              </el-icon>
            </div>
            <div class="card-content">
              <div class="card-title-row">
                <span class="card-model">{{ process.model }}</span>
                <span class="card-serial">{{ process.deviceSerial }}</span>
              </div>
              <div class="card-meta">
                <span class="meta-chip">
                  <el-icon :size="11"><Share /></el-icon>
                  {{ process.branchName }}
                </span>
                <span class="meta-divider">·</span>
                <span class="meta-chip">{{ process.romVersion }}</span>
                <span class="meta-divider">·</span>
                <span class="meta-chip">{{ formatTime(process.createdAt) }}</span>
              </div>
            </div>
          </div>
          <div class="card-status">
            <el-tag :type="statusType(process.status)" size="small" effect="light">
              <span v-if="process.status === 'flashing'" class="tag-spinner">
                <el-icon :size="12" style="margin-right: 2px;"><Refresh /></el-icon>
              </span>
              {{ statusText(process.status) }}
            </el-tag>
            <el-icon :size="16" class="expand-icon" :class="{ expanded: expandedIds.has(process.id) }">
              <ArrowDown />
            </el-icon>
          </div>
        </div>

        <!-- 展开详情 -->
        <Transition name="slide">
          <div v-if="expandedIds.has(process.id)" class="card-detail">
            <el-divider style="margin: 8px 0 14px;" />

            <!-- 刷机步骤时间线 -->
            <div class="step-timeline">
              <div
                v-for="(step, idx) in process.steps"
                :key="step.key"
                class="step-item"
                :class="[step.status]"
              >
                <div class="step-indicator">
                  <div class="step-dot" :class="step.status">
                    <el-icon v-if="step.status === 'success'" :size="12" color="#fff"><CircleCheck /></el-icon>
                    <el-icon v-else-if="step.status === 'failed'" :size="12" color="#fff"><CircleClose /></el-icon>
                    <span v-else-if="step.status === 'running'" class="inner-spinner">
                      <el-icon :size="12" color="#409eff"><Refresh /></el-icon>
                    </span>
                  </div>
                  <div v-if="idx < process.steps.length - 1" class="step-line" :class="{ done: step.status === 'success' }" />
                </div>
                <div class="step-content">
                  <div class="step-header">
                    <span class="step-name">{{ step.name }}</span>
                    <el-tag
                      v-if="step.status === 'running'"
                      size="small"
                      type="primary"
                      effect="dark"
                    >进行中</el-tag>
                    <el-tag
                      v-else-if="step.status === 'success'"
                      size="small"
                      type="success"
                      effect="plain"
                    >已完成</el-tag>
                    <el-tag
                      v-else-if="step.status === 'failed'"
                      size="small"
                      type="danger"
                      effect="light"
                    >失败</el-tag>
                    <el-tag
                      v-else
                      size="small"
                      type="info"
                      effect="plain"
                    >等待中</el-tag>
                  </div>
                  <div class="step-message" v-if="step.message">{{ step.message }}</div>
                  <div class="step-error" v-if="step.errorMessage">
                    <div class="error-title">错误详情</div>
                    <pre class="error-detail">{{ step.errorMessage }}</pre>
                  </div>
                  <div class="step-footer" v-if="step.startedAt || step.retryCount !== undefined">
                    <span v-if="step.startedAt" class="step-time">
                      开始: {{ formatTime(step.startedAt) }}
                    </span>
                    <span v-if="step.endedAt" class="step-time">
                      结束: {{ formatTime(step.endedAt) }}
                    </span>
                    <span v-if="step.retryCount" class="step-retry">
                      已重试 {{ step.retryCount }} 次
                    </span>
                  </div>
                  <div v-if="step.status === 'failed'" class="step-actions">
                    <el-button size="small" type="danger" :icon="Refresh" @click="retryStep(process, step)">
                      重试此步骤
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 整体操作 -->
            <el-divider style="margin: 8px 0 12px;" />
            <div class="detail-footer">
              <div class="footer-info">
                <span class="footer-label">设备:</span>
                <span>{{ process.deviceSerial }}</span>
                <span class="footer-divider">|</span>
                <span class="footer-label">ROM:</span>
                <span>{{ process.romVersion }}</span>
              </div>
              <div class="footer-actions">
                <el-button
                  size="small"
                  type="danger"
                  plain
                  :icon="Refresh"
                  @click="retryAll(process)"
                  v-if="process.status === 'failed'"
                >全部重试</el-button>
                <el-button
                  size="small"
                  type="warning"
                  plain
                  :icon="CircleClose"
                  @click="cancelFlash(process)"
                  v-if="process.status === 'pending' || process.status === 'flashing'"
                >取消刷机</el-button>
              </div>
            </div>
          </div>
        </Transition>
      </div>

      <!-- 分页 -->
      <div v-if="filteredProcesses.length > pageSize" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredProcesses.length"
          :pager-count="5"
          layout="prev, pager, next"
          size="small"
          background
        />
      </div>

      <div v-if="!filteredProcesses.length" class="empty-state">
        <el-empty :image-size="100" description="暂无刷机记录">
          <template #image>
            <div class="empty-icon"><el-icon :size="48" color="#c0c4cc"><Opportunity /></el-icon></div>
          </template>
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
  Search, Refresh, CircleCheck, CircleClose, ArrowDown, Opportunity, Share
} from '@element-plus/icons-vue'
import type { FlashingProcess, FlashingStep } from '@/types'

const appStore = useAppStore()
const route = useRoute()

const statusFilter = ref('')
const searchKeyword = ref('')
const expandedIds = ref<Set<number>>(new Set())
const focusId = ref<number | null>(null)

const flashingProcesses = computed(() => appStore.flashingProcesses)

const filteredProcesses = computed(() => {
  let result = flashingProcesses.value
  if (statusFilter.value) {
    result = result.filter(p => p.status === statusFilter.value)
  }
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(p =>
      p.deviceSerial.toLowerCase().includes(kw) ||
      p.romVersion.toLowerCase().includes(kw) ||
      p.model.toLowerCase().includes(kw)
    )
  }
  return result
})

const currentPage = ref(1)
const pageSize = 12
const pagedProcesses = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredProcesses.value.slice(start, start + pageSize)
})

watch([statusFilter, searchKeyword], () => { currentPage.value = 1 })

const flashStats = computed(() => [
  { key: 'total', label: '总刷机次数', count: flashingProcesses.value.length, color: '#409eff' },
  { key: 'pending', label: '排队中', count: flashingProcesses.value.filter(p => p.status === 'pending').length, color: '#e6a23c' },
  { key: 'flashing', label: '刷机中', count: flashingProcesses.value.filter(p => p.status === 'flashing').length, color: '#409eff' },
  { key: 'success', label: '刷机成功', count: flashingProcesses.value.filter(p => p.status === 'success').length, color: '#67c23a' },
  { key: 'failed', label: '刷机失败', count: flashingProcesses.value.filter(p => p.status === 'failed').length, color: '#f56c6c' }
])

const statusType = (s: string) => {
  const map: Record<string, string> = { pending: 'warning', flashing: 'primary', success: 'success', failed: 'danger' }
  return map[s] || 'info'
}

const statusText = (s: string) => {
  const map: Record<string, string> = { pending: '排队中', flashing: '刷机中', success: '刷机成功', failed: '失败' }
  return map[s] || s
}

const formatTime = (t: string) => {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', {
    month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit'
  })
}

const toggleExpand = (id: number) => {
  const newSet = new Set(expandedIds.value)
  if (newSet.has(id)) {
    newSet.delete(id)
  } else {
    newSet.add(id)
  }
  expandedIds.value = newSet
}

const retryStep = async (process: FlashingProcess, step: FlashingStep) => {
  try {
    await ElMessageBox.confirm(
      `确定重试步骤「${step.name}」吗？将从该步骤重新开始。`,
      '重试确认',
      { type: 'warning', confirmButtonText: '重试', cancelButtonText: '取消' }
    )
    step.status = 'running'
    step.message = '正在重试...'
    step.errorMessage = undefined
    step.retryCount = (step.retryCount || 0) + 1
    process.status = 'flashing'
    ElMessage.success(`已开始重试步骤: ${step.name}`)
  } catch { /* canceled */ }
}

const retryAll = async (process: FlashingProcess) => {
  try {
    await ElMessageBox.confirm(
      '确定从失败的步骤开始全部重试吗？',
      '全部重试',
      { type: 'warning', confirmButtonText: '重试', cancelButtonText: '取消' }
    )
    const failedIdx = process.steps.findIndex(s => s.status === 'failed')
    for (let i = failedIdx; i < process.steps.length; i++) {
      const s = process.steps[i]
      if (s.status === 'failed' || s.status === 'pending') {
        s.status = i === failedIdx ? 'running' : 'pending'
        s.message = i === failedIdx ? '正在重试...' : undefined
        s.errorMessage = undefined
        if (i === failedIdx) s.retryCount = (s.retryCount || 0) + 1
      }
    }
    process.status = 'flashing'
    process.currentStepIndex = failedIdx
    ElMessage.success('已开始全部重试')
  } catch { /* canceled */ }
}

const cancelFlash = async (process: FlashingProcess) => {
  try {
    await ElMessageBox.confirm(
      '确定要取消刷机吗？',
      '取消确认',
      { type: 'warning', confirmButtonText: '取消', cancelButtonText: '暂不' }
    )
    process.status = 'failed'
    ElMessage.warning(`刷机已取消: ${process.deviceSerial}`)
  } catch { /* canceled */ }
}

// URL 焦点跳转：从版本跟踪跳转过来时自动定位到对应刷机过程
onMounted(async () => {
  const focus = route.query.focus
  if (focus) {
    const id = parseInt(focus as string, 10)
    if (!isNaN(id)) {
      focusId.value = id
      // 自动展开并滚动到该卡片
      expandedIds.value = new Set([id])
      await nextTick()
      setTimeout(() => {
        const el = document.getElementById(`flash-card-${id}`)
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' })
          el.classList.add('flash-card-focused')
          setTimeout(() => el.classList.remove('flash-card-focused'), 2000)
        }
      }, 200)
    }
  }
})
</script>

<style scoped>
.flash-page {
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

/* ==================== 统计行 ==================== */
.stats-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}

.stat-card {
  background: #fff;
  border-radius: 10px;
  padding: 14px 16px;
  border-left: 4px solid;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  transition: transform 0.2s;
}

.stat-card:hover {
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

/* ==================== 刷机卡片列表 ==================== */
.flash-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.flash-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  overflow: hidden;
  transition: all 0.3s;
}

.flash-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

.flash-card-highlight {
  animation: cardPulse 1.5s ease 2;
}

@keyframes cardPulse {
  0%, 100% { box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
  50% { box-shadow: 0 0 0 3px rgba(64,158,255,0.3), 0 2px 12px rgba(64,158,255,0.15); }
}

.flash-card-focused {
  animation: cardFlash 0.5s ease 3;
}

@keyframes cardFlash {
  0%, 100% { box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
  50% { box-shadow: 0 0 0 4px rgba(245,108,108,0.4), 0 2px 12px rgba(245,108,108,0.2); }
}

.flash-card.failed {
  border-left: 3px solid #f56c6c;
}

.flash-card.flashing {
  border-left: 3px solid #409eff;
}

.flash-card.success {
  border-left: 3px solid #67c23a;
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  cursor: pointer;
  user-select: none;
}

.card-main {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.card-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-icon.pending { background: #fdf6ec; }
.card-icon.flashing { background: #ecf5ff; }
.card-icon.success { background: #f0f9eb; }
.card-icon.failed { background: #fef0f0; }

.card-icon.pending :deep(.el-icon),
.card-icon.flashing :deep(.el-icon) { color: #409eff; }
.card-icon.success :deep(.el-icon) { color: #67c23a; }
.card-icon.failed :deep(.el-icon) { color: #f56c6c; }

.card-content {
  flex: 1;
  min-width: 0;
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 3px;
}

.card-model {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.card-serial {
  font-size: 12px;
  color: #909399;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

.meta-divider {
  color: #dcdfe6;
  font-size: 10px;
}

/* 状态区 */
.card-status {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.expand-icon {
  color: #c0c4cc;
  transition: transform 0.3s;
}

.expand-icon.expanded {
  transform: rotate(180deg);
  color: #409eff;
}

/* ==================== 详情展开 ==================== */
.card-detail {
  padding: 0 20px 14px;
  animation: slideDown 0.25s ease;
}

@keyframes slideDown {
  from { opacity: 0; max-height: 0; }
  to { opacity: 1; max-height: 1000px; }
}

/* ==================== 步骤时间线 ==================== */
.step-timeline {
  padding-left: 4px;
}

.step-item {
  display: flex;
  gap: 14px;
  padding: 4px 0;
}

.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 24px;
  flex-shrink: 0;
}

.step-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid;
  flex-shrink: 0;
  background: #fff;
  transition: all 0.3s;
}

.step-dot.success {
  background: #67c23a;
  border-color: #67c23a;
}

.step-dot.failed {
  background: #f56c6c;
  border-color: #f56c6c;
}

.step-dot.running {
  background: #ecf5ff;
  border-color: #409eff;
  animation: pulse 2s ease-out infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.4); }
  70% { box-shadow: 0 0 0 8px rgba(64, 158, 255, 0); }
  100% { box-shadow: 0 0 0 0 rgba(64, 158, 255, 0); }
}

.step-dot.pending {
  background: #fff;
  border-color: #dcdfe6;
}

.step-line {
  width: 2px;
  flex: 1;
  min-height: 16px;
  background: #e4e7ed;
  margin: 2px 0;
}

.step-line.done {
  background: #67c23a;
}

/* 步骤内容 */
.step-content {
  flex: 1;
  padding-bottom: 12px;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.step-name {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.step-message {
  font-size: 12px;
  color: #606266;
  padding: 4px 8px;
  background: #f5f7fa;
  border-radius: 4px;
  display: inline-block;
  margin: 2px 0;
}

.step-error {
  margin: 6px 0;
}

.error-title {
  font-size: 11px;
  font-weight: 600;
  color: #f56c6c;
  margin-bottom: 4px;
}

.error-detail {
  background: #1e1e1e;
  color: #f48771;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 11px;
  padding: 8px 10px;
  border-radius: 6px;
  white-space: pre-wrap;
  line-height: 1.5;
  max-height: 100px;
  overflow-y: auto;
  margin: 0;
}

.step-footer {
  display: flex;
  gap: 12px;
  margin-top: 4px;
}

.step-time,
.step-retry {
  font-size: 11px;
  color: #c0c4cc;
}

.step-actions {
  margin-top: 6px;
}

/* 详情底部 */
.detail-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.footer-info {
  font-size: 12px;
  color: #909399;
}

.footer-label {
  color: #c0c4cc;
  margin-right: 2px;
}

.footer-divider {
  margin: 0 6px;
  color: #dcdfe6;
}

.footer-actions {
  display: flex;
  gap: 8px;
}

/* ==================== 标签旋转动画 ==================== */
.tag-spinner {
  display: inline-flex;
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.inner-spinner {
  display: flex;
  animation: spin 1.5s linear infinite;
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
  .detail-footer {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
}
/* ==================== 分页 ==================== */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 12px 0 4px;
}
</style>
