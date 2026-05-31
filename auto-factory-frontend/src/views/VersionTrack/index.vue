<template>
  <div class="coverage-page">
    <!-- 头部：覆盖统计概览 -->
    <div class="page-header">
      <div class="header-left">
        <el-icon :size="22" color="#e6a23c"><Collection /></el-icon>
        <span class="header-title">版本跟踪 · 覆盖看板</span>
        <el-tag size="small" type="warning" effect="plain" round>
          {{ totalCount }} 个版本
        </el-tag>
      </div>
      <div class="header-right">
        <el-select v-model="coverageFilter" placeholder="覆盖状态" clearable size="small" style="width: 140px">
          <el-option label="全部版本" value="" />
          <el-option label="✅ 已覆盖" value="covered" />
          <el-option label="⏳ 覆盖中" value="covering" />
          <el-option label="❌ 未覆盖" value="uncovered" />
        </el-select>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索版本号/分支..."
          clearable
          size="small"
          style="width: 180px"
        />
        <el-button size="small" :icon="Search" @click="handleSearch">查询</el-button>
      </div>
    </div>

    <!-- 三格统计卡片 -->
    <div class="stats-row">
      <div class="stat-card covered" @click="setCoverageFilter('covered')">
        <div class="stat-card-icon">
          <el-icon :size="26"><CircleCheckFilled /></el-icon>
        </div>
        <div class="stat-card-body">
          <div class="stat-number">{{ coveredCount }}</div>
          <div class="stat-label">已覆盖测试</div>
        </div>
        <div class="stat-detail">
          {{ coveredPassCount }} 通过 · {{ coveredFailCount }} 未通过
        </div>
      </div>

      <div class="stat-card covering" @click="setCoverageFilter('covering')">
        <div class="stat-card-icon">
          <el-icon :size="26"><Refresh /></el-icon>
        </div>
        <div class="stat-card-body">
          <div class="stat-number">{{ coveringCount }}</div>
          <div class="stat-label">覆盖中</div>
        </div>
        <div class="stat-detail">
          {{ flashingCount }} 刷机 · {{ taskingCount }} 执行任务
        </div>
      </div>

      <div class="stat-card uncovered" @click="setCoverageFilter('uncovered')">
        <div class="stat-card-icon">
          <el-icon :size="26"><WarnTriangleFilled /></el-icon>
        </div>
        <div class="stat-card-body">
          <div class="stat-number">{{ uncoveredCount }}</div>
          <div class="stat-label">未覆盖</div>
        </div>
        <div class="stat-detail">
          {{ noMatchCount }} 未匹配 · {{ noDeviceCount }} 无设备 · {{ failedCount }} 刷机失败
        </div>
      </div>
    </div>

    <!-- 版本列表（按时间倒序） -->
    <div class="record-list">
      <TransitionGroup name="record-list">
        <div v-for="rec in pagedRecords" :key="rec.id" class="record-card" :class="rec.coverageClass">
          <!-- 覆盖状态色条 -->
          <div class="status-bar" :class="rec.coverageClass" />

          <div class="card-body">
            <!-- 左侧主信息 -->
            <div class="card-main">
              <div class="version-row">
                <span class="version-tag" :class="rec.coverageClass">{{ rec.version }}</span>
                <el-tag
                  :type="rec.coverageTagType"
                  size="small"
                  effect="dark"
                  round
                >{{ rec.coverageLabel }}</el-tag>
                <el-tag :type="branchTagType(rec.branchType)" size="small" effect="light" round>{{ rec.branchType }}</el-tag>
                <span class="rec-time">{{ formatTime(appStore.versions.find(v => v.id === rec.id)?.createdAt || '') }}</span>
              </div>
              <div class="meta-row">
                <span class="meta-chip">
                  <el-icon :size="11"><Folder /></el-icon>
                  {{ rec.branchName }}
                </span>
                <span class="meta-chip">
                  <el-icon :size="11"><Collection /></el-icon>
                  {{ VERSION_STATUS_TEXT[rec.status] || '未知' }}
                </span>
                <span
                  v-if="rec.flashingTaskIds && rec.flashingTaskIds.length > 0"
                  class="meta-chip flashing-link"
                  :class="{ 'flash-failed-link': rec.status === 3 }"
                  @click="$router.push('/flash?version=' + rec.version)"
                >
                  <el-icon :size="11"><Opportunity /></el-icon>
                  刷机管理
                </span>
              </div>
            </div>

            <!-- 右侧覆盖率/结果概览 -->
            <div class="card-result">
              <!-- 已覆盖：显示通过/失败统计 -->
              <template v-if="rec.coverageStatus === 'covered'">
                <div class="result-pass">
                  <div class="result-big-num">{{ rec.passCount }}</div>
                  <div class="result-big-label">通过</div>
                </div>
                <div v-if="rec.failCount" class="result-fail">
                  <div class="result-big-num">{{ rec.failCount }}</div>
                  <div class="result-big-label">失败</div>
                </div>
                <div class="result-rate" :class="{ warn: rec.passRate !== undefined && rec.passRate < 90 }">
                  {{ rec.passRate }}%
                </div>
              </template>

              <!-- 覆盖中 -->
              <template v-else-if="rec.coverageStatus === 'covering'">
                <div class="coverage-badge processing">
                  <el-icon :size="14" class="rotating"><Refresh /></el-icon>
                  {{ rec.coverageLabel }}
                </div>
              </template>

              <!-- 未覆盖 -->
              <template v-else>
                <div class="coverage-badge blocked">
                  <el-icon :size="14"><WarnTriangleFilled /></el-icon>
                  {{ rec.coverageLabel }}
                </div>
              </template>
            </div>
          </div>

          <!-- 展开区域：详细任务结果 | 原因说明 -->
          <div class="detail-area">
            <!-- 已覆盖/覆盖中：展开任务明细 -->
            <template v-if="rec.tasks && rec.tasks.length">
              <div class="detail-header" @click="toggleDetail(rec.id)">
                <el-icon :size="13" color="#909399"><List /></el-icon>
                <span>{{ rec.tasks.length }} 项任务</span>
                <el-icon class="detail-arrow" :class="{ expanded: expandedDetails.has(rec.id) }"><ArrowDown /></el-icon>
              </div>
              <Transition name="expand">
                <div v-if="expandedDetails.has(rec.id)" class="task-detail-list">
                  <div v-for="tr in rec.tasks" :key="tr.id" class="task-detail-row" :class="tr.status" @click.stop="$router.push('/task?focus=' + tr.id)">
                    <div class="td-left">
                      <el-icon :size="12">
                        <CircleCheck v-if="tr.status === 'completed' && !tr.failCount" />
                        <CircleClose v-else-if="tr.status === 'completed' && tr.failCount" />
                        <Refresh v-else-if="tr.status === 'running'" />
                        <Clock v-else />
                      </el-icon>
                      <span class="td-name">{{ tr.name }}</span>
                    </div>
                    <div class="td-stats">
                      <span v-if="tr.passRate !== undefined" class="td-rate" :class="{ warn: tr.passRate !== undefined && tr.passRate < 90 }">
                        {{ tr.passRate }}%
                      </span>
                      <span class="td-count" :title="'通过 ' + (tr.passCount ?? 0) + ' / 失败 ' + (tr.failCount ?? 0) + ' / 总 ' + (tr.totalCount ?? 0)">
                        {{ tr.passCount ?? 0 }}/{{ tr.failCount ?? 0 }}/{{ tr.totalCount ?? 0 }}
                      </span>
                    </div>
                    <div class="td-bar-bg">
                      <div
                        class="td-bar-fill"
                        :style="{ width: (tr.passRate ?? 0) + '%' }"
                        :class="{ warn: (tr.passRate ?? 100) < 90, danger: (tr.passRate ?? 100) < 70 }"
                      />
                    </div>
                  </div>
                </div>
              </Transition>
            </template>

            <!-- 刷机失败：显示失败原因 -->
            <div v-else-if="rec.status === 3" class="detail-reason">
              <el-icon :size="13" color="#f56c6c"><WarnTriangleFilled /></el-icon>
              <span>{{ VERSION_STATUS_TEXT[3] }}</span>
            </div>

            <!-- 无设备 -->
            <div v-else-if="rec.status === 0" class="detail-reason">
              <el-icon :size="13" color="#909399"><Clock /></el-icon>
              <span>{{ VERSION_STATUS_TEXT[0] }}</span>
              <el-button size="small" type="primary" plain :loading="versionDispatchLoading === rec.id" @click.stop="dispatchFlash(rec)">
                重新下发
              </el-button>
            </div>

            <!-- 等待中 -->
            <div v-else-if="rec.status === 1 && (!rec.tasks || rec.tasks.length === 0)" class="detail-reason pending">
              <el-icon :size="13" color="#e6a23c"><Clock /></el-icon>
              <span>等待刷机后执行任务...</span>
              <el-button size="small" type="primary" plain :loading="versionDispatchLoading === rec.id" @click.stop="dispatchFlash(rec)">
                下发刷机
              </el-button>
            </div>

            <!-- 已完成无任务 -->
            <div v-else-if="rec.status === 5 && (!rec.tasks || rec.tasks.length === 0)" class="detail-reason">
              <el-icon :size="13" color="#909399"><InfoFilled /></el-icon>
              <span>该版本已完成测试</span>
            </div>

            <!-- 已废弃 -->
            <div v-else-if="rec.status === 6" class="detail-reason">
              <el-icon :size="13" color="#909399"><InfoFilled /></el-icon>
              <span>{{ VERSION_STATUS_TEXT[6] }}</span>
            </div>
          </div>
        </div>
      </TransitionGroup>

      <!-- 分页 -->
      <div v-if="filteredRecords.length > pageSize" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredRecords.length"
          :pager-count="5"
          layout="prev, pager, next"
          size="small"
          background
        />
      </div>

      <div v-if="!filteredRecords.length" class="empty-state">
        <el-empty :image-size="80" :description="totalCount ? '无匹配的版本记录' : '暂无版本记录'" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { VERSION_STATUS_TEXT } from '@/stores/app'
