<template>
  <div class="flash-page">
    <!-- 头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-icon :size="22" color="#409eff"><Opportunity /></el-icon>
        <span class="header-title">刷机管理</span>
        <el-tag size="small" type="primary" effect="plain" round>
          {{ versionGroups.length }} 个版本
        </el-tag>
      </div>
      <div class="header-right">
        <el-select v-model="statusFilter" placeholder="版本状态" clearable size="small" style="width: 120px">
          <el-option label="全部" value="" />
          <el-option label="排队中" value="pending" />
          <el-option label="刷机中" value="running" />
          <el-option label="已完成" value="success" />
          <el-option label="失败" value="failed" />
        </el-select>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索设备号/ROM版本..."
          clearable
          size="small"
          style="width: 180px"
        />
        <el-button size="small" :icon="Search" @click="handleSearch">查询</el-button>
      </div>
    </div>

    <!-- 统计行 -->
    <div class="stats-row">
      <div v-for="s in flashStats" :key="s.key" class="stat-card" :style="{ borderLeftColor: s.color }">
        <div class="stat-value" :style="{ color: s.color }">{{ s.count }}</div>
        <div class="stat-label">{{ s.label }}</div>
      </div>
    </div>

    <!-- 版本分组列表 -->
    <div class="version-list">
      <div
        v-for="group in pagedGroups"
        :key="group.key"
        :id="'group-' + group.key"
        class="version-group"
        :class="'group-' + group.overallStatus"
      >
        <!-- 版本组头部 -->
        <div class="group-header" @click="toggleGroupExpand(group.key)">
          <div class="group-icon" :class="group.overallStatus">
            <el-icon :size="20">
              <Opportunity v-if="group.overallStatus === 'pending'" />
              <Refresh v-else-if="group.overallStatus === 'flashing'" />
              <CircleCheck v-else-if="group.overallStatus === 'success'" />
              <CircleClose v-else />
            </el-icon>
          </div>
          <div class="group-info">
            <div class="group-title-row">
              <span class="group-version">{{ group.versionLabel }}</span>
            </div>
            <div class="group-meta">
              <span>{{ group.processes.length }} 台设备</span>
              <span class="meta-divider">·</span>
              <span v-if="group.lastUpdated">更新: {{ formatTime(group.lastUpdated) }}</span>
            </div>
          </div>
          <div class="group-status">
            <el-tag :type="statusType(group.overallStatus)" size="small" effect="light">
              {{ statusText(group.overallStatus) }}
            </el-tag>
            <el-icon :size="16" class="expand-icon" :class="{ expanded: expandedGroups.has(group.key) }">
              <ArrowDown />
            </el-icon>
          </div>
          <el-button
            v-if="group.overallStatus === 'pending'"
            size="small"
            type="primary"
            :loading="dispatchLoading[group.key]"
            @click.stop="dispatchGroupFlash(group)"
          >
            <el-icon :size="14" style="margin-right:4px"><Refresh /></el-icon>
            下发刷机
          </el-button>
        </div>

        <!-- 组内设备卡片列表 -->
        <Transition name="slide">
          <div v-if="expandedGroups.has(group.key)" class="group-body">
            <div
              v-for="process in group.processes"
              :key="process.id"
              class="device-card"
              :class="[process.status, { 'device-card-focused': process.id === focusId }]"
              :id="'flash-card-' + process.id"
            >
              <!-- 设备卡片头部 -->
              <div class="device-header" @click="toggleDeviceExpand(process.id)">
                <div class="device-main">
                  <div class="device-icon" :class="process.status">
                    <el-icon :size="16">
                      <Opportunity v-if="process.status === 'pending'" />
                      <Refresh v-else-if="process.status === 'running'" />
                      <CircleCheck v-else-if="process.status === 'success'" />
                      <CircleClose v-else />
                    </el-icon>
                  </div>
                  <div class="device-content">
                    <div class="device-title-row">
                      <span class="device-model">{{ process.deviceModel || '未知型号' }}</span>
                      <span class="device-serial">{{ process.deviceSerial }}</span>
                    </div>
                    <div class="device-meta">
                      <span class="meta-chip">{{ formatTime(process.createdAt) }}</span>
                    </div>
                  </div>
                </div>
                <div class="device-status">
                  <el-tag :type="statusType(process.status)" size="small" effect="light">
                    <span v-if="process.status === 'running'" class="tag-spinner">
                      <el-icon :size="12" style="margin-right: 2px;"><Refresh /></el-icon>
                    </span>
                    {{ statusText(process.status) }}
                  </el-tag>
                  <el-icon :size="14" class="expand-icon" :class="{ expanded: expandedDevices.has(process.id) }">
                    <ArrowDown />
                  </el-icon>
                </div>
              </div>

              <!-- 设备刷机详情 -->
              <Transition name="slide">
                <div v-if="expandedDevices.has(process.id)" class="device-detail">
                  <el-divider style="margin: 6px 0 12px;" />

                  <!-- 刷机步骤时间线 -->
                  <div class="step-timeline">
                    <div
                      v-for="(step, idx) in process.steps"
                      :key="step.name"
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
                            effect="plain"
                          >进行中</el-tag>
                          <el-tag
                            v-else-if="step.status === 'pending'"
                            size="small"
                            type="info"
                            effect="plain"
                          >等待中</el-tag>
                        </div>
                        <div class="step-error" v-if="step.errorMessage">
                          <div class="error-title">错误详情</div>
                          <pre class="error-detail">{{ step.errorMessage }}</pre>
                        </div>
                        <div class="step-footer" v-if="step.retryCount !== undefined">
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

                  <!-- 设备刷机底部操作 -->
                  <el-divider style="margin: 4px 0 10px;" />
                  <div class="device-footer">
                    <div class="footer-info">
                      <span class="footer-label">设备:</span>
                      <span>{{ process.deviceSerial }}</span>
                      <span class="footer-divider">|</span>
                      <span class="footer-label">型号:</span>
                      <span>{{ process.deviceModel || '未知型号' }}</span>
                      <span class="footer-divider">|</span>
                      <span class="footer-label">ROM:</span>
                      <span>{{ process.rom || '-' }}</span>
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
                        v-if="process.status === 'pending' || process.status === 'running'"
                      >取消刷机</el-button>
                    </div>
                  </div>
                </div>
              </Transition>
            </div>
          </div>
        </Transition>
      </div>

      <!-- 分页 -->
      <div v-if="filteredGroups.length > pageSize" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredGroups.length"
          :pager-count="5"
          layout="prev, pager, next"
          size="small"
          background
        />
      </div>

      <div v-if="!filteredGroups.length" class="empty-state">
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
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Refresh, CircleCheck, CircleClose, ArrowDown, Opportunity
} from '@element-plus/icons-vue'
import type { FlashingProcess, FlashingStep } from '@/types'
import { dispatchFlashing, retryFlashingStep, retryAllFlashingSteps } from '@/api'

