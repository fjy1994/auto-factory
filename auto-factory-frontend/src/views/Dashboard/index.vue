<template>
  <div class="dashboard-page">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <div class="welcome-icon">
          <el-icon :size="56" color="var(--primary)"><Monitor /></el-icon>
        </div>
        <div class="welcome-text">
          <div class="greeting">自动化测试工厂</div>
          <div class="subtitle">高效 · 稳定 · 智能的设备管理与自动化测试平台</div>
        </div>
      </div>
      <div class="welcome-stats">
        <div class="ws-item">
          <div class="ws-value">{{ totalDevices }}</div>
          <div class="ws-label">设备总数</div>
        </div>
        <div class="ws-divider" />
        <div class="ws-item">
          <div class="ws-value">{{ runningTasks }}</div>
          <div class="ws-label">运行中任务</div>
        </div>
        <div class="ws-divider" />
        <div class="ws-item">
          <div class="ws-value">{{ branches }}</div>
          <div class="ws-label">分支数</div>
        </div>
      </div>
    </div>

    <!-- 快速操作卡片 -->
    <div class="quick-actions">
      <div class="section-header">
        <el-icon :size="18" color="#409eff"><Lightning /></el-icon>
        <span>快捷操作</span>
      </div>
      <div class="action-cards">
        <div class="action-card" v-for="action in quickActions" :key="action.label" @click="action.handler">
          <div class="action-icon" :style="{ background: action.bg }">
            <el-icon :size="22" color="#fff"><component :is="action.icon" /></el-icon>
          </div>
          <div class="action-info">
            <div class="action-label">{{ action.label }}</div>
            <div class="action-desc">{{ action.desc }}</div>
          </div>
          <el-icon class="action-arrow" color="#c0c4cc"><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <!-- 概览信息 -->
    <div class="overview-grid">
      <div class="overview-card devices-card">
        <div class="card-header">
          <div class="card-title">
            <el-icon :size="16" color="#409eff"><Monitor /></el-icon>
            <span>设备状态概览</span>
          </div>
          <el-button text size="small" @click="goToDevice">查看全部 <el-icon><ArrowRight /></el-icon></el-button>
        </div>
        <div class="card-body">
          <div class="status-chart">
            <div class="status-bar">
              <div class="bar-segment idle" :style="{ width: devicePercent('idle') + '%' }" title="空闲"></div>
              <div class="bar-segment busy" :style="{ width: devicePercent('busy') + '%' }" title="使用中"></div>
              <div class="bar-segment flashing" :style="{ width: devicePercent('flashing') + '%' }" title="刷机中"></div>
              <div class="bar-segment offline" :style="{ width: devicePercent('offline') + '%' }" title="离线"></div>
              <div class="bar-segment error" :style="{ width: devicePercent('error') + '%' }" title="异常"></div>
            </div>
          </div>
          <div class="status-legend">
            <div v-for="s in statusSummary" :key="s.key" class="legend-item" @click="goToDevice">
              <span class="legend-dot" :style="{ background: s.color }"></span>
              <span class="legend-label">{{ s.label }}</span>
              <span class="legend-value">{{ s.count }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="overview-card tasks-card">
        <div class="card-header">
          <div class="card-title">
            <el-icon :size="16" color="#67c23a"><List /></el-icon>
            <span>任务快速概览</span>
          </div>
          <el-button text size="small" @click="goToTask">查看全部 <el-icon><ArrowRight /></el-icon></el-button>
        </div>
        <div class="card-body">
          <div class="task-summary">
            <div class="ts-row">
              <div class="ts-item">
                <div class="ts-count pending">{{ pendingTasks }}</div>
                <div class="ts-label">排队中</div>
              </div>
              <div class="ts-item">
                <div class="ts-count running">{{ runningTasks }}</div>
                <div class="ts-label">运行中</div>
              </div>
              <div class="ts-item">
                <div class="ts-count success">{{ successTasks }}</div>
                <div class="ts-label">已完成</div>
              </div>
              <div class="ts-item">
                <div class="ts-count failed">{{ failedTasks }}</div>
                <div class="ts-label">失败</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="overview-card branches-card">
        <div class="card-header">
          <div class="card-title">
            <el-icon :size="16" color="#e6a23c"><Share /></el-icon>
            <span>分支概览</span>
          </div>
          <el-button text size="small" @click="goToBranch">查看全部 <el-icon><ArrowRight /></el-icon></el-button>
        </div>
        <div class="card-body">
          <div class="branch-list">
            <div v-for="b in branchSummary" :key="b.name" class="branch-item">
              <div class="branch-left">
                <el-icon :size="14" style="color: #909399"><Share /></el-icon>
                <span class="branch-name">{{ b.name }}</span>
              </div>
              <el-tag :type="!b.disabled ? 'success' : 'info'" size="small" round>
                {{ !b.disabled ? '启用' : '停用' }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import {
  Monitor, Lightning, ArrowRight, List, Share,
  Plus, Document
} from '@element-plus/icons-vue'

const router = useRouter()
const appStore = useAppStore()

const devices = computed(() => appStore.devices)
const tasks = computed(() => appStore.tasks)
const branches = computed(() => appStore.branches.length)

// 设备统计
const totalDevices = computed(() => devices.value.length)
const statusSummary = computed(() => {
  const counts = {
    idle: devices.value.filter(d => d.status === 'idle').length,
    busy: devices.value.filter(d => d.status === 'busy').length,
    flashing: devices.value.filter(d => d.status === 'flashing').length,
    offline: devices.value.filter(d => d.status === 'offline').length,
    error: 0 // 设备类型无 'error' 状态
  }
  return [
    { key: 'idle', label: '空闲', count: counts.idle, color: '#67c23a' },
    { key: 'busy', label: '使用中', count: counts.busy, color: '#409eff' },
    { key: 'flashing', label: '刷机中', count: counts.flashing, color: '#e6a23c' },
    { key: 'offline', label: '离线', count: counts.offline, color: '#c0c4cc' },
    { key: 'error', label: '异常', count: counts.error, color: '#f56c6c' }
  ]
})

const devicePercent = (status: string) => {
  const total = totalDevices.value || 1
  const count = devices.value.filter(d => d.status === status).length
  return (count / total) * 100
}

// 任务统计
const pendingTasks = computed(() => tasks.value.filter(t => t.status === 'queued').length)
const runningTasks = computed(() => tasks.value.filter(t => t.status === 'running').length)
const successTasks = computed(() => tasks.value.filter(t => t.status === 'completed').length)
const failedTasks = computed(() => tasks.value.filter(t => t.status === 'completed' && (t.failCount ?? 0) > 0).length)

// 分支摘要
const branchSummary = computed(() => appStore.branches)

// 快捷操作
const quickActions = [
  { label: '新建任务', desc: '创建新的自动化测试任务', icon: Plus, bg: 'linear-gradient(135deg, #667eea, #764ba2)', handler: () => router.push('/task') },
  { label: '设备管理', desc: '查看和管理测试设备', icon: Monitor, bg: 'linear-gradient(135deg, #4facfe, #00f2fe)', handler: () => router.push('/device') },
  { label: '用例管理', desc: '管理测试用例与脚本', icon: Document, bg: 'linear-gradient(135deg, #11998e, #38ef7d)', handler: () => router.push('/testcase') },
  { label: '分支配置', desc: '管理各分支版本信息', icon: Share, bg: 'linear-gradient(135deg, #f093fb, #f5576c)', handler: () => router.push('/branch') }
]

const goToDevice = () => router.push('/device')
const goToTask = () => router.push('/task')
const goToBranch = () => router.push('/branch')

onMounted(() => {
  appStore.fetchDevices()
  appStore.fetchTasks()
  appStore.fetchBranches()
})
</script>

<style scoped>
:root {
  --primary: #409eff;
}

.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== 欢迎区域 ==================== */
.welcome-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 14px;
  padding: 24px 32px;
  color: #fff;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
  overflow: hidden;
  position: relative;
}

.welcome-section::after {
  content: '';
  position: absolute;
  top: -60%;
  right: -10%;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
  pointer-events: none;
}

.welcome-content {
  display: flex;
  align-items: center;
  gap: 18px;
  position: relative;
  z-index: 1;
}

.welcome-icon {
  width: 72px;
  height: 72px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(255, 255, 255, 0.2);
  flex-shrink: 0;
}

.greeting {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 1px;
}

.subtitle {
  font-size: 13px;
  opacity: 0.85;
  margin-top: 4px;
}

.welcome-stats {
  display: flex;
  align-items: center;
  gap: 20px;
  position: relative;
  z-index: 1;
}

.ws-item {
  text-align: center;
}

.ws-value {
  font-size: 28px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.ws-label {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 2px;
}

.ws-divider {
  width: 1px;
  height: 36px;
  background: rgba(255, 255, 255, 0.3);
}

/* ==================== 快捷操作 ==================== */
.quick-actions {
  background: #fff;
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.action-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 10px;
  background: #f8f9fb;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.action-card:hover {
  background: #fff;
  border-color: #e4e7ed;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}

.action-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.action-info {
  flex: 1;
  min-width: 0;
}

.action-label {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.action-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.action-arrow {
  opacity: 0;
  transition: all 0.3s;
}

.action-card:hover .action-arrow {
  opacity: 1;
  transform: translateX(3px);
}

/* ==================== 概览卡片 ==================== */
.overview-grid {
  display: grid;
  grid-template-columns: 1.8fr 1.2fr 1.2fr;
  gap: 14px;
}

.overview-card {
  background: #fff;
  border-radius: 12px;
  padding: 18px 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  transition: box-shadow 0.3s;
}

.overview-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.card-body {
  min-height: 80px;
}

/* ---- 状态条 ---- */
.status-chart {
  margin-bottom: 12px;
}

.status-bar {
  display: flex;
  height: 10px;
  border-radius: 10px;
  overflow: hidden;
  background: #f0f2f5;
}

.bar-segment {
  transition: width 0.8s ease;
}

.bar-segment.idle { background: #67c23a; }
.bar-segment.busy { background: #409eff; }
.bar-segment.flashing { background: #e6a23c; }
.bar-segment.offline { background: #c0c4cc; }
.bar-segment.error { background: #f56c6c; }

.status-legend {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 4px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.legend-item:hover {
  background: #f0f5ff;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-label {
  font-size: 12px;
  color: #606266;
  flex: 1;
}

.legend-value {
  font-size: 14px;
  font-weight: 700;
  color: #303133;
  font-variant-numeric: tabular-nums;
}

/* ---- 任务概览 ---- */
.task-summary .ts-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.ts-item {
  text-align: center;
  padding: 14px 8px;
  border-radius: 10px;
  background: #f8f9fb;
  transition: transform 0.2s;
}

.ts-item:hover {
  transform: scale(1.05);
}

.ts-count {
  font-size: 22px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.ts-count.pending { color: #e6a23c; }
.ts-count.running { color: #409eff; }
.ts-count.success { color: #67c23a; }
.ts-count.failed { color: #f56c6c; }

.ts-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* ---- 分支概览 ---- */
.branch-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.branch-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  border-radius: 8px;
  transition: background 0.2s;
}

.branch-item:hover {
  background: #f5f7fa;
}

.branch-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.branch-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
}

/* ==================== 响应式 ==================== */
@media (max-width: 1200px) {
  .overview-grid {
    grid-template-columns: 1fr 1fr;
  }
  .action-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 800px) {
  .welcome-section {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  .welcome-stats {
    width: 100%;
    justify-content: center;
  }
  .overview-grid {
    grid-template-columns: 1fr;
  }
  .action-cards {
    grid-template-columns: 1fr;
  }
}
</style>