import { ElMessage } from 'element-plus'
import {
  Search, CircleCheck, CircleClose, Clock, Refresh, ArrowDown,
  Collection, Folder, CircleCheckFilled, List, Opportunity
} from '@element-plus/icons-vue'
import { WarnTriangleFilled } from '@element-plus/icons-vue'
import type { Version, VersionTask } from '@/types'
import { dispatchFlashing } from '@/api'

interface RecordVM {
  id: number
  version: string
  branchId: number
  branchName: string
  branchType: string
  status: number
  flashingTaskIds?: number[]
  tasks?: VersionTask[]
  // computed
  coverageStatus: 'covered' | 'covering' | 'uncovered'
  coverageLabel: string
  coverageTagType: 'success' | 'warning' | 'danger' | 'info'
  coverageClass: string
  passCount: number
  failCount: number
  totalCount: number
  passRate: number
}

const appStore = useAppStore()
const coverageFilter = ref('')
const searchKeyword = ref('')
const expandedDetails = ref<Set<number>>(new Set())

const toggleDetail = (id: number) => {
  const s = new Set(expandedDetails.value)
  if (s.has(id)) s.delete(id); else s.add(id)
  expandedDetails.value = s
}

// 根据 Version status 计算覆盖率状态
function computeCoverage(v: Version): {
  coverageStatus: 'covered' | 'covering' | 'uncovered'
  coverageLabel: string
  coverageTagType: 'success' | 'warning' | 'danger' | 'info'
  coverageClass: string
} {
  const s = v.status

  // 已完成 (COMPLETED)
  if (s === 5) {
    const anyFailed = (v.failCount ?? 0) > 0
    return {
      coverageStatus: 'covered',
      coverageLabel: anyFailed ? '测试未通过' : '测试通过',
      coverageTagType: anyFailed ? 'danger' : 'success',
      coverageClass: anyFailed ? 'covered-fail' : 'covered-pass',
    }
  }

  // 测试中 (TESTING)
  if (s === 4) {
    return {
      coverageStatus: 'covering',
      coverageLabel: '任务执行中',
      coverageTagType: 'warning',
      coverageClass: 'tasking',
    }
  }

  // 刷机中 (FLASHING)
  if (s === 2) {
    return {
      coverageStatus: 'covering',
      coverageLabel: '刷机中',
      coverageTagType: 'warning',
      coverageClass: 'flashing',
    }
  }

  // 等待中 (QUEUED)
  if (s === 1) {
    return {
      coverageStatus: 'covering',
      coverageLabel: '等待执行',
      coverageTagType: 'warning',
      coverageClass: 'flashing',
    }
  }

  // 刷机失败 (FLASH_FAILED)
  if (s === 3) {
    return {
      coverageStatus: 'uncovered',
      coverageLabel: '刷机失败',
      coverageTagType: 'danger',
      coverageClass: 'flash-failed',
    }
  }

  // 无设备 (NO_DEVICE)
  if (s === 0) {
    return {
      coverageStatus: 'uncovered',
      coverageLabel: '无对应设备',
      coverageTagType: 'info',
      coverageClass: 'blocked',
    }
  }

  // 已废弃 (OBSOLETED)
  if (s === 6) {
    return {
      coverageStatus: 'uncovered',
      coverageLabel: '已废弃',
      coverageTagType: 'info',
      coverageClass: 'blocked',
    }
  }

  return {
    coverageStatus: 'uncovered',
    coverageLabel: '未知',
    coverageTagType: 'info',
    coverageClass: 'blocked',
  }
}