interface FlashVersionGroup {
  key: string
  versionLabel: string
  processes: FlashingProcess[]
  overallStatus: string
  lastUpdated: string
}

const appStore = useAppStore()
const route = useRoute()

const statusFilter = ref('')
const searchKeyword = ref('')
const expandedGroups = ref<Set<string>>(new Set())
const expandedDevices = ref<Set<number>>(new Set())
const focusId = ref<number | null>(null)

// 下发刷机状态
const dispatchLoading = ref<Record<string, boolean>>({})
const pollingTimer = ref<ReturnType<typeof setInterval> | null>(null)
const hasRunning = ref(false)

// 检查是否有进行中的刷机，自动启动/停止轮询
const checkAndPoll = () => {
  const running = versionGroups.value.some(g => g.overallStatus === 'running' || g.overallStatus === 'pending')
  hasRunning.value = running
  if (running && !pollingTimer.value) {
    pollingTimer.value = setInterval(async () => {
      await appStore.fetchFlashingProcesses()
      handleSearch()
    }, 5000) // 每 5 秒轮询
  } else if (!running && pollingTimer.value) {
    clearInterval(pollingTimer.value)
    pollingTimer.value = null
  }
}

const flashingProcesses = computed(() => appStore.flashingProcesses)

// 构建版本分组
const versionGroups = computed(() => {
  const groups = new Map<string, FlashVersionGroup>()
  for (const p of flashingProcesses.value) {
    const key = p.versionLabel || p.deviceSerial
    if (!groups.has(key)) {
      groups.set(key, {
        key,
        versionLabel: p.versionLabel || p.deviceSerial,
        processes: [],
        overallStatus: 'pending',
        lastUpdated: ''
      })
    }
    groups.get(key)!.processes.push(p)
  }
  // 计算每个组的整体状态和时间
  for (const g of groups.values()) {
    // 整体状态：有 flashing 则 flashing，有 failed 则 failed，有 pending 则 pending，全 success 则 success
    const hasRunning = g.processes.some(p => p.status === 'running')
    const hasFailed = g.processes.some(p => p.status === 'failed')
    const hasPending = g.processes.some(p => p.status === 'pending')
    if (hasRunning) g.overallStatus = 'running'
    else if (hasFailed) g.overallStatus = 'failed'
    else if (hasPending) g.overallStatus = 'pending'
    else g.overallStatus = 'success'

    // 取最晚更新时间
    g.lastUpdated = g.processes.reduce((latest, p) => {
      return (p.updatedAt > latest) ? p.updatedAt : latest
    }, '')
  }
  // 按最后更新时间排序，最新的在前
  return Array.from(groups.values()).sort((a, b) => {
    if (a.lastUpdated > b.lastUpdated) return -1
    if (a.lastUpdated < b.lastUpdated) return 1
    return 0
  })
})

