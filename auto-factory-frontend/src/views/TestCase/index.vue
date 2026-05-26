<template>
  <div class="testcase-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用例管理</span>
          <div class="header-actions">
            <el-upload
              ref="uploadRef"
              :show-file-list="false"
              :on-change="handleFileChange"
              :auto-upload="false"
              accept=".xlsx,.xls"
            >
              <el-button type="primary">
                <el-icon><Upload /></el-icon>
                导入Excel
              </el-button>
            </el-upload>
            <el-button @click="openAddDialog">
              <el-icon><Plus /></el-icon>
              新增用例
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-input v-model="filters.keyword" placeholder="搜索用例名称/编号" clearable style="width: 250px; margin-right: 10px;" />
        <el-select v-model="filters.module" placeholder="模块筛选" clearable style="width: 150px; margin-right: 10px;">
          <el-option v-for="mod in modules" :key="mod" :label="mod" :value="mod" />
        </el-select>
        <el-select v-model="filters.priority" placeholder="优先级筛选" clearable style="width: 130px; margin-right: 10px;">
          <el-option label="高" value="high" />
          <el-option label="中" value="medium" />
          <el-option label="低" value="low" />
        </el-select>
        <el-button type="primary" @click="resetFilters">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>

      <!-- 统计信息 -->
      <el-row :gutter="16" class="stats-row">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ testCases.length }}</div>
              <div class="stat-label">总用例数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card stat-success">
            <div class="stat-content">
              <div class="stat-value">{{ highCount }}</div>
              <div class="stat-label">高优先级</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card stat-warning">
            <div class="stat-content">
              <div class="stat-value">{{ mediumCount }}</div>
              <div class="stat-label">中优先级</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card stat-info">
            <div class="stat-content">
              <div class="stat-value">{{ lowCount }}</div>
              <div class="stat-label">低优先级</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 用例列表 -->
      <el-table :data="filteredCases" style="width: 100%" v-loading="loading">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="caseId" label="用例编号" width="120" />
        <el-table-column prop="name" label="用例名称" min-width="250" show-overflow-tooltip />
        <el-table-column prop="module" label="所属模块" width="120" />
        <el-table-column label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="steps" label="测试步骤" min-width="200" show-overflow-tooltip />
        <el-table-column prop="expected" label="预期结果" min-width="200" show-overflow-tooltip />
        <el-table-column prop="creator" label="创建人" width="100" />
        <el-table-column prop="createTime" label="创建时间" width="160" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="editCase(row)">
              编辑
            </el-button>
            <el-button link type="success" size="small" @click="viewCase(row)">
              详情
            </el-button>
            <el-button link type="danger" size="small" @click="deleteCase(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!filteredCases.length && !loading" description="暂无测试用例" style="margin-top: 60px;" />
    </el-card>

    <!-- 新增/编辑用例弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingCase ? '编辑用例' : '新增用例'"
      width="700px"
      destroy-on-close
    >
      <el-form :model="form" label-width="100px" label-position="left">
        <el-form-item label="用例编号" required>
          <el-input v-model="form.caseId" placeholder="如: TC-001" />
        </el-form-item>
        <el-form-item label="用例名称" required>
          <el-input v-model="form.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="所属模块" required>
          <el-select v-model="form.module" placeholder="请选择模块" style="width: 100%;">
            <el-option v-for="mod in modules" :key="mod" :label="mod" :value="mod" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" required>
          <el-radio-group v-model="form.priority">
            <el-radio value="high">高</el-radio>
            <el-radio value="medium">中</el-radio>
            <el-radio value="low">低</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="测试步骤">
          <el-input v-model="form.steps" type="textarea" :rows="4" placeholder="请输入测试步骤，每行一个步骤" />
        </el-form-item>
        <el-form-item label="预期结果">
          <el-input v-model="form.expected" type="textarea" :rows="3" placeholder="请输入预期结果" />
        </el-form-item>
        <el-form-item label="创建人">
          <el-input v-model="form.creator" placeholder="请输入创建人" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCase">保存</el-button>
      </template>
    </el-dialog>

    <!-- 用例详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      title="用例详情"
      width="700px"
    >
      <el-descriptions v-if="currentCase" :column="2" border>
        <el-descriptions-item label="用例编号">{{ currentCase.caseId }}</el-descriptions-item>
        <el-descriptions-item label="用例名称" :span="2">{{ currentCase.name }}</el-descriptions-item>
        <el-descriptions-item label="所属模块">{{ currentCase.module }}</el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="getPriorityType(currentCase.priority)" size="small">
            {{ getPriorityText(currentCase.priority) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="测试步骤" :span="2">
          <div class="detail-text">{{ currentCase.steps }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="预期结果" :span="2">
          <div class="detail-text">{{ currentCase.expected }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="创建人">{{ currentCase.creator }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ currentCase.createTime }}</el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 导入预览弹窗 -->
    <el-dialog
      v-model="importVisible"
      title="导入预览"
      width="900px"
      destroy-on-close
    >
      <div class="import-preview">
        <div class="import-info">
          <el-alert
            :title="importTitle"
            type="info"
            :closable="false"
          />
        </div>
        <el-table :data="importData" max-height="400" style="width: 100%; margin-top: 15px;">
          <el-table-column prop="caseId" label="用例编号" width="120" />
          <el-table-column prop="name" label="用例名称" min-width="200" show-overflow-tooltip />
          <el-table-column prop="module" label="所属模块" width="120" />
          <el-table-column label="优先级" width="90">
            <template #default="{ row }">
              <el-tag :type="getPriorityType(row.priority)" size="small">
                {{ getPriorityText(row.priority) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="steps" label="测试步骤" min-width="180" show-overflow-tooltip />
          <el-table-column prop="expected" label="预期结果" min-width="180" show-overflow-tooltip />
          <el-table-column prop="creator" label="创建人" width="100" />
        </el-table>
      </div>

      <template #footer>
        <el-button @click="importVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmImport">确认导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Plus, Refresh } from '@element-plus/icons-vue'
import type { TestCase } from '@/types'
// import * as XLSX from 'xlsx'

const loading = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const importVisible = ref(false)
const editingCase = ref<TestCase | null>(null)
const currentCase = ref<TestCase | null>(null)

const filters = ref({
  keyword: '',
  module: '',
  priority: ''
})

const form = ref({
  caseId: '',
  name: '',
  module: '',
  priority: 'medium' as 'high' | 'medium' | 'low',
  steps: '',
  expected: '',
  creator: ''
})

const importData = ref<TestCase[]>([])

const modules = ['登录模块', '用户管理', '权限管理', '订单管理', '商品管理', '报表统计', '系统设置']

// 模拟数据
const testCases = ref<TestCase[]>([
  {
    id: 1,
    caseId: 'TC-001',
    name: '验证正常登录功能',
    module: '登录模块',
    priority: 'high',
    steps: '1. 输入正确用户名\n2. 输入正确密码\n3. 点击登录按钮',
    expected: '成功登录，跳转到首页',
    creator: '张三',
    createTime: '2024-01-15 10:00:00'
  },
  {
    id: 2,
    caseId: 'TC-002',
    name: '验证错误密码登录',
    module: '登录模块',
    priority: 'high',
    steps: '1. 输入正确用户名\n2. 输入错误密码\n3. 点击登录按钮',
    expected: '提示"用户名或密码错误"，无法登录',
    creator: '张三',
    createTime: '2024-01-15 10:05:00'
  },
  {
    id: 3,
    caseId: 'TC-003',
    name: '验证空用户名登录',
    module: '登录模块',
    priority: 'medium',
    steps: '1. 用户名为空\n2. 输入正确密码\n3. 点击登录按钮',
    expected: '提示"请输入用户名"',
    creator: '李四',
    createTime: '2024-01-15 10:10:00'
  },
  {
    id: 4,
    caseId: 'TC-004',
    name: '验证用户列表查询功能',
    module: '用户管理',
    priority: 'medium',
    steps: '1. 进入用户管理页面\n2. 输入查询条件\n3. 点击查询按钮',
    expected: '显示符合条件的用户列表',
    creator: '李四',
    createTime: '2024-01-16 09:30:00'
  },
  {
    id: 5,
    caseId: 'TC-005',
    name: '验证新增用户功能',
    module: '用户管理',
    priority: 'high',
    steps: '1. 点击新增按钮\n2. 填写用户信息\n3. 点击保存',
    expected: '用户创建成功，列表中显示新用户',
    creator: '王五',
    createTime: '2024-01-16 14:20:00'
  },
  {
    id: 6,
    caseId: 'TC-006',
    name: '验证订单创建功能',
    module: '订单管理',
    priority: 'high',
    steps: '1. 选择商品\n2. 填写收货地址\n3. 提交订单',
    expected: '订单创建成功，状态为待付款',
    creator: '王五',
    createTime: '2024-01-17 11:00:00'
  }
])

const importTitle = computed(() => '共解析到 ' + importData.value.length + ' 条用例，请确认后点击导入')

const filteredCases = computed(() => {
  let result = [...testCases.value]
  
  if (filters.value.keyword) {
    const keyword = filters.value.keyword.toLowerCase()
    result = result.filter(c => 
      c.caseId.toLowerCase().includes(keyword) || 
      c.name.toLowerCase().includes(keyword)
    )
  }
  
  if (filters.value.module) {
    result = result.filter(c => c.module === filters.value.module)
  }
  
  if (filters.value.priority) {
    result = result.filter(c => c.priority === filters.value.priority)
  }
  
  return result
})

const highCount = computed(() => testCases.value.filter(c => c.priority === 'high').length)
const mediumCount = computed(() => testCases.value.filter(c => c.priority === 'medium').length)
const lowCount = computed(() => testCases.value.filter(c => c.priority === 'low').length)

const getPriorityType = (priority: string) => {
  const map: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return map[priority] || 'info'
}

const getPriorityText = (priority: string) => {
  const map: Record<string, string> = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return map[priority] || priority
}

const resetFilters = () => {
  filters.value = {
    keyword: '',
    module: '',
    priority: ''
  }
}

const openAddDialog = () => {
  editingCase.value = null
  form.value = {
    caseId: '',
    name: '',
    module: '',
    priority: 'medium',
    steps: '',
    expected: '',
    creator: ''
  }
  dialogVisible.value = true
}

const editCase = (row: TestCase) => {
  editingCase.value = row
  form.value = {
    caseId: row.caseId,
    name: row.name,
    module: row.module,
    priority: row.priority,
    steps: row.steps,
    expected: row.expected,
    creator: row.creator
  }
  dialogVisible.value = true
}

const viewCase = (row: TestCase) => {
  currentCase.value = row
  detailVisible.value = true
}

const saveCase = () => {
  if (!form.value.caseId || !form.value.name || !form.value.module) {
    ElMessage.warning('请填写必填项')
    return
  }

  if (editingCase.value) {
    // 编辑
    const index = testCases.value.findIndex(c => c.id === editingCase.value!.id)
    if (index > -1) {
      testCases.value[index] = {
        ...testCases.value[index],
        ...form.value
      }
    }
    ElMessage.success('用例已更新')
  } else {
    // 新增
    const newCase: TestCase = {
      id: Date.now(),
      ...form.value,
      createTime: new Date().toLocaleString('zh-CN')
    }
    testCases.value.unshift(newCase)
    ElMessage.success('用例已添加')
  }

  dialogVisible.value = false
}

const deleteCase = (row: TestCase) => {
  ElMessageBox.confirm(
    '确定要删除用例 "' + row.name + '" 吗？',
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const index = testCases.value.findIndex(c => c.id === row.id)
    if (index > -1) {
      testCases.value.splice(index, 1)
      ElMessage.success('用例已删除')
    }
  }).catch(() => {})
}

// Excel文件处理
const handleFileChange = (file: any) => {
  // 实际项目中需要安装 xlsx 库并取消注释 import
  // npm install xlsx
  
  // 模拟解析Excel
  // const reader = new FileReader()
  // reader.onload = (e) => {
  //   const data = e.target?.result
  //   const workbook = XLSX.read(data, { type: 'binary' })
  //   const sheetName = workbook.SheetNames[0]
  //   const worksheet = workbook.Sheets[sheetName]
  //   const json = XLSX.utils.sheet_to_json(worksheet)
  //   
  //   importData.value = json.map((item: any, index: number) => ({
  //     id: Date.now() + index,
  //     caseId: item['用例编号'] || item['caseId'] || 'TC-' + (Date.now() + index),
  //     name: item['用例名称'] || item['name'] || '',
  //     module: item['所属模块'] || item['module'] || '其他',
  //     priority: (item['优先级'] || item['priority'] || 'medium').toLowerCase().replace('高', 'high').replace('中', 'medium').replace('低', 'low'),
  //     steps: item['测试步骤'] || item['steps'] || '',
  //     expected: item['预期结果'] || item['expected'] || '',
  //     creator: item['创建人'] || item['creator'] || '导入',
  //     createTime: new Date().toLocaleString('zh-CN')
  //   }))
  //   
  //   importVisible.value = true
  // }
  // reader.readAsBinaryString(file.raw)

  // 模拟导入效果
  const mockImport = [
    {
      id: Date.now() + 1,
      caseId: 'IMP-001',
      name: 'Excel导入测试用例1',
      module: '系统设置',
      priority: 'high' as 'high' | 'medium' | 'low',
      steps: '步骤1\n步骤2\n步骤3',
      expected: '预期结果1',
      creator: 'Excel导入',
      createTime: new Date().toLocaleString('zh-CN')
    },
    {
      id: Date.now() + 2,
      caseId: 'IMP-002',
      name: 'Excel导入测试用例2',
      module: '报表统计',
      priority: 'medium' as 'high' | 'medium' | 'low',
      steps: '步骤A\n步骤B',
      expected: '预期结果2',
      creator: 'Excel导入',
      createTime: new Date().toLocaleString('zh-CN')
    }
  ]
  importData.value = mockImport
  importVisible.value = true
}

const confirmImport = () => {
  importData.value.forEach(item => {
    testCases.value.unshift({
      ...item,
      id: Date.now() + Math.random()
    })
  })
  ElMessage.success('成功导入 ' + importData.value.length + ' 条用例')
  importVisible.value = false
  importData.value = []
}

onMounted(() => {
  // 初始化
})
</script>

<style scoped>
.testcase-page {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.stat-card.stat-success {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.stat-card.stat-warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card.stat-info {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
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

.detail-text {
  white-space: pre-wrap;
  line-height: 1.6;
}

.import-info {
  margin-bottom: 15px;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>