function extractBranchType(branchName: string): string {
  if (branchName.startsWith('DEV')) return 'DEV'
  if (branchName.includes('主干')) return '主干'
  if (branchName.startsWith('商分') || branchName.includes('商分')) return '商分'
  return '其他'
}

const versions = computed(() => appStore.versions)

const allRecords = computed<RecordVM[]>(() => {
  return versions.value.map(v => {
    const coverage = computeCoverage(v)
    return {
      id: v.id,
      version: v.version,
      branchId: v.branchId,
      branchName: v.branchName,
      branchType: extractBranchType(v.branchName),
      status: v.status,
      flashingTaskIds: v.flashingTaskIds,
      tasks: v.tasks,
      passCount: v.passCount ?? 0,
      failCount: v.failCount ?? 0,
      totalCount: v.totalCount ?? 0,
      passRate: v.passRate ?? 0,
      ...coverage,
    }
  }).sort((a, b) => new Date(appStore.versions.find(v => v.id === b.id)?.createdAt || 0).getTime() - new Date(appStore.versions.find(v => v.id === a.id)?.createdAt || 0).getTime())
})

const totalCount = computed(() => allRecords.value.length)

const coveredCount = computed(() => allRecords.value.filter(r => r.coverageStatus === 'covered').length)
const coveringCount = computed(() => allRecords.value.filter(r => r.coverageStatus === 'covering').length)
const uncoveredCount = computed(() => allRecords.value.filter(r => r.coverageStatus === 'uncovered').length)