// 筛选
const filteredGroups = ref<FlashVersionGroup[]>([])

const currentPage = ref(1)
const pageSize = 10
const pagedGroups = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredGroups.value.slice(start, start + pageSize)
})

const handleSearch = () => {
  currentPage.value = 1
  let result = versionGroups.value
  if (statusFilter.value) {
    result = result.filter(g => g.overallStatus === statusFilter.value)
  }
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(g =>
      g.versionLabel.toLowerCase().includes(kw) ||
      g.processes.some(p =>
        p.deviceSerial.toLowerCase().includes(kw) ||
        (p.deviceModel || '').toLowerCase().includes(kw)
      )
    )
  }
  filteredGroups.value = result
}

// 统计
const flashStats = computed(() => [
  { key: 'total', label: '总版本数', count: versionGroups.value.length, color: '#409eff' },
  { key: 'pending', label: '排队中', count: versionGroups.value.filter(g => g.overallStatus === 'pending').length, color: '#e6a23c' },
  { key: 'running', label: '刷机中', count: versionGroups.value.filter(g => g.overallStatus === 'running').length, color: '#409eff' },
  { key: 'success', label: '全量成功', count: versionGroups.value.filter(g => g.overallStatus === 'success').length, color: '#67c23a' },
  { key: 'failed', label: '存在失败', count: versionGroups.value.filter(g => g.overallStatus === 'failed').length, color: '#f56c6c' }
])

const statusType = (s: string) => {
  const map: Record<string, string> = { pending: 'warning', running: 'primary', success: 'success', failed: 'danger' }
  return map[s] || 'info'
}

const statusText = (s: string) => {
  const map: Record<string, string> = { pending: '排队中', running: '刷机中', success: '全部完成', failed: '存在失败' }
  return map[s] || s
}

const formatTime = (t: string) => {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', {
    month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit'
  })
}

// 展开/折叠
const toggleGroupExpand = (key: string) => {
  const newSet = new Set(expandedGroups.value)
  if (newSet.has(key)) {
    newSet.delete(key)
  } else {
    newSet.add(key)
  }
  expandedGroups.value = newSet
}

const toggleDeviceExpand = (id: number) => {
  const newSet = new Set(expandedDevices.value)
  if (newSet.has(id)) {
    newSet.delete(id)
  } else {
    newSet.add(id)
  }
  expandedDevices.value = newSet
}

