<template>
  <div class="device-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>设备列表</span>
          <div class="header-actions">
            <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 120px; margin-right: 10px;">
              <el-option label="空闲" value="idle" />
              <el-option label="忙碌" value="busy" />
              <el-option label="刷机中" value="flashing" />
              <el-option label="离线" value="offline" />
              <el-option label="异常" value="error" />
            </el-select>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索机型/序列号"
              clearable
              style="width: 200px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>
      </template>

      <!-- 设备统计卡片 -->
      <el-row :gutter="16" class="stats-row">
        <el-col :span="4">
          <el-card class="stat-card stat-total">
            <div class="stat-content">
              <div class="stat-value">{{ totalCount }}</div>
              <div class="stat-label">总设备数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card stat-idle">
            <div class="stat-content">
              <div class="stat-value">{{ idleCount }}</div>
              <div class="stat-label">空闲设备</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card stat-busy">
            <div class="stat-content">
              <div class="stat-value">{{ busyCount }}</div>
              <div class="stat-label">使用中设备</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card stat-offline">
            <div class="stat-content">
              <div class="stat-value">{{ offlineCount }}</div>
              <div class="stat-label">离线设备</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card stat-error">
            <div class="stat-content">
              <div class="stat-value">{{ errorCount }}</div>
              <div class="stat-label">异常设备</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 设备表格展示 -->
      <el-table :data="filteredDevices" style="width: 100%" v-loading="false" @row-click="showDetail">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="executorIp" label="执行机" width="140" />
        <el-table-column prop="serial" label="序列号" min-width="160" />
        <el-table-column prop="romVersion" label="ROM版本" min-width="140" />
        <el-table-column prop="browserVersion" label="浏览器版本" min-width="180" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="最后上报时间" width="140">
          <template #default="{ row }">
            {{ formatTime(row.lastReportTime) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="editDevice(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="filteredDevices.length === 0" description="暂无设备数据" style="margin-top: 60px;" />
    </el-card>

    <!-- 设备详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      title="设备详情"
      width="600px"
    >
      <el-descriptions v-if="selectedDevice" :column="2" border>
        <el-descriptions-item label="序列号" :span="2">{{ selectedDevice.serial }}</el-descriptions-item>
        <el-descriptions-item label="执行机IP">{{ selectedDevice.executorIp }}</el-descriptions-item>
        <el-descriptions-item label="ROM版本">{{ selectedDevice.romVersion }}</el-descriptions-item>
        <el-descriptions-item label="浏览器版本" :span="2">{{ selectedDevice.browserVersion }}</el-descriptions-item>
        <el-descriptions-item label="设备状态">
          <el-tag :type="getStatusType(selectedDevice.status)">
            {{ getStatusText(selectedDevice.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="最后上报时间" :span="2">
          {{ formatTime(selectedDevice.lastReportTime) }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ selectedDevice.remark || '-' }}</el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="rebootDevice">重启设备</el-button>
      </template>
    </el-dialog>

    <!-- 编辑设备弹窗 -->
    <el-dialog
      v-model="editVisible"
      title="编辑设备"
      width="500px"
    >
      <el-form label-width="80px">
        <el-form-item label="设备序列号">
          <el-input v-model="editingDeviceSerial" disabled />
        </el-form-item>
        <el-form-item label="设备状态">
          <el-select v-model="editingStatus" style="width: 100%;">
            <el-option label="空闲" value="idle" />
            <el-option label="忙碌" value="busy" />
            <el-option label="刷机中" value="flashing" />
            <el-option label="离线" value="offline" />
            <el-option label="异常" value="error" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
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

      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import type { Device } from '@/types'

const appStore = useAppStore()

const statusFilter = ref('')
const searchKeyword = ref('')
const detailVisible = ref(false)
const selectedDevice = ref<Device | null>(null)
const editVisible = ref(false)
const editingDeviceId = ref<number | null>(null)
const editingDeviceSerial = ref('')
const editingStatus = ref('')
const editingRemark = ref('')

const devices = computed(() => appStore.devices)

const filteredDevices = computed(() => {
  let result = devices.value
  
  if (statusFilter.value) {
    result = result.filter(d => d.status === statusFilter.value)
  }
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(d => 
      d.serial.toLowerCase().includes(keyword) ||
      d.executorIp.toLowerCase().includes(keyword)
    )
  }
  
  return result
})

// 设备统计
const totalCount = computed(() => devices.value.length)
const idleCount = computed(() => devices.value.filter(d => d.status === 'idle').length)
const busyCount = computed(() => devices.value.filter(d => d.status === 'busy').length)
const offlineCount = computed(() => devices.value.filter(d => d.status === 'offline').length)
const errorCount = computed(() => devices.value.filter(d => d.status === 'error').length)

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    idle: 'success',
    busy: 'primary',
    flashing: 'info',
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

const formatTime = (time: string) => {
  if (!time) return '-'
  const now = new Date()
  const reportTime = new Date(time)
  const diff = now.getTime() - reportTime.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return reportTime.toLocaleDateString('zh-CN')
}

const showDetail = (device: Device) => {
  selectedDevice.value = device
  detailVisible.value = true
}

const rebootDevice = () => {
  ElMessage.success('重启指令已下发')
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
    appStore.initMockData()
  }
})
</script>

<style scoped>
.device-page {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.stats-row {
  margin-bottom: 20px;
  display: flex;
  gap: 16px;
}

.stat-card {
  flex: 1;
  border: none;
  color: #fff;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-3px);
}

.stat-card.stat-total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card.stat-idle {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.stat-card.stat-busy {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card.stat-offline {
  background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
}

.stat-card.stat-error {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-content {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

:deep(.el-table__body tr) {
  cursor: pointer;
}
</style>