const coveredPassCount = computed(() => allRecords.value.filter(r => r.coverageStatus === 'covered' && r.coverageClass === 'covered-pass').length)
const coveredFailCount = computed(() => allRecords.value.filter(r => r.coverageStatus === 'covered' && r.coverageClass === 'covered-fail').length)

const flashingCount = computed(() => allRecords.value.filter(r => r.coverageClass === 'flashing').length)
const taskingCount = computed(() => allRecords.value.filter(r => r.coverageClass === 'tasking').length)

const noDeviceCount = computed(() => allRecords.value.filter(r => r.status === 0).length)
const failedCount = computed(() => allRecords.value.filter(r => r.status === 3).length)
const noMatchCount = computed(() => 0) // 新版本没有"未匹配"状态

const filteredRecords = ref<RecordVM[]>([])

const currentPage = ref(1)
const pageSize = 10
const pagedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredRecords.value.slice(start, start + pageSize)
})

const handleSearch = () => {
  currentPage.value = 1
  let list = allRecords.value
  if (coverageFilter.value) {
    list = list.filter(r => r.coverageStatus === coverageFilter.value)
  }
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    list = list.filter(r =>
      r.version.toLowerCase().includes(kw) ||
      r.branchName.toLowerCase().includes(kw)
    )
  }
  filteredRecords.value = list
}

