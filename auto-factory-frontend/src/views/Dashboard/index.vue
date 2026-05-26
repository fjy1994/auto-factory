<template>
  <div class="dashboard">
    <!-- 概览卡片行 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon total">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ devices.length }}</div>
              <div class="stat-label">总设备数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon idle">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ idleCount }}</div>
              <div class="stat-label">空闲设备</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon running">
              <el-icon><Loading /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ runningCount }}</div>
              <div class="stat-label">执行中任务</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon today">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ todayTaskCount }}</div>
              <div class="stat-label">今日任务</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 状态卡片和图表行 -->
    <el-row :gutter="20" class="middle-row">
      <el-col :span="8">
        <el-card class="mail-status-card">
          <template #header>
            <div class="card-header">
              <span>📧 邮件服务状态</span>
            </div>
          </template>
          
          <div class="status-list">
            <div class="status-item">
              <span class="label">连接状态:</span>
              <el-tag :type="mailStatus.connected ? 'success' : 'danger'">
                {{ mailStatus.connected ? '已连接' : '未连接' }}
              </el-tag>
            </div>
            <div class="status-item">
              <span class="label">监听状态:</span>
              <el-tag :type="mailStatus.running ? 'success' : 'warning'">
                {{ mailStatus.running ? '监听中' : '已停止' }}
              </el-tag>
            </div>
            <div class="status-item">
              <span class="label">邮箱地址:</span>
              <span class="value">{{ mailStatus.email || '-' }}</span>
            </div>
            <div class="status-item">
              <span class="label">轮询间隔:</span>
              <span class="value">{{ mailStatus.pollInterval }}秒</span>
            </div>
          </div>

          <div class="action-buttons">
            <el-button size="small" @click="fetchMailStatus">
              <el-icon><Refresh /></el-icon>
              刷新状态
            </el-button>
            <el-button size="small" @click="toggleMailService">
              {{ mailStatus.running ? '停止监听' : '启动监听' }}
            </el-button>
            <el-button size="small" @click="openMailSettings">
              <el-icon><Setting /></el-icon>
              设置
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>任务状态分布</span>
            </div>
          </template>
          <div ref="chartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近任务列表 -->
    <el-card class="recent-tasks-card">
      <template #header>
        <div class="card-header">
          <span>最近任务</span>
          <el-button type="primary" link @click="$router.push('/task')">查看全部</el-button>
        </div>
      </template>
      
      <el-table :data="recentTasks" style="width: 100%">
        <el-table-column prop="name" label="任务名称" width="150" />
        <el-table-column prop="version" label="版本号" width="120" />
        <el-table-column prop="model" label="机型" width="100" />
        <el-table-column prop="taskType" label="任务类型" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :stroke-width="8" />
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.createdAt) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'
import { Monitor, CircleCheck, Loading, Calendar, Refresh, Setting } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()
const appStore = useAppStore()
const chartRef = ref<HTMLElement>()

const devices = computed(() => appStore.devices)
const tasks = computed(() => appStore.tasks)
const mailStatus = computed(() => appStore.mailStatus)

const idleCount = computed(() => devices.value.filter(d => d.status === 'idle').length)
const runningCount = computed(() => tasks.value.filter(t => t.status === 'running').length)
const todayTaskCount = computed(() => tasks.value.filter(t => {
  const today = new Date().toDateString()
  return new Date(t.createdAt).toDateString() === today
}).length)

const recentTasks = computed(() => tasks.value.slice(0, 10))

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

const fetchMailStatus = () => {
  ElMessage.success('状态已刷新')
}

const toggleMailService = () => {
  appStore.mailStatus.running = !appStore.mailStatus.running
  ElMessage.success(appStore.mailStatus.running ? '已启动邮件监听' : '已停止邮件监听')
}

const openMailSettings = () => {
  router.push('/settings/mail')
}

const initChart = () => {
  if (!chartRef.value) return
  
  const chart = echarts.init(chartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      bottom: '0%',
      left: 'center'
    },
    series: [
      {
        name: '任务状态',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: 1, name: '排队中', itemStyle: { color: '#909399' } },
          { value: 1, name: '执行中', itemStyle: { color: '#409eff' } },
          { value: 1, name: '成功', itemStyle: { color: '#67c23a' } },
          { value: 0, name: '失败', itemStyle: { color: '#f56c6c' } },
          { value: 0, name: '异常', itemStyle: { color: '#e6a23c' } }
        ]
      }
    ]
  }
  
  chart.setOption(option)
}

onMounted(() => {
  appStore.initMockData()
  setTimeout(initChart, 100)
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stat-cards {
  margin-bottom: 0;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.idle {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.stat-icon.running {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.today {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.middle-row {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-item .label {
  color: #606266;
}

.status-item .value {
  color: #303133;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chart-container {
  height: 300px;
}

.recent-tasks-card {
  flex: 1;
}
</style>
