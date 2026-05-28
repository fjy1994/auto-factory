<template>
  <div class="branch-page">
    <!-- 头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-icon :size="22" color="#e6a23c"><Share /></el-icon>
        <span class="header-title">分支管理</span>
        <el-tag size="small" type="warning" effect="plain" round>{{ branches.length }} 个分支</el-tag>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索分支名称..."
          clearable
          size="small"
          style="width: 200px"
          :prefix-icon="Search"
        />
        <el-button type="primary" size="small" :icon="Plus" @click="showAddDialog">
          添加分支
        </el-button>
      </div>
    </div>

    <!-- 分支列表 -->
    <div class="branch-list-container">
      <div
        v-for="branch in filteredBranches"
        :key="branch.id"
        class="branch-card"
        :class="{
          collapsed: !expandedBranches.has(branch.id),
          disabled: branch.disabled
        }"
      >
        <!-- 分支头部 -->
        <div class="branch-header" @click="toggleBranch(branch.id)">
          <div class="branch-header-left">
            <div class="branch-icon" :style="{ background: branchIconBg(branch) }">
              <el-icon :size="20" :color="branchIconColor(branch)"><Share /></el-icon>
            </div>
            <div class="branch-info">
              <div class="branch-name">
                <span>{{ branch.name }}</span>
                <el-tag
                  :type="branchTagType(branch)"
                  size="small"
                  effect="dark"
                  round
                >
                  {{ branchTypeLabel(branch) }}
                </el-tag>
                <el-tag
                  v-if="branch.disabled"
                  type="danger"
                  size="small"
                  effect="plain"
                  round
                >
                  已禁用
                </el-tag>
              </div>
              <div class="branch-meta">
                <span>匹配规则: {{ branch.versionPattern || '未设置' }}</span>
              </div>
            </div>
          </div>
          <div class="branch-header-right">
            <el-tooltip :content="branch.disabled ? '已禁用' : '已启用'" placement="top">
              <el-icon :size="18" :color="branch.disabled ? '#c0c4cc' : '#67c23a'">
                <CircleCheck />
              </el-icon>
            </el-tooltip>
            <el-icon :size="18" color="#c0c4cc" class="expand-icon">
              <ArrowDown />
            </el-icon>
          </div>
        </div>

        <!-- 展开内容 -->
        <Transition name="collapse">
          <div v-show="expandedBranches.has(branch.id)" class="branch-detail">
            <el-divider style="margin: 0 0 12px 0;" />

            <!-- 基本信息 -->
            <div class="detail-section">
              <div class="section-title">
                <el-icon :size="14" color="#909399"><QuestionFilled /></el-icon>
                <span>基本信息</span>
              </div>
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">分支名称</span>
                  <span class="info-value">{{ branch.name }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">分支类型</span>
                  <span class="info-value">
                    <el-tag :type="branchTagType(branch)" size="small" effect="dark">
                      {{ branchTypeLabel(branch) }}
                    </el-tag>
                  </span>
                </div>
                <div class="info-item">
                  <span class="info-label">版本匹配规则</span>
                  <span class="info-value">
                    <code class="pattern-code">{{ branch.versionPattern || '-' }}</code>
                  </span>
                </div>
                <div class="info-item">
                  <span class="info-label">邮件标题匹配</span>
                  <span class="info-value">
                    <code class="pattern-code">{{ branch.mailTitlePattern || '-' }}</code>
                  </span>
                </div>
                <div class="info-item">
                  <span class="info-label">状态</span>
                  <span class="info-value">
                    <el-tag :type="branch.disabled ? 'danger' : 'success'" size="small" effect="plain" round>
                      {{ branch.disabled ? '已禁用' : '已启用' }}
                    </el-tag>
                  </span>
                </div>
                <div class="info-item">
                  <span class="info-label">创建时间</span>
                  <span class="info-value">{{ branch.createdAt ? formatDate(branch.createdAt) : '-' }}</span>
                </div>
              </div>
            </div>

            <!-- 任务配置 -->
            <div class="detail-section">
              <div class="section-title">
                <el-icon :size="14" color="#409eff"><List /></el-icon>
                <span>任务配置</span>
                <el-button size="small" text :icon="Plus" @click="showAddTask(branch.id)" />
              </div>
              <div v-if="branchTasks(branch.id).length" class="task-config-list">
                <div
                  v-for="(task, idx) in sortedTasks(branch.id)"
                  :key="task.id"
                  class="task-config-item"
                >
                  <div class="task-config-order">{{ idx + 1 }}</div>
                  <div class="task-config-info">
                    <div class="task-config-name">{{ task.name }}</div>
                            <div class="task-config-meta">
                      <span>用例集: {{ task.caseSets.length > 0 ? task.caseSets.join(', ') : '无' }}</span>
                      <span class="meta-divider">·</span>
                      <span>每批 {{ task.batchSize || 10 }} 个</span>
                      <span v-if="task.scriptPath" class="meta-divider">·</span>
                      <span v-if="task.scriptPath">脚本: {{ task.scriptPath }}</span>
                    </div>
                  </div>
                  <div class="task-config-actions">
                    <el-button size="small" text :icon="Edit" @click="editBranchTask(task)" />
                    <el-button size="small" text :icon="Delete" type="danger" @click="deleteBranchTask(task.id)" />
                  </div>
                </div>
              </div>
              <div v-else class="task-config-empty">
                <span>暂无任务配置，添加任务以在刷机完成后自动执行</span>
              </div>
            </div>

            <!-- 操作 -->
            <div class="detail-actions">
              <el-button size="small" :icon="Edit" @click="editBranch(branch)">编辑</el-button>
              <el-button size="small" type="danger" :icon="Delete" plain @click="deleteBranch(branch.id)">
                删除
              </el-button>
            </div>
          </div>
        </Transition>
      </div>

      <div v-if="!filteredBranches.length" class="empty-state">
        <el-empty :image-size="100" description="暂无分支数据">
          <template #image>
            <div class="empty-icon"><el-icon :size="48" color="#c0c4cc"><Share /></el-icon></div>
          </template>
          <el-button type="primary" size="small" :icon="Plus" @click="showAddDialog">添加分支</el-button>
        </el-empty>
      </div>
    </div>

    <!-- 添加 / 编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑分支' : '添加分支'"
      width="520px"
      class="branch-dialog"
      destroy-on-close
    >
      <el-form :model="form" label-width="110px" size="small">
        <el-form-item label="分支名称" required>
          <el-input v-model="form.name" placeholder="例如: DEV_7.1.0 / 主干_7.0.0 / 商分_6.8.0" />
        </el-form-item>
        <el-form-item label="版本匹配规则">
          <el-input v-model="form.versionPattern" placeholder="正则表达式，如 B\\d{2}SP\\d{2}.*" />
        </el-form-item>
        <el-form-item label="邮件标题匹配">
          <el-input v-model="form.mailTitlePattern" placeholder="邮件标题正则匹配规则" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.disabled" inactive-text="启用" active-text="禁用" :active-value="true" :inactive-value="false" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveBranch">保存</el-button>
      </template>
    </el-dialog>

    <!-- 任务配置弹窗 -->
    <el-dialog
      v-model="taskDialogVisible"
      title="配置任务"
      width="500px"
      class="branch-dialog"
      destroy-on-close
    >
      <el-form :model="taskForm" label-width="100px" size="small">
        <el-form-item label="任务名称" required>
          <el-input v-model="taskForm.name" placeholder="例如: 基础功能测试" />
        </el-form-item>
        <el-form-item label="脚本路径">
          <el-input v-model="taskForm.scriptPath" placeholder="/scripts/xxx.sh" />
        </el-form-item>
        <el-form-item label="每批下发">
          <el-input-number v-model="taskForm.batchSize" :min="1" :max="100" size="small" />
          <span style="margin-left: 8px; font-size: 12px; color: #909399;">个用例</span>
        </el-form-item>
        <el-form-item label="关联用例集">
          <el-select v-model="taskForm.caseSets" multiple placeholder="选择关联的用例集" style="width: 100%">
            <el-option
              v-for="tc in testCases"
              :key="tc.id"
              :label="`${tc.caseId} - ${tc.name}`"
              :value="tc.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="执行顺序">
          <el-input-number v-model="taskForm.order" :min="1" :max="20" size="small" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="taskDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveBranchTask">保存</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAppStore } from '@/stores/app'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Share, Search, Plus, Edit, Delete, ArrowDown, CircleCheck,
  QuestionFilled, List
} from '@element-plus/icons-vue'
import type { Branch, BranchTaskConfig } from '@/types'