const setCoverageFilter = (value: string) => {
  coverageFilter.value = coverageFilter.value === value ? '' : value
  handleSearch()
}

onMounted(() => {
  appStore.fetchVersions()
  handleSearch()
})

const branchTagType = (t: string) => {
  const map: Record<string, string> = { DEV: 'primary', 主干: 'success', 商分: 'warning' }
  return map[t] || 'info'
}

const formatTime = (t: string) => {
  if (!t) return '-'
  const d = new Date(t)
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  return `${mm}-${dd} ${hh}:${mi}`
}

// 下发刷机
const versionDispatchLoading = ref<number | null>(null)
const dispatchFlash = async (rec: RecordVM) => {
  versionDispatchLoading.value = rec.id
  try {
    const result = await dispatchFlashing(rec.id)
    if (result.code === 0) {
      ElMessage.success(`已下发刷机任务到 ${result.data?.process_count || 0} 台设备`)
      // 刷新版本数据
      await appStore.fetchVersions()
    } else {
      ElMessage.error(result.message || '下发刷机失败')
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '下发刷机失败')
  } finally {
    versionDispatchLoading.value = null
  }
}

// formatDuration 已移除（新类型中不需要）
</script>

<style scoped>
.coverage-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ========== 头部 ========== */
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

/* ========== 统计三卡 ========== */
.stats-row {
  display: flex;
  gap: 10px;
}

.stat-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  border-radius: 12px;
  padding: 14px 18px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
  user-select: none;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}

