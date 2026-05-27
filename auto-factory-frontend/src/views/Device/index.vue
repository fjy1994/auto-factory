<template>
  <div class="device-page">
    <!-- 统计卡片行 -->
    <div class="stats-row">
      <div
        v-for="stat in statCards"
        :key="stat.key"
        class="stat-card"
        :style="{ '--gradient': stat.gradient }"
        @click="statusFilter = stat.key === 'total' ? '' : stat.key"
      >
        <div class="stat-icon-wrapper" :style="{ background: stat.iconBg }">
          <el-icon :size="24"><component :is="stat.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
        <div class="stat-trend" v-if="stat.trend">
          <span :class="stat.trend > 0 ? 'up' : 'down'">
            {{ stat.trend > 0 ? '↑' : '↓' }} {{ Math.abs(stat.trend) }}%
          </span>
        </div>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-icon :size="20" color="#409eff"><Monitor /></el-icon>
        <span class="toolbar-title">设备列表</span>
        <el-tag size="small" type="info" round>{{ filteredDevices.length }} / {{ totalCount }}</el-tag>
      </div>
      <div class="toolbar-right">
        <div class="last-update" v-if="lastUpdateTime">
          <el-icon><Clock /></el-icon>
          <span>上次更新: {{ lastUpdateTime }}</span>
        </div>
        <el-select
          v-model="statusFilter"
          placeholder="状态筛选"
          clearable
          size="small"
          style="width: 130px"
          @change="handleFilterChange"
        >
          <el-option label="全部状态" value="" />
          <el-option label="空闲" value="idle" />
          <el-option label="忙碌" value="busy" />
          <el-option label="刷机中" value="flashing" />
          <el-option label="离线" value="offline" />
          <el-option label="异常" value="error" />
        </el-select>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索机型 / 序列号 / IP"
          clearable
          size="small"
          style="width: 220px"
          :prefix-icon="Search"
        />
        <el-button size="small" :icon="Refresh" circle @click="refreshData" />
      </div>
    </div>

    <!-- 设备列表 -->
    <div class="device-list-container">
      <el-table
        :data="pagedDevices"
        style="width: 100%"
        :show-header="true"
        @row-click="showDetail"
        class="device-table"
      >
        <el-table-column label="设备" min-width="200">
          <template #default="{ row }">
            <div class="device-cell">
              <div class="device-indicator" :class="row.status">
                <span class="pulse-ring"></span>
              </div>
              <div class="device-info">
                <div class="device-name">
                  <span class="name-text">{{ row.deviceName || row.serial }}</span>
                  <el-tag
                    :type="getStatusType(row.status)"
                    size="small"
                    class="status-tag"
                  >
                    <span class="status-dot" :class="row.status"></span>
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </div>
                <div class="device-meta">
                  <span class="meta-item">{{ row.model || '-' }}</span>
                  <span class="meta-divider">·</span>
                  <span class="meta-item">{{ row.serial }}</span>
                  <span class="meta-divider">·</span>
                  <span class="meta-item">{{ row.executorIp }}</span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="ROM 版本" min-width="140">
          <template #default="{ row }">
            <div class="rom-cell">
              <el-icon :size="14" color="#909399"><Cpu /></el-icon>
              <span class="rom-text">{{ row.romVersion }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="浏览器" min-width="150">
          <template #default="{ row }">
            <div class="browser-cell">
              <el-icon :size="14" color="#409eff"><Connection /></el-icon>
              <span>{{ row.browserVersion }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="最后上报" width="120" align="center">
          <template #default="{ row }">
            <div class="time-cell" :class="getTimeFreshness(row.lastReportTime)">
              {{ formatRelativeTime(row.lastReportTime) }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="remark-text">{{ row.remark || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right" align="center">
          <template #default="{ row }">
            <el-tooltip content="编辑设备" placement="top">
              <el-button
                link
                type="primary"
                size="small"
                :icon="Edit"
                @click.stop="editDevice(row)"
              />
            </el-tooltip>
            <el-tooltip content="重启设备" placement="top">
              <el-button
                link
                type="warning"
                size="small"
                :icon="RefreshRight"
                @click.stop="handleReboot(row)"
              />
            </el-tooltip>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty :image-size="100" description="暂无设备数据">
            <template #image>
              <div class="empty-device-icon">
                <el-icon :size="60" color="#c0c4cc"><Monitor /></el-icon>
              </div>
            </template>
          </el-empty>
        </template>
      </el-table>

      <!-- 分页 -->
      <div v-if="filteredDevices.length > 10" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredDevices.length"
          :pager-count="5"
          layout="prev, pager, next"
          size="small"
          background
        />
      </div>
    </div>

    <!-- 设备详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      :title="selectedDevice?.deviceName || selectedDevice?.serial || '设备详情'"
      width="640px"
      class="detail-dialog"
      destroy-on-close
    >
      <div v-if="selectedDevice" class="detail-body">
        <!-- 设备状态横幅 -->
        <div class="detail-banner" :class="selectedDevice.status">
          <div class="banner-left">
            <div class="banner-icon">
              <el-icon :size="40"><Monitor /></el-icon>
            </div>
            <div class="banner-status">
              <div class="banner-device-name">{{ selectedDevice.deviceName }}</div>
              <div class="banner-status-tag">
                <el-tag :type="getStatusType(selectedDevice.status)" size="small" effect="dark">
                  <span class="status-dot" :class="selectedDevice.status"></span>
                  {{ getStatusText(selectedDevice.status) }}
                </el-tag>
              </div>
            </div>
          </div>
          <div class="banner-right">
            <div class="banner-meta">
              <div class="banner-meta-item">
                <span class="meta-label">序列号</span>
                <span class="meta-value">{{ selectedDevice.serial }}</span>
              </div>
              <div class="banner-meta-item">
                <span class="meta-label">最后上报</span>
                <span class="meta-value">{{ formatRelativeTime(selectedDevice.lastReportTime) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 设备详情网格 -->
        <div class="detail-grid">
          <div class="detail-item">
            <div class="detail-item-label">执行机 IP</div>
            <div class="detail-item-value">
              <el-icon :size="14" color="#409eff"><Monitor /></el-icon>
              {{ selectedDevice.executorIp }}
            </div>
          </div>
          <div class="detail-item">
            <div class="detail-item-label">ROM 版本</div>
            <div class="detail-item-value">
              <el-icon :size="14" color="#909399"><Cpu /></el-icon>
              {{ selectedDevice.romVersion }}
            </div>
          </div>
          <div class="detail-item">
            <div class="detail-item-label">浏览器版本</div>
            <div class="detail-item-value">
              <el-icon :size="14" color="#409eff"><Connection /></el-icon>
              {{ selectedDevice.browserVersion }}
            </div>
          </div>
          <div class="detail-item">
            <div class="detail-item-label">机型代号</div>
            <div class="detail-item-value">{{ selectedDevice.model || '-' }}</div>
          </div>
          <div class="detail-item full-width">
            <div class="detail-item-label">备注</div>
            <div class="detail-item-value">{{ selectedDevice.remark || '无备注信息' }}</div>
          </div>
          <div class="detail-item full-width">
            <div class="detail-item-label">上次上报时间</div>
            <div class="detail-item-value detail-time">
              <el-icon :size="14" color="#909399"><Clock /></el-icon>
              {{ formatFullTime(selectedDevice.lastReportTime) }}
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailVisible = false">关闭</el-button>
          <el-button type="warning" :icon="RefreshRight" @click="handleReboot(selectedDevice!)">
            重启设备
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 编辑设备弹窗 -->
    <el-dialog
      v-model="editVisible"
      title="编辑设备"
      width="480px"
      class="edit-dialog"
      destroy-on-close
    >
      <div class="edit-body">
        <div class="edit-device-info">
          <el-icon :size="18" color="#409eff"><Monitor /></el-icon>
          <span class="edit-serial">{{ editingDeviceSerial }}</span>
          <el-tag
            :type="getStatusType(editingStatus)"
            size="small"
            effect="plain"
          >{{ getStatusText(editingStatus) }}</el-tag>
        </div>
        <el-form label-width="80px" class="edit-form">
          <el-form-item label="设备状态">
            <el-select v-model="editingStatus" style="width: 100%">
              <el-option label="空闲" value="idle" />
              <el-option label="忙碌" value="busy" />
              <el-option label="刷机中" value="flashing" />
              <el-option label="离线" value="offline" />
              <el-option label="异常" value="error" />
            </el-select>
          </el-form-item>
          <el-form-item label="备注信息">
            <el-input
              v-model="editingRemark"
              type="textarea"
              :rows="4"
              placeholder="请输入备注信息"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'
import {
  Search, Refresh, Monitor, Cpu, Connection, Clock,
  Edit, RefreshRight, CircleCheck, Warning,
  VideoPause, DataLine
} from '@element-plus/icons-vue'
import type { Device } from '@/types'

const appStore = useAppStore()

const statusFilter = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = 20
const detailVisible = ref(false)
const selectedDevice = ref<Device | null>(null)
const editVisible = ref(false)
const editingDeviceId = ref<number | null>(null)
const editingDeviceSerial = ref('')
const editingStatus = ref('')
const editingRemark = ref('')
const lastUpdateTime = ref('')

const devices = computed(() => appStore.devices)

const filteredDevices = computed(() => {
  let result = devices.value
  if (statusFilter.value) {
    result = result.filter(d => d.status === statusFilter.value)
  }
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(d =>
      (d.deviceName || '').toLowerCase().includes(kw) ||
      d.serial.toLowerCase().includes(kw) ||
      d.executorIp.toLowerCase().includes(kw) ||
      (d.model || '').toLowerCase().includes(kw)
    )
  }
  return result
})

const pagedDevices = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredDevices.value.slice(start, start + pageSize)
})

watch([statusFilter, searchKeyword], () => { currentPage.value = 1 })

// 统计卡片数据
const totalCount = computed(() => devices.value.length)
const idleCount = computed(() => devices.value.filter(d => d.status === 'idle').length)
const busyCount = computed(() => devices.value.filter(d => d.status === 'busy').length)
const flashingCount = computed(() => devices.value.filter(d => d.status === 'flashing').length)
const offlineCount = computed(() => devices.value.filter(d => d.status === 'offline').length)
const errorCount = computed(() => devices.value.filter(d => d.status === 'error').length)

const statCards = computed(() => [
  {
    key: 'total',
    label: '总设备数',
    value: totalCount.value,
    icon: DataLine,
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    iconBg: 'rgba(255,255,255,0.2)',
    trend: null
  },
  {
    key: 'idle',
    label: '空闲',
    value: idleCount.value,
    icon: CircleCheck,
    gradient: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    iconBg: 'rgba(255,255,255,0.2)',
    trend: idleCount.value > 0 ? Math.round((idleCount.value / (totalCount.value || 1)) * 100) : 0
  },
  {
    key: 'busy',
    label: '使用中',
    value: busyCount.value,
    icon: Monitor,
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    iconBg: 'rgba(255,255,255,0.2)',
    trend: busyCount.value > 0 ? Math.round((busyCount.value / (totalCount.value || 1)) * 100) : null
  },
  {
    key: 'flashing',
    label: '刷机中',
    value: flashingCount.value,
    icon: RefreshRight,
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    iconBg: 'rgba(255,255,255,0.2)',
    trend: null
  },
  {
    key: 'offline',
    label: '离线',
    value: offlineCount.value,
    icon: VideoPause,
    gradient: 'linear-gradient(135deg, #bdc3c7 0%, #2c3e50 100%)',
    iconBg: 'rgba(255,255,255,0.2)',
    trend: null
  },
  {
    key: 'error',
    label: '异常',
    value: errorCount.value,
    icon: Warning,
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    iconBg: 'rgba(255,255,255,0.2)',
    trend: null
  }
])

// 状态映射
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    idle: 'success',
    busy: 'primary',
    flashing: 'warning',
    offline: 'info',
    error: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    idle: '空闲',
    busy: '忙碌',
    flashing: '刷机中',
    offline: '离线',
    error: '异常'
  }
  return map[status] || status
}

// 时间格式化
const formatRelativeTime = (time: string) => {
  if (!time) return '-'
  const now = Date.now()
  const t = new Date(time).getTime()
  const diff = now - t

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  return new Date(time).toLocaleDateString('zh-CN')
}

const formatFullTime = (time: string) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const getTimeFreshness = (time: string) => {
  if (!time) return 'old'
  const diff = Date.now() - new Date(time).getTime()
  if (diff < 300000) return 'fresh'      // < 5min
  if (diff < 3600000) return 'normal'    // < 1h
  return 'stale'                          // > 1h
}

// 操作
const handleFilterChange = () => {
  // no additional logic needed
}

const refreshData = () => {
  const now = new Date()
  lastUpdateTime.value = now.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
  ElMessage.success('数据已刷新')
}

const showDetail = (device: Device) => {
  selectedDevice.value = device
  detailVisible.value = true
}

const handleReboot = (device: Device) => {
  ElMessage.success(`重启指令已下发至 ${device.deviceName || device.serial}`)
  detailVisible.value = false
}

const editDevice = (device: Device) => {
  editingDeviceId.value = device.id
  editingDeviceSerial.value = device.serial
  editingStatus.value = device.status
  editingRemark.value = device.remark || ''
  editVisible.value = true
}

const saveEdit = () => {
  if (editingDeviceId.value !== null) {
    const device = appStore.devices.find(d => d.id === editingDeviceId.value)
    if (device) {
      device.status = editingStatus.value as Device['status']
      device.remark = editingRemark.value
      ElMessage.success('设备信息已更新')
    }
    editVisible.value = false
  }
}

onMounted(() => {
  if (!appStore.devices.length) {
    appStore.fetchAll()
  }
  refreshData()
})
</script>

<style scoped>
/* ==================== 布局 ==================== */
.device-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== 统计卡片 ==================== */
.stats-row {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
}

.stat-card {
  background: var(--gradient);
  border-radius: 12px;
  padding: 16px 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.stat-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  transition: all 0.5s;
  pointer-events: none;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
}

.stat-card:hover::before {
  top: -30%;
  right: -30%;
  width: 120%;
  height: 120%;
}

.stat-icon-wrapper {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  backdrop-filter: blur(4px);
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #fff;
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 2px;
  letter-spacing: 0.5px;
}

.stat-trend {
  position: absolute;
  top: 10px;
  right: 12px;
}

.stat-trend span {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

/* ==================== 工具栏 ==================== */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-radius: 10px;
  padding: 10px 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.last-update {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

/* ==================== 设备表格 ==================== */
.device-list-container {
  flex: 1;
  overflow: hidden;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

:deep(.device-table) {
  border-radius: 10px;
  overflow: hidden;
}

:deep(.device-table .el-table__header-wrapper) {
  background: #f5f7fa;
}

:deep(.device-table .el-table__header th) {
  background: #f5f7fa;
  color: #606266;
  font-weight: 600;
  font-size: 13px;
  padding: 10px 0;
}

:deep(.device-table .el-table__row) {
  transition: background-color 0.2s;
  cursor: pointer;
}

:deep(.device-table .el-table__row:hover) {
  background-color: #f0f7ff !important;
}

:deep(.device-table .el-table__cell) {
  padding: 8px 0;
}

/* -- 设备名称列 -- */
.device-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.device-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  position: relative;
  flex-shrink: 0;
}

.device-indicator.idle { background: #67c23a; }
.device-indicator.busy { background: #409eff; }
.device-indicator.flashing { background: #e6a23c; }
.device-indicator.offline { background: #c0c4cc; }
.device-indicator.error { background: #f56c6c; }

.pulse-ring {
  display: none;
}

.device-indicator.busy .pulse-ring,
.device-indicator.flashing .pulse-ring {
  display: block;
  position: absolute;
  top: -3px;
  left: -3px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid currentColor;
  animation: pulse 2s ease-out infinite;
  opacity: 0;
}

.device-indicator.busy .pulse-ring { border-color: #409eff; }
.device-indicator.flashing .pulse-ring { border-color: #e6a23c; }

@keyframes pulse {
  0% { transform: scale(0.5); opacity: 1; }
  100% { transform: scale(1.8); opacity: 0; }
}

.device-info {
  min-width: 0;
  flex: 1;
}

.device-name {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}

.name-text {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.status-tag {
  flex-shrink: 0;
}

.status-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 4px;
  vertical-align: middle;
}

.status-dot.idle { background: #67c23a; }
.status-dot.busy { background: #409eff; }
.status-dot.flashing { background: #e6a23c; }
.status-dot.offline { background: #c0c4cc; }
.status-dot.error { background: #f56c6c; }

.device-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.meta-item {
  font-size: 12px;
  color: #909399;
}

.meta-divider {
  font-size: 10px;
  color: #dcdfe6;
}

/* -- ROM 列 -- */
.rom-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.rom-text {
  font-size: 13px;
  color: #606266;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  letter-spacing: 0.2px;
}

/* -- 浏览器列 -- */
.browser-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
}

/* -- 时间列 -- */
.time-cell {
  font-size: 12px;
  font-weight: 500;
  transition: color 0.3s;
}

.time-cell.fresh { color: #67c23a; }
.time-cell.normal { color: #909399; }
.time-cell.stale { color: #f56c6c; }

/* -- 备注列 -- */
.remark-text {
  font-size: 13px;
  color: #909399;
}

/* ==================== 分页 ==================== */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 12px 0 4px;
}

/* ==================== 空状态 ==================== */
.empty-device-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #f0f2f5;
  margin: 0 auto;
}

/* ==================== 详情弹窗 ==================== */
:deep(.detail-dialog .el-dialog__header) {
  padding: 16px 20px;
  margin: 0;
  border-bottom: 1px solid #ebeef5;
}

:deep(.detail-dialog .el-dialog__title) {
  font-size: 16px;
  font-weight: 600;
}

:deep(.detail-dialog .el-dialog__body) {
  padding: 20px;
  padding-top: 0;
}

.detail-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* -- 状态横幅 -- */
.detail-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-radius: 10px;
  margin-top: 16px;
  color: #fff;
}

.detail-banner.idle { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
.detail-banner.busy { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.detail-banner.flashing { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.detail-banner.offline { background: linear-gradient(135deg, #bdc3c7 0%, #2c3e50 100%); }
.detail-banner.error { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }

.banner-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.banner-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.banner-device-name {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 4px;
}

.banner-right {
  text-align: right;
}

.banner-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.banner-meta-item {
  font-size: 12px;
  opacity: 0.9;
}

.meta-label {
  margin-right: 4px;
  opacity: 0.75;
}

.meta-value {
  font-weight: 500;
}

/* -- 详情网格 -- */
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.detail-item {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px 14px;
  transition: background 0.2s;
}

.detail-item:hover {
  background: #eef1f6;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-item-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}

.detail-item-value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-time {
  font-size: 13px;
  color: #606266;
  font-weight: 400;
}

/* ==================== 编辑弹窗 ==================== */
:deep(.edit-dialog .el-dialog__header) {
  padding: 16px 20px;
  margin: 0;
  border-bottom: 1px solid #ebeef5;
}

:deep(.edit-dialog .el-dialog__body) {
  padding: 20px;
}

.edit-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.edit-device-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 14px;
  color: #303133;
}

.edit-serial {
  flex: 1;
  font-weight: 600;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
}

/* ==================== 弹窗底部 ==================== */
.dialog-footer {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* ==================== 响应式 ==================== */
@media (max-width: 1400px) {
  .stats-row {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 800px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .toolbar {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  .toolbar-right {
    flex-wrap: wrap;
  }
}
</style>