const appStore = useAppStore()

const searchKeyword = ref('')
const expandedBranches = ref<Set<number>>(new Set())
const dialogVisible = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)

// 任务配置
const taskDialogVisible = ref(false)
const editingTaskId = ref<number | null>(null)
const editingTaskBranchId = ref<number | null>(null)
const taskForm = ref({
  name: '',
  scriptPath: '',
  caseSets: [] as number[],
  batchSize: 10,
  order: 1
})

const testCases = computed(() => appStore.testCases)

const branchTasks = (branchId: number) => {
  return appStore.branchTaskConfigs.filter(t => t.branchId === branchId)
}

const sortedTasks = (branchId: number) => {
  return branchTasks(branchId).sort((a, b) => a.order - b.order)
}

const showAddTask = (branchId: number) => {
  editingTaskId.value = null
  editingTaskBranchId.value = branchId
  taskForm.value = { name: '', scriptPath: '', caseSets: [], batchSize: 10, order: branchTasks(branchId).length + 1 }
  taskDialogVisible.value = true
}

const editBranchTask = (task: BranchTaskConfig) => {
  editingTaskId.value = task.id
  editingTaskBranchId.value = task.branchId
  taskForm.value = {
    name: task.name,
    scriptPath: task.scriptPath || '',
    caseSets: [...task.caseSets],
    batchSize: task.batchSize || 10,
    order: task.order
  }
  taskDialogVisible.value = true
}