// 重试
const retryStep = async (process: FlashingProcess, step: FlashingStep) => {
  try {
    await ElMessageBox.confirm(
      `确定重试步骤「${step.name}」吗？将从该步骤重新开始。`,
      '重试确认',
      { type: 'warning', confirmButtonText: '重试', cancelButtonText: '取消' }
    )
    const result = await retryFlashingStep(process.id, step.name)
    if (result.code === 0) {
      step.status = 'running'
      step.errorMessage = undefined
      step.retryCount = (step.retryCount || 0) + 1
      process.status = 'running'
      ElMessage.success(`已开始重试步骤: ${step.name}`)
    } else {
      ElMessage.error(result.message || '重试失败')
    }
  } catch { /* canceled */ }
}

const retryAll = async (process: FlashingProcess) => {
  try {
    await ElMessageBox.confirm(
      '确定从失败的步骤开始全部重试吗？',
      '全部重试',
      { type: 'warning', confirmButtonText: '重试', cancelButtonText: '取消' }
    )
    const result = await retryAllFlashingSteps(process.id)
    if (result.code === 0) {
      const failedIdx = process.steps.findIndex(s => s.status === 'failed')
      for (let i = failedIdx; i < process.steps.length; i++) {
        const s = process.steps[i]
        if (s.status === 'failed' || s.status === 'pending') {
          s.status = i === failedIdx ? 'running' : 'pending'
          s.errorMessage = undefined
          if (i === failedIdx) s.retryCount = (s.retryCount || 0) + 1
        }
      }
      process.status = 'running'
      ElMessage.success('已开始全部重试')
    } else {
      ElMessage.error(result.message || '重试失败')
    }
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

// 下发刷机
const dispatchGroupFlash = async (group: FlashVersionGroup) => {
  const versionLabel = group.versionLabel
  dispatchLoading.value[group.key] = true

  try {
    // 通过版本标签找到对应的版本 ID
    const matchedVersions = appStore.versions.filter(v => v.version === versionLabel)
    if (matchedVersions.length === 0) {
      ElMessage.warning('未找到匹配的版本记录，请先同步版本数据')
      return
    }
    const version = matchedVersions[0]
    const result = await dispatchFlashing(version.id)
    if (result.code === 0) {
      ElMessage.success(`已下发刷机任务到 ${result.data?.process_count || 0} 台设备`)
      // 展开此分组
      expandedGroups.value = new Set([group.key])
      // 刷新数据并启动轮询
      await appStore.fetchFlashingProcesses()
      handleSearch()
      checkAndPoll()
    } else {
      ElMessage.error(result.message || '下发刷机失败')
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '下发刷机失败')
  } finally {
    dispatchLoading.value[group.key] = false
  }
}

// URL 焦点跳转 — 支持两种模式
onMounted(async () => {
  await Promise.all([
    appStore.fetchFlashingProcesses(),
    appStore.fetchVersions(),
  ])
  handleSearch()

  // 启动自动轮询（如果有进行中的刷机）
  checkAndPoll()

  const focusVersion = route.query.version as string
  if (focusVersion) {
    // 版本级焦点：展开对应版本分组
    for (const g of versionGroups.value) {
      if (g.versionLabel === focusVersion) {
        expandedGroups.value = new Set([g.key])
        await nextTick()
        setTimeout(() => {
          const el = document.getElementById(`group-${g.key}`)
          if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'center' })
            el.classList.add('group-focused')
            setTimeout(() => el.classList.remove('group-focused'), 2000)
          }
        }, 200)
        break
      }
    }
  } else {
    // 原有的设备级焦点（兼容旧链接）
    const focus = route.query.focus
    if (focus) {
      const id = parseInt(focus as string, 10)
      if (!isNaN(id)) {
        focusId.value = id
        // 找到所属分组并展开
        for (const g of versionGroups.value) {
          if (g.processes.some(p => p.id === id)) {
            expandedGroups.value = new Set([g.key])
            expandedDevices.value = new Set([id])
            await nextTick()
            setTimeout(() => {
              const el = document.getElementById(`flash-card-${id}`)
              if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'center' })
                el.classList.add('device-card-focused')
                setTimeout(() => el.classList.remove('device-card-focused'), 2000)
              }
            }, 200)
            break
          }
        }
      }
    }
  }
})

