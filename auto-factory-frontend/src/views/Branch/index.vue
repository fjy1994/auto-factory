<template>
  <div class="branch-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>分支管理</span>
          <el-button type="primary" @click="openAddBranchDialog">
            <el-icon><Plus /></el-icon>
            新增分支
          </el-button>
        </div>
      </template>

      <!-- 分支列表 -->
      <div class="branch-list">
        <el-collapse v-model="activeNames">
          <el-collapse-item
            v-for="branch in branches"
            :key="branch.id"
            :name="branch.id.toString()"
          >
            <template #title>
              <div class="branch-title">
                <span class="branch-name">{{ branch.name }}</span>
                <el-tag v-if="branch.disabled" size="small" type="danger">已禁用</el-tag>
                <div class="branch-actions">
                  <el-switch
                    v-model="branch.disabled"
                    size="small"
                    active-text="禁用"
                    inactive-text="启用"
                    @change="toggleBranchDisabled(branch)"
                  />
                  <el-button link type="primary" size="small" @click.stop="editBranch(branch)">
                    <el-icon><Edit /></el-icon>
                    编辑
                  </el-button>
                  <el-button link type="danger" size="small" @click.stop="deleteBranch(branch)">
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </div>
              </div>
            </template>

            <!-- 任务配置列表 -->
            <div class="task-config-section">
              <div class="section-header">
                <span>任务配置列表</span>
                <el-button type="primary" size="small" @click="openAddTaskDialog(branch)">
                  <el-icon><Plus /></el-icon>
                  新增任务配置
                </el-button>
              </div>

              <el-table :data="branch.tasks" style="width: 100%" size="small">
                <el-table-column prop="name" label="任务名称" />
                <el-table-column prop="scriptPath" label="脚本路径" />
                <el-table-column label="设备数量范围" width="150">
                  <template #default="{ row }">
                    {{ row.minDeviceCount }} ~ {{ row.maxDeviceCount }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="120" fixed="right">
                  <template #default="{ row }">
                    <el-button link type="primary" size="small" @click="editTaskConfig(branch, row)">
                      编辑
                    </el-button>
                    <el-button link type="danger" size="small" @click="deleteTaskConfig(branch, row)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>

              <el-empty v-if="!branch.tasks.length" description="暂无任务配置" />
            </div>
          </el-collapse-item>
        </el-collapse>

        <el-empty v-if="!branches.length" description="暂无分支数据" />
      </div>
    </el-card>

    <!-- 新增/编辑分支弹窗 -->
    <el-dialog
      v-model="branchDialogVisible"
      :title="editingBranch ? '编辑分支' : '新增分支'"
      width="500px"
    >
      <el-form :model="branchForm" label-width="100px">
        <el-form-item label="分支名称" required>
          <el-input v-model="branchForm.name" placeholder="如: 开发7.1、主干7.0" />
        </el-form-item>
        <el-form-item label="版本匹配" required>
          <el-input v-model="branchForm.versionPattern" placeholder="如: ^dev71_、^master70_\d+" />
          <div class="form-tip">支持正则表达式，用于从版本号中匹配识别所属分支</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="branchDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveBranch">保存</el-button>
      </template>
    </el-dialog>

    <!-- 新增/编辑任务配置弹窗 -->
    <el-dialog
      v-model="taskDialogVisible"
      :title="editingTask ? '编辑任务配置' : '新增任务配置'"
      width="600px"
    >
      <el-form :model="taskForm" label-width="120px">
        <el-form-item label="任务名称" required>
          <el-input v-model="taskForm.name" placeholder="如: 功能自动化用例、稳定性自动化用例" />
        </el-form-item>
        <el-form-item label="脚本路径">
          <el-input v-model="taskForm.scriptPath" placeholder="执行脚本的路径" />
        </el-form-item>
        <el-form-item label="设备数量范围">
          <el-input-number v-model="taskForm.minDeviceCount" :min="1" :max="100" class="device-count-input" />
          <span class="device-count-separator">~</span>
          <el-input-number v-model="taskForm.maxDeviceCount" :min="1" :max="100" class="device-count-input" />
          <div class="form-tip">空闲设备超过min台时才创建任务，最多同时使用max台设备批跑</div>
        </el-form-item>
        <el-form-item label="用例匹配">
          <el-input v-model="taskForm.casePattern" type="textarea" :rows="3" placeholder="支持正则表达式，指定该任务执行哪些用例" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="taskDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTaskConfig">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import type { Branch, TaskConfig } from '@/types'

const activeNames = ref<string[]>(['1'])
const branchDialogVisible = ref(false)
const taskDialogVisible = ref(false)
const editingBranch = ref<Branch | null>(null)
const editingTask = ref<TaskConfig | null>(null)
const currentBranch = ref<Branch | null>(null)

const branches = ref<Branch[]>([
  {
    id: 1,
    name: '开发7.1',
    versionPattern: '^dev71_',
    disabled: false,
    createdAt: '2024-01-01T00:00:00.000Z',
    tasks: [
      {
        id: 1,
        name: '功能自动化用例',
        scriptPath: '/scripts/functional_test.sh',
        minDeviceCount: 1,
        maxDeviceCount: 3,
        casePattern: '^test_.*'
      },
      {
        id: 2,
        name: '稳定性自动化用例',
        scriptPath: '/scripts/stability_test.sh',
        minDeviceCount: 2,
        maxDeviceCount: 5,
        casePattern: '^stability_.*'
      }
    ]
  },
  {
    id: 2,
    name: '主干7.0',
    versionPattern: '^master70_',
    disabled: false,
    createdAt: '2024-01-01T00:00:00.000Z',
    tasks: [
      {
        id: 3,
        name: '功能自动化用例',
        scriptPath: '/scripts/functional_test.sh',
        minDeviceCount: 1,
        maxDeviceCount: 2,
        casePattern: '.*'
      }
    ]
  }
])

const branchForm = ref({
  name: '',
  versionPattern: ''
})

const taskForm = ref({
  name: '',
  scriptPath: '',
  minDeviceCount: 1,
  maxDeviceCount: 3,
  casePattern: ''
})

const openAddBranchDialog = () => {
  editingBranch.value = null
  branchForm.value = { name: '', versionPattern: '' }
  branchDialogVisible.value = true
}

const editBranch = (branch: Branch) => {
  editingBranch.value = branch
  branchForm.value = {
    name: branch.name,
    versionPattern: branch.versionPattern
  }
  branchDialogVisible.value = true
}

const toggleBranchDisabled = (branch: Branch) => {
  ElMessage.success(branch.disabled ? '分支已禁用' : '分支已启用')
}

const saveBranch = () => {
  if (!branchForm.value.name || !branchForm.value.versionPattern) {
    ElMessage.warning('请填写必填项')
    return
  }

  if (editingBranch.value) {
    // 编辑
    editingBranch.value.name = branchForm.value.name
    editingBranch.value.versionPattern = branchForm.value.versionPattern
    ElMessage.success('分支已更新')
  } else {
    // 新增
    const newBranch: Branch = {
      id: Date.now(),
      name: branchForm.value.name,
      versionPattern: branchForm.value.versionPattern,
      disabled: false,
      createdAt: new Date().toISOString(),
      tasks: []
    }
    branches.value.push(newBranch)
    ElMessage.success('分支已添加')
  }

  branchDialogVisible.value = false
}

const deleteBranch = (branch: Branch) => {
  ElMessageBox.confirm(
    `确定要删除分支 "${branch.name}" 吗？其下的任务配置也会被删除。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const index = branches.value.findIndex(b => b.id === branch.id)
    if (index > -1) {
      branches.value.splice(index, 1)
      ElMessage.success('分支已删除')
    }
  }).catch(() => {})
}

const openAddTaskDialog = (branch: Branch) => {
  currentBranch.value = branch
  editingTask.value = null
  taskForm.value = {
    name: '',
    scriptPath: '',
    minDeviceCount: 1,
    maxDeviceCount: 3,
    casePattern: ''
  }
  taskDialogVisible.value = true
}

const editTaskConfig = (branch: Branch, task: TaskConfig) => {
  currentBranch.value = branch
  editingTask.value = task
  taskForm.value = {
    name: task.name,
    scriptPath: task.scriptPath,
    minDeviceCount: task.minDeviceCount,
    maxDeviceCount: task.maxDeviceCount,
    casePattern: task.casePattern
  }
  taskDialogVisible.value = true
}

const saveTaskConfig = () => {
  if (!taskForm.value.name) {
    ElMessage.warning('请填写任务名称')
    return
  }

  if (!currentBranch.value) return

  if (taskForm.value.minDeviceCount > taskForm.value.maxDeviceCount) {
    ElMessage.warning('最小设备数不能大于最大设备数')
    return
  }

  if (editingTask.value) {
    // 编辑
    Object.assign(editingTask.value, taskForm.value)
    ElMessage.success('任务配置已更新')
  } else {
    // 新增
    const newTask: TaskConfig = {
      id: Date.now(),
      ...taskForm.value
    }
    currentBranch.value.tasks.push(newTask)
    ElMessage.success('任务配置已添加')
  }

  taskDialogVisible.value = false
}

const deleteTaskConfig = (branch: Branch, task: TaskConfig) => {
  ElMessageBox.confirm(
    `确定要删除任务配置 "${task.name}" 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const index = branch.tasks.findIndex(t => t.id === task.id)
    if (index > -1) {
      branch.tasks.splice(index, 1)
      ElMessage.success('任务配置已删除')
    }
  }).catch(() => {})
}

onMounted(() => {
  activeNames.value = ['1', '2']
})
</script>

<style scoped>
.branch-page {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.branch-title {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.branch-name {
  font-size: 16px;
  font-weight: 600;
}

.branch-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-config-section {
  padding: 10px 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  font-weight: 500;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.device-count-input {
  width: 120px;
}

.device-count-separator {
  margin: 0 8px;
}
</style>