const saveBranchTask = () => {
  if (!taskForm.value.name) {
    ElMessage.warning('请输入任务名称')
    return
  }
  if (editingTaskId.value) {
    const task = appStore.branchTaskConfigs.find(t => t.id === editingTaskId.value)
    if (task) {
      task.name = taskForm.value.name
      task.scriptPath = taskForm.value.scriptPath
      task.caseSets = [...taskForm.value.caseSets]
      task.batchSize = taskForm.value.batchSize
      task.order = taskForm.value.order
    }
  } else {
    appStore.branchTaskConfigs.push({
      id: Date.now(),
      branchId: editingTaskBranchId.value!,
      name: taskForm.value.name,
      scriptPath: taskForm.value.scriptPath,
      caseSets: [...taskForm.value.caseSets],
      batchSize: taskForm.value.batchSize,
      order: taskForm.value.order,
      createdAt: new Date().toISOString()
    })
  }
  taskDialogVisible.value = false
  ElMessage.success(editingTaskId.value ? '任务已更新' : '任务已添加')
}

const deleteBranchTask = async (taskId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除此任务配置吗？', '确认删除', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消'
    })
    appStore.branchTaskConfigs = appStore.branchTaskConfigs.filter(t => t.id !== taskId)
    ElMessage.success('任务已删除')
  } catch { /* canceled */ }
}

const branches = computed(() => appStore.branches)

const filteredBranches = computed(() => {
  if (!searchKeyword.value) return branches.value
  const kw = searchKeyword.value.toLowerCase()
  return branches.value.filter(b => b.name.toLowerCase().includes(kw))
})

const form = ref({
  name: '',
  versionPattern: '',
  mailTitlePattern: '',
  disabled: false
})

// 从分支名称推断分支类型
function getBranchType(name: string): 'dev' | 'trunk' | 'commercial' | 'other' {
  const lower = (name || '').toLowerCase()
  if (lower.startsWith('dev')) return 'dev'
  if (lower.startsWith('主干') || lower.startsWith('trunk') || lower.startsWith('main') || lower.startsWith('master')) return 'trunk'
  if (lower.startsWith('商分') || lower.startsWith('commercial') || lower.startsWith('comm')) return 'commercial'
  return 'other'
}

function branchTypeLabel(branch: Branch): string {
  const type = getBranchType(branch.name)
  switch (type) {
    case 'dev': return 'DEV'
    case 'trunk': return '主干'
    case 'commercial': return '商分'
    default: return branch.name.split(/[_\-/]/)[0] || '其他'
  }
}

function branchTagType(branch: Branch): string {
  const type = getBranchType(branch.name)
  switch (type) {
    case 'dev': return 'primary'
    case 'trunk': return 'success'
    case 'commercial': return 'warning'
    default: return 'info'
  }
}

function branchIconColor(branch: Branch): string {
  const type = getBranchType(branch.name)
  switch (type) {
    case 'dev': return '#409eff'
    case 'trunk': return '#67c23a'
    case 'commercial': return '#e6a23c'
    default: return '#909399'
  }
}