// 组件卸载时清理轮询
onUnmounted(() => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
    pollingTimer.value = null
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

/* ==================== 版本分组 ==================== */
.version-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.version-group {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  overflow: hidden;
  transition: all 0.3s;
}

.version-group:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

.group-failed {
  border-left: 3px solid #f56c6c;
}

.group-flashing {
  border-left: 3px solid #409eff;
}

.group-success {
  border-left: 3px solid #67c23a;
}

.group-pending {
  border-left: 3px solid #e6a23c;
}

/* 版本组头部 */
.group-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  cursor: pointer;
  user-select: none;
}

.group-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.group-icon.pending { background: #fdf6ec; }
.group-icon.flashing { background: #ecf5ff; }
.group-icon.success { background: #f0f9eb; }
.group-icon.failed { background: #fef0f0; }

.group-icon.pending :deep(.el-icon) { color: #e6a23c; }
.group-icon.flashing :deep(.el-icon) { color: #409eff; }
.group-icon.success :deep(.el-icon) { color: #67c23a; }
.group-icon.failed :deep(.el-icon) { color: #f56c6c; }

.group-info {
  flex: 1;
  min-width: 0;
}

.group-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 3px;
}

.group-version {
  font-size: 15px;
  font-weight: 700;
  color: #303133;
}

.group-branch {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  border-radius: 4px;
  padding: 1px 6px;
}

.group-meta {
  font-size: 12px;
  color: #909399;
}

.group-status {
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

/* ==================== 组内设备卡片 ==================== */
.group-body {
  padding: 0 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  animation: slideDown 0.25s ease;
}

.device-card {
  border: 1px solid #ebeef5;
  border-radius: 10px;
  overflow: hidden;
  transition: all 0.3s;
}

.device-card:hover {
  border-color: #c0c4cc;
}

.device-card.failed {
  border-left: 3px solid #f56c6c;
}

.device-card.flashing {
  border-left: 3px solid #409eff;
}

.device-card.success {
  border-left: 3px solid #67c23a;
}

.device-card.pending {
  border-left: 3px solid #e6a23c;
}

.device-card-focused {
  animation: deviceFlash 0.5s ease 3;
}

.group-focused {
  animation: groupFlash 1s ease 2;
}

@keyframes groupFlash {
  0%, 100% { box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
  50% { box-shadow: 0 0 0 4px rgba(64,158,255,0.3), 0 2px 12px rgba(64,158,255,0.15); }
}

@keyframes deviceFlash {
  0%, 100% { box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
  50% { box-shadow: 0 0 0 4px rgba(245,108,108,0.4), 0 2px 12px rgba(245,108,108,0.2); }
}

/* 设备卡片头部 */
.device-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  cursor: pointer;
  user-select: none;
  background: #fafbfc;
}

.device-main {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.device-icon {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.device-icon.pending { background: #fdf6ec; }
.device-icon.flashing { background: #ecf5ff; }
.device-icon.success { background: #f0f9eb; }
.device-icon.failed { background: #fef0f0; }

.device-icon.pending :deep(.el-icon),
.device-icon.flashing :deep(.el-icon) { color: #409eff; }
.device-icon.success :deep(.el-icon) { color: #67c23a; }
.device-icon.failed :deep(.el-icon) { color: #f56c6c; }

.device-content {
  flex: 1;
  min-width: 0;
}

.device-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}

.device-model {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.device-serial {
  font-size: 11px;
  color: #909399;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
}

.device-meta {
  font-size: 11px;
  color: #909399;
}

.device-status {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

/* 设备刷机详情 */
.device-detail {
  padding: 0 14px 10px;
  animation: slideDown 0.25s ease;
}

.device-footer {
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

/* ==================== 动画 ==================== */
@keyframes slideDown {
  from { opacity: 0; max-height: 0; }
  to { opacity: 1; max-height: 1000px; }
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
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

/* ==================== 分页 ==================== */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 12px 0 4px;
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
  .device-footer {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
}
</style>