.stat-card.covered { border-left: 4px solid #67c23a; }
.stat-card.covered:hover,
.stat-card.covered:has(+ .stat-card.covered:hover) { border-color: #67c23a; }

.stat-card.covering { border-left: 4px solid #409eff; }
.stat-card.covering:hover { border-color: #409eff; }

.stat-card.uncovered { border-left: 4px solid #909399; }
.stat-card.uncovered:hover { border-color: #909399; }

.stat-card-icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-card.covered .stat-card-icon { background: #f0f9eb; color: #67c23a; }
.stat-card.covering .stat-card-icon { background: #ecf5ff; color: #409eff; }
.stat-card.uncovered .stat-card-icon { background: #f5f7fa; color: #909399; }

.stat-card-body {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.stat-detail {
  font-size: 11px;
  color: #bbb;
  text-align: right;
  white-space: nowrap;
}

/* ========== 版本卡片列表 ========== */
.record-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.record-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s;
}

.record-card:hover {
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

/* 状态色条 */
.status-bar {
  height: 3px;
}

.status-bar.covered-pass { background: linear-gradient(90deg, #67c23a, #95de64); }
.status-bar.covered-fail { background: linear-gradient(90deg, #f56c6c, #ff7875); }
.status-bar.tasking { background: linear-gradient(90deg, #409eff, #69b1ff); }
.status-bar.flashing { background: linear-gradient(90deg, #409eff, #69b1ff); }
.status-bar.blocked { background: linear-gradient(90deg, #c0c4cc, #dcdfe6); }
.status-bar.flash-failed { background: linear-gradient(90deg, #e6a23c, #f5a623); }

/* 卡主体 */
.card-body {
  display: flex;
  padding: 10px 16px;
  gap: 16px;
}

.card-main {
  flex: 1;
  min-width: 0;
}

.version-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.version-tag {
  font-size: 14px;
  font-weight: 700;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  color: #303133;
}

.version-tag.covered-pass { color: #67c23a; }
.version-tag.covered-fail { color: #f56c6c; }

.rec-time {
  font-size: 11px;
  color: #c0c4cc;
  margin-left: auto;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #909399;
  flex-wrap: wrap;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

.meta-chip code {
  font-size: 11px;
  background: #e9e9eb;
  padding: 1px 5px;
  border-radius: 3px;
  color: #606266;
}

.flashing-link {
  cursor: pointer;
  color: #409eff;
  transition: all 0.15s;
  padding: 1px 6px;
  border-radius: 4px;
}

.flashing-link:hover {
  background: #ecf5ff;
  text-decoration: underline;
}

.flashing-link.flash-failed-link {
  color: #f56c6c;
  font-weight: 600;
}

.flashing-link.flash-failed-link:hover {
  background: #fef0f0;
}

/* 结果概览区 */
.card-result {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 4px 0;
}

.result-pass {
  text-align: center;
}

.result-fail {
  text-align: center;
}

.result-err {
  text-align: center;
}

.result-big-num {
  font-size: 22px;
  font-weight: 700;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.result-pass .result-big-num { color: #67c23a; }
.result-fail .result-big-num { color: #f56c6c; }
.result-err .result-big-num { color: #e6a23c; }

.result-big-label {
  font-size: 10px;
  color: #909399;
  margin-top: 1px;
}

.result-rate {
  font-size: 20px;
  font-weight: 700;
  color: #67c23a;
  font-variant-numeric: tabular-nums;
  min-width: 50px;
  text-align: center;
}

.result-rate.warn {
  color: #e6a23c;
}

.coverage-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 6px;
  white-space: nowrap;
}

.coverage-badge.processing {
  background: #ecf5ff;
  color: #409eff;
}

.coverage-badge.blocked {
  background: #f5f7fa;
  color: #909399;
}

.rotating {
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ========== 展开区域 ========== */
.detail-area {
  border-top: 1px solid #f0f2f5;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-size: 12px;
  color: #909399;
  cursor: pointer;
  user-select: none;
  transition: background 0.15s;
}

.detail-header:hover {
  background: #f5f7fa;
}

.detail-arrow {
  margin-left: auto;
  font-size: 14px;
  color: #c0c4cc;
  transition: transform 0.25s;
}

.detail-arrow.expanded {
  transform: rotate(180deg);
  color: #409eff;
}

.task-detail-list {
  padding: 0 16px 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.task-detail-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  border-radius: 8px;
  background: #f5f7fa;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.task-detail-row:hover {
  background: #ecf5ff;
}

.td-left {
  display: flex;
  align-items: center;
  gap: 5px;
  min-width: 130px;
  flex-shrink: 0;
}

.task-detail-row.success .td-left :deep(.el-icon) { color: #67c23a; }
.task-detail-row.failed .td-left :deep(.el-icon),
.task-detail-row.error .td-left :deep(.el-icon) { color: #f56c6c; }
.task-detail-row.running .td-left :deep(.el-icon) { color: #409eff; }

.td-name {
  font-weight: 500;
  color: #303133;
}

.td-stats {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}

.td-rate {
  font-weight: 700;
  color: #67c23a;
  min-width: 36px;
}

.td-rate.warn {
  color: #e6a23c;
}

.td-count {
  color: #606266;
}

.td-duration {
  color: #bbb;
}

.td-bar-bg {
  flex: 1;
  height: 4px;
  background: #e9e9eb;
  border-radius: 2px;
  overflow: hidden;
}

.td-bar-fill {
  height: 100%;
  background: #67c23a;
  border-radius: 2px;
  transition: width 0.4s;
}

.td-bar-fill.warn {
  background: #e6a23c;
}

.td-bar-fill.danger {
  background: #f56c6c;
}

/* 原因说明 */
.detail-reason {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 8px 16px 10px;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

.detail-reason.pending {
  color: #e6a23c;
}

/* ========== 空状态 ========== */
.empty-state {
  background: #fff;
  border-radius: 12px;
  padding: 40px 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

/* ========== 动画 ========== */
.record-list-enter-active,
.record-list-leave-active {
  transition: all 0.3s ease;
}

.record-list-enter-from,
.record-list-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

/* ========== 响应式 ========== */
@media (max-width: 800px) {
  .stats-row { flex-direction: column; }
  .page-header { flex-direction: column; gap: 10px; align-items: stretch; }
  .card-result { display: none; }
}
/* ==================== 分页 ==================== */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 12px 0 4px;
}
</style>