function branchIconBg(branch: Branch): string {
  const type = getBranchType(branch.name)
  switch (type) {
    case 'dev': return '#ecf5ff'
    case 'trunk': return '#f0f9eb'
    case 'commercial': return '#fdf6ec'
    default: return '#f5f7fa'
  }
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${day} ${h}:${min}`
}

const toggleBranch = (id: number) => {
  if (expandedBranches.value.has(id)) {
    expandedBranches.value.delete(id)
  } else {
    expandedBranches.value.add(id)
  }
}

const showAddDialog = () => {
  isEditing.value = false
  editingId.value = null
  form.value = { name: '', versionPattern: '', mailTitlePattern: '', disabled: false }
  dialogVisible.value = true
}

const editBranch = (branch: Branch) => {
  isEditing.value = true
  editingId.value = branch.id
  form.value = {
    name: branch.name,
    versionPattern: branch.versionPattern || '',
    mailTitlePattern: branch.mailTitlePattern || '',
    disabled: branch.disabled || false
  }
  dialogVisible.value = true
}

const saveBranch = () => {
  if (!form.value.name.trim()) {
    ElMessage.warning('请输入分支名称')
    return
  }
  if (isEditing.value && editingId.value !== null) {
    const idx = appStore.branches.findIndex(b => b.id === editingId.value)
    if (idx >= 0) {
      const branch = appStore.branches[idx]
      branch.name = form.value.name
      branch.versionPattern = form.value.versionPattern || undefined
      branch.mailTitlePattern = form.value.mailTitlePattern || undefined
      branch.disabled = form.value.disabled
      ElMessage.success('分支已更新')
    }
  } else {
    appStore.branches.push({
      id: Date.now(),
      name: form.value.name,
      versionPattern: form.value.versionPattern || undefined,
      mailTitlePattern: form.value.mailTitlePattern || undefined,
      disabled: form.value.disabled,
      createdAt: new Date().toISOString()
    })
    ElMessage.success('分支已创建')
  }
  dialogVisible.value = false
}

const deleteBranch = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除该分支吗？此操作不可撤销。', '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
    appStore.branches = appStore.branches.filter(b => b.id !== id)
    expandedBranches.value.delete(id)
    ElMessage.success('分支已删除')
  } catch { /* canceled */ }
}
</script>

<style scoped>
.branch-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
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

/* ==================== 分支卡片 ==================== */
.branch-list-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.branch-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  overflow: hidden;
  transition: box-shadow 0.3s, opacity 0.3s;
}

.branch-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

.branch-card.disabled {
  opacity: 0.7;
}

.branch-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  cursor: pointer;
  transition: background 0.2s;
}

.branch-header:hover {
  background: #f8f9fb;
}

.branch-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  min-width: 0;
}

.branch-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.branch-info {
  flex: 1;
  min-width: 0;
}

.branch-name {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 3px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  flex-wrap: wrap;
}

.branch-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
  flex-wrap: wrap;
}

.meta-divider {
  color: #dcdfe6;
  font-size: 10px;
}

.branch-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.expand-icon {
  transition: transform 0.3s;
}

.branch-card:not(.collapsed) .expand-icon {
  transform: rotate(180deg);
}

/* ==================== 展开内容 ==================== */
.branch-detail {
  padding: 0 20px 16px;
}

.detail-section {
  margin-bottom: 14px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 10px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.info-item {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 10px 12px;
  transition: background 0.2s;
}

.info-item:hover {
  background: #eef1f6;
}

.info-label {
  font-size: 11px;
  color: #909399;
  display: block;
  margin-bottom: 4px;
}

.info-value {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
}

.pattern-code {
  font-size: 12px;
  background: #e9e9eb;
  padding: 1px 6px;
  border-radius: 3px;
  color: #606266;
  word-break: break-all;
}

.detail-actions {
  display: flex;
  gap: 8px;
  padding-top: 8px;
}

/* ==================== 任务配置列表 ==================== */
.task-config-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.task-config-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 8px 12px;
  transition: background 0.2s;
}

.task-config-item:hover {
  background: #eef1f6;
}

.task-config-order {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.task-config-info {
  flex: 1;
  min-width: 0;
}

.task-config-name {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.task-config-meta {
  font-size: 11px;
  color: #909399;
  margin-top: 2px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.task-config-actions {
  display: flex;
  gap: 2px;
  flex-shrink: 0;
}

.task-config-empty {
  padding: 12px;
  text-align: center;
  font-size: 12px;
  color: #c0c4cc;
  background: #fafafa;
  border-radius: 8px;
  border: 1px dashed #dcdfe6;
}

/* ==================== 折叠动画 ==================== */
.collapse-enter-active,
.collapse-leave-active {
  transition: all 0.3s ease;
}
.collapse-enter-from,
.collapse-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
  margin-top: 0;
}
.collapse-enter-to,
.collapse-leave-from {
  opacity: 1;
  max-height: 500px;
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
@media (max-width: 800px) {
  .page-header {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  .info-grid {
    grid-template-columns: 1fr;
  }
  .branch-name {
    flex-wrap: wrap;
  }
}
</style>
