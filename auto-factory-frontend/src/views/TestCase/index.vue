<template>
  <div class="testcase-page">
    <!-- 头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-icon :size="22" color="#67c23a"><Document /></el-icon>
        <span class="header-title">用例管理</span>
        <el-tag size="small" type="success" effect="plain" round>
          {{ testCases.length }} 个用例
        </el-tag>
      </div>
      <div class="header-right">
        <el-select v-model="moduleFilter" placeholder="模块" clearable size="small" style="width: 120px">
          <el-option v-for="m in modules" :key="m" :label="m" :value="m" />
        </el-select>
        <el-select v-model="priorityFilter" placeholder="优先级" clearable size="small" style="width: 110px">
          <el-option label="L0" value="L0" />
          <el-option label="L1" value="L1" />
          <el-option label="L2" value="L2" />
          <el-option label="L3" value="L3" />
          <el-option label="L4" value="L4" />
        </el-select>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索用例名称 / ID..."
          clearable
          size="small"
          style="width: 180px"
        />
        <el-button size="small" :icon="Search" @click="handleSearch">查询</el-button>
        <el-button size="small" :icon="Upload" @click="showImportDialog">导入用例</el-button>
        <el-button type="primary" size="small" :icon="Plus" @click="showAddDialog">新建用例</el-button>
      </div>
    </div>

    <!-- 统计条 + 表格 / 用例集 -->
    <el-tabs v-model="currentTab" class="page-tabs" @tab-change="handleTabChange">
      <el-tab-pane label="用例" name="cases">
        <!-- 统计条 -->
        <div class="stats-row">
          <div v-for="s in caseStats" :key="s.key" class="stat-chip" :style="{ background: s.bg }">
            <el-icon :size="16" color="#fff"><component :is="s.icon" /></el-icon>
            <span class="stat-value">{{ s.count }}</span>
            <span class="stat-label">{{ s.label }}</span>
          </div>
        </div>

        <!-- 表格 -->
        <div class="table-container">
          <el-table
            :data="pagedCases"
            style="width: 100%"
            stripe
            class="case-table"
            @row-click="showDetail"
          >
            <el-table-column label="用例信息" min-width="200">
              <template #default="{ row }">
                <div class="case-info-cell">
                  <div class="case-id">#{{ row.caseId }}</div>
                  <div class="case-name">{{ row.name }}</div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="模块" width="120">
              <template #default="{ row }">
                <div class="module-cell">
                  <el-icon :size="14" color="#909399"><Folder /></el-icon>
                  <span>{{ row.module }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="优先级" width="100" align="center">
              <template #default="{ row }">
                <el-tag
                  :type="priorityType(row.priority)"
                  size="small"
                  effect="light"
                  round
                >
                  {{ priorityText(row.priority) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="责任人" width="100">
              <template #default="{ row }">
                <div class="creator-cell">
                  <el-avatar :size="22" style="background: #409eff; vertical-align: middle; font-size: 11px;">
                    {{ row.creator.charAt(0) }}
                  </el-avatar>
                  <span style="margin-left: 6px;">{{ row.creator }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="创建时间" width="140">
              <template #default="{ row }">
                <div class="time-cell">
                  <el-icon :size="12" color="#909399"><Clock /></el-icon>
                  {{ formatTime(row.createdAt) }}
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center" fixed="right">
              <template #default="{ row }">
                <el-tooltip content="编辑" placement="top">
                  <el-button link type="primary" :icon="Edit" size="small" @click.stop="editCase(row)" />
                </el-tooltip>
                <el-tooltip content="删除" placement="top">
                  <el-button link type="danger" :icon="Delete" size="small" @click.stop="deleteCase(row.id)" />
                </el-tooltip>
              </template>
            </el-table-column>
            <template #empty>
              <el-empty :image-size="100" description="暂无用例数据">
                <template #image>
                  <div class="empty-icon"><el-icon :size="48" color="#c0c4cc"><Document /></el-icon></div>
                </template>
              </el-empty>
            </template>
          </el-table>

          <!-- 分页 -->
          <div v-if="filteredCases.length > pageSize" class="pagination-wrapper" style="margin-top: 12px;">
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="pageSize"
              :total="filteredCases.length"
              :pager-count="5"
              layout="prev, pager, next"
              size="small"
              background
            />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="用例集" name="sets">
        <div class="sets-header">
          <span class="sets-count">{{ caseSets.length }} 个用例集</span>
          <el-button type="primary" size="small" :icon="Plus" @click="showAddSetDialog">新建用例集</el-button>
        </div>
        <div class="sets-grid">
          <div v-for="s in caseSets" :key="s.id" class="set-card">
            <div class="set-card-top">
              <div class="set-icon">
                <el-icon :size="20" color="#409eff"><Collection /></el-icon>
              </div>
              <div class="set-info">
                <div class="set-name">{{ s.name }}</div>
                <div class="set-desc">{{ s.description || '暂无描述' }}</div>
              </div>
              <div class="set-actions">
                <el-tooltip content="编辑" placement="top">
                  <el-button link type="primary" :icon="Edit" size="small" @click="editSet(s)" />
                </el-tooltip>
                <el-tooltip content="删除" placement="top">
                  <el-button link type="danger" :icon="Delete" size="small" @click="deleteSet(s.id)" />
                </el-tooltip>
              </div>
            </div>
            <div class="set-card-bottom">
              <el-tag size="small" type="info" effect="plain" round>{{ s.caseIds.length }} 个用例</el-tag>
              <span class="set-time">{{ formatTime(s.createdAt) }}</span>
            </div>
            <div v-if="s.caseIds.length > 0" class="set-cases">
              <span v-for="tc in getCasesInSet(s)" :key="tc.id" class="set-case-tag">
                {{ tc.caseId }}
              </span>
              <span v-if="s.caseIds.length > 5" class="set-case-more">+{{ s.caseIds.length - 5 }}</span>
            </div>
          </div>
          <div v-if="caseSets.length === 0" class="sets-empty">
            <el-empty :image-size="80" description="暂无用例集">
              <template #image>
                <el-icon :size="48" color="#c0c4cc"><Collection /></el-icon>
              </template>
            </el-empty>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      :title="'用例详情 — ' + selectedCase?.caseId"
      width="680px"
      class="case-dialog"
      destroy-on-close
    >
      <div v-if="selectedCase" class="detail-body">
        <div class="detail-summary">
          <div class="ds-left">
            <div class="ds-title">{{ selectedCase.name }}</div>
            <div class="ds-meta">
              <el-tag :type="priorityType(selectedCase.priority)" size="small" round>
                {{ priorityText(selectedCase.priority) }}
              </el-tag>
              <span class="ds-module">{{ selectedCase.module }}</span>
              <span class="ds-divider">·</span>
              <span>{{ selectedCase.creator }}</span>
            </div>
          </div>
          <div class="ds-right">
            <el-avatar :size="40" style="background: #409eff;">{{ selectedCase.creator.charAt(0) }}</el-avatar>
          </div>
        </div>

        <div class="detail-sections">
          <div class="section-block">
            <div class="section-label">测试步骤</div>
            <div class="section-content steps-content">{{ selectedCase.steps || '无描述' }}</div>
          </div>
          <div class="section-block">
            <div class="section-label">预期结果</div>
            <div class="section-content expected-content">{{ selectedCase.expected || '无描述' }}</div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 编辑/新建弹窗 -->
    <el-dialog
      v-model="editVisible"
      :title="isEditing ? '编辑用例' : '新建用例'"
      width="560px"
      class="case-dialog"
      destroy-on-close
    >
      <el-form :model="form" label-width="100px" size="small">
        <el-form-item label="用例名称" required>
          <el-input v-model="form.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="用例编号">
          <el-input v-model="form.caseId" placeholder="如 TC-001" :disabled="isEditing" />
        </el-form-item>
        <el-form-item label="所属模块">
          <el-select v-model="form.module" placeholder="请选择模块" style="width: 100%">
            <el-option v-for="m in modules" :key="m" :label="m" :value="m" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-radio-group v-model="form.priority">
            <el-radio-button value="L0">L0</el-radio-button>
            <el-radio-button value="L1">L1</el-radio-button>
            <el-radio-button value="L2">L2</el-radio-button>
            <el-radio-button value="L3">L3</el-radio-button>
            <el-radio-button value="L4">L4</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="测试步骤">
          <el-input v-model="form.steps" type="textarea" :rows="3" placeholder="描述测试步骤" />
        </el-form-item>
        <el-form-item label="预期结果">
          <el-input v-model="form.expected" type="textarea" :rows="3" placeholder="描述预期结果" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCase">保存</el-button>
      </template>
    </el-dialog>

    <!-- 导入弹窗 -->
    <el-dialog
      v-model="importVisible"
      title="导入用例"
      width="760px"
      class="case-dialog"
      destroy-on-close
    >
      <div class="import-body">
        <!-- 尚未选择文件 -->
        <div v-if="!importData.file" class="import-upload-area" @click="triggerUpload">
          <el-icon :size="48" color="#409eff"><Upload /></el-icon>
          <p class="import-upload-hint">点击选择 Excel 文件</p>
          <p class="import-upload-desc">支持 .xlsx / .xls 格式</p>
        </div>

        <!-- 已选择文件，显示预览 -->
        <div v-if="importData.file" class="import-preview">
          <div class="import-file-info">
            <el-icon :size="20" color="#67c23a"><Document /></el-icon>
            <span class="import-file-name">{{ importData.file.name }}</span>
            <el-button link type="danger" size="small" :icon="Delete" @click="clearImport" />
          </div>

          <div v-if="parseError" class="import-error">{{ parseError }}</div>

          <el-table
            v-if="importData.rows.length > 0"
            :data="importData.rows"
            stripe
            max-height="320"
            style="width: 100%"
            class="import-table"
          >
            <el-table-column label="用例名称" prop="name" min-width="160" />
            <el-table-column label="模块" prop="module" width="100" />
            <el-table-column label="优先级" width="80">
              <template #default="{ row }">
                <el-tag :type="priorityType(row.priority)" size="small" round>{{ priorityText(row.priority) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="步骤" prop="steps" min-width="140">
              <template #default="{ row }">
                <span class="cell-preview">{{ row.steps || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="预期结果" prop="expected" min-width="140">
              <template #default="{ row }">
                <span class="cell-preview">{{ row.expected || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="责任人" prop="creator" width="80" />
          </el-table>

          <div v-if="importData.rows.length > 0" class="import-summary">
            共解析到 <strong>{{ importData.rows.length }}</strong> 条用例
          </div>
        </div>

        <!-- 隐藏的 file input -->
        <input
          ref="fileInputRef"
          type="file"
          accept=".xlsx,.xls"
          style="display:none"
          @change="handleFileChange"
        />
      </div>
      <template #footer>
        <el-button @click="importVisible = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="importData.rows.length === 0"
          :loading="importing"
          @click="confirmImport"
        >确认导入</el-button>
      </template>
    </el-dialog>

    <!-- 用例集编辑/新建弹窗 -->
    <el-dialog
      v-model="setEditVisible"
      :title="isEditingSet ? '编辑用例集' : '新建用例集'"
      width="560px"
      class="case-dialog"
      destroy-on-close
    >
      <el-form :model="setForm" label-width="100px" size="small">
        <el-form-item label="用例集名称" required>
          <el-input v-model="setForm.name" placeholder="请输入用例集名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="setForm.description" type="textarea" :rows="2" placeholder="描述用例集的用途" />
        </el-form-item>
        <el-form-item label="关联用例">
          <el-select v-model="setForm.caseIds" multiple placeholder="选择要包含的用例" style="width: 100%">
            <el-option
              v-for="tc in testCases"
              :key="tc.id"
              :label="`${tc.caseId} — ${tc.name}`"
              :value="tc.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="setEditVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSet">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document, Search, Plus, Edit, Delete, Folder, Clock, Warning, CircleCheck, InfoFilled, Collection, Upload
} from '@element-plus/icons-vue'
import type { TestCase, CaseSet } from '@/types'
import * as XLSX from 'xlsx'

const appStore = useAppStore()

const currentTab = ref('cases')

const moduleFilter = ref('')
const priorityFilter = ref('')
const searchKeyword = ref('')
const detailVisible = ref(false)
const selectedCase = ref<TestCase | null>(null)
const editVisible = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)

const testCases = computed(() => appStore.testCases || [])
const caseSets = computed(() => appStore.caseSets || [])

const handleTabChange = (name: string) => {
  if (name === 'sets') {
    document.querySelector('.page-tabs .el-tabs__item')?.scrollIntoView({ behavior: 'smooth' })
  }
}

const getCasesInSet = (s: CaseSet) => {
  return testCases.value.filter(tc => s.caseIds.includes(tc.id))
}

const modules = computed(() => {
  const set = new Set(testCases.value.map(c => c.module))
  return Array.from(set)
})

const filteredCases = ref<TestCase[]>([])

const currentPage = ref(1)
const pageSize = 10
const pagedCases = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredCases.value.slice(start, start + pageSize)
})

const handleSearch = () => {
  currentPage.value = 1
  let result = testCases.value
  if (moduleFilter.value) result = result.filter(c => c.module === moduleFilter.value)
  if (priorityFilter.value) result = result.filter(c => c.priority === priorityFilter.value)
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(c =>
      c.name.toLowerCase().includes(kw) ||
      c.caseId.toLowerCase().includes(kw)
    )
  }
  filteredCases.value = result
}

const caseStats = computed(() => [
  { key: 'total', icon: Document, bg: 'linear-gradient(135deg, #4facfe, #00f2fe)', count: testCases.value.length, label: '总用例' },
  { key: 'L0', icon: Warning, bg: 'linear-gradient(135deg, #f093fb, #f5576c)', count: testCases.value.filter(c => c.priority === 'L0').length, label: 'L0 优先级' },
  { key: 'L1', icon: Warning, bg: 'linear-gradient(135deg, #ff9a9e, #fecfef)', count: testCases.value.filter(c => c.priority === 'L1').length, label: 'L1 优先级' },
  { key: 'L2', icon: CircleCheck, bg: 'linear-gradient(135deg, #11998e, #38ef7d)', count: testCases.value.filter(c => c.priority === 'L2').length, label: 'L2 优先级' },
  { key: 'L3', icon: InfoFilled, bg: 'linear-gradient(135deg, #a1c4fd, #c2e9fb)', count: testCases.value.filter(c => c.priority === 'L3').length, label: 'L3 优先级' },
  { key: 'L4', icon: InfoFilled, bg: 'linear-gradient(135deg, #bdc3c7, #2c3e50)', count: testCases.value.filter(c => c.priority === 'L4').length, label: 'L4 优先级' }
])

const priorityType = (p: string) => {
  const map: Record<string, string> = { L0: 'danger', L1: '', L2: 'warning', L3: '', L4: 'info' }
  return map[p] || 'info'
}

const priorityText = (p: string) => {
  const map: Record<string, string> = {
    'L0': 'L0', 'l0': 'L0', 'P0': 'L0', 'p0': 'L0',
    '高': 'L0', 'high': 'L0', 'High': 'L0', 'H': 'L0',
    'L1': 'L1', 'l1': 'L1', 'P1': 'L1', 'p1': 'L1',
    'L2': 'L2', 'l2': 'L2', 'P2': 'L2', 'p2': 'L2',
    '中': 'L2', 'medium': 'L2', 'Medium': 'L2', 'M': 'L2',
    'L3': 'L3', 'l3': 'L3', 'P3': 'L3', 'p3': 'L3',
    'L4': 'L4', 'l4': 'L4', 'P4': 'L4', 'p4': 'L4',
    '低': 'L4', 'low': 'L4', 'Low': 'L4', 'L': 'L4'
  }
  return map[p] || p
}

// ==================== 导入用例 ====================

const importVisible = ref(false)
const importing = ref(false)
const parseError = ref('')
const fileInputRef = ref<HTMLInputElement>()

interface ImportRow {
  name: string
  module: string
  priority: 'L0' | 'L1' | 'L2' | 'L3' | 'L4'
  steps: string
  expected: string
  creator: string
}

const importData = ref<{ file: File | null; rows: ImportRow[] }>({
  file: null,
  rows: []
})

const showImportDialog = () => {
  parseError.value = ''
  importData.value = { file: null, rows: [] }
  importVisible.value = true
}

const triggerUpload = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  parseError.value = ''
  importData.value.file = file
  parseExcel(file)
  // Reset input so re-selecting same file triggers change
  target.value = ''
}

const clearImport = () => {
  importData.value = { file: null, rows: [] }
  parseError.value = ''
}

const parseExcel = (file: File) => {
  const reader = new FileReader()
  reader.onload = (evt) => {
    try {
      const data = new Uint8Array(evt.target!.result as ArrayBuffer)
      const workbook = XLSX.read(data, { type: 'array' })
      const sheet = workbook.Sheets[workbook.SheetNames[0]]
      if (!sheet) {
        parseError.value = 'Excel 文件中没有找到工作表'
        return
      }
      const raw: Record<string, string>[] = XLSX.utils.sheet_to_json(sheet, { defval: '' })
      if (raw.length === 0) {
        parseError.value = 'Excel 文件为空，没有解析到数据'
        return
      }
      const rows: ImportRow[] = raw.map((r) => ({
        name: String(r['用例名称'] || r['name'] || r['Name'] || '').trim(),
        module: String(r['模块'] || r['module'] || r['Module'] || '').trim(),
        priority: normalizePriority(String(r['优先级'] || r['priority'] || r['Priority'] || '').trim()),
        steps: String(r['步骤'] || r['steps'] || r['Steps'] || '').trim(),
        expected: String(r['预期结果'] || r['expected'] || r['Expected'] || '').trim(),
        creator: String(r['责任人'] || r['创建人'] || r['creator'] || r['Creator'] || '导入用户').trim()
      }))
      const validRows = rows.filter(r => r.name !== '')
      if (validRows.length === 0) {
        parseError.value = '未能解析到有效用例数据，请检查表头是否包含"用例名称"或"name"列'
        return
      }
      if (validRows.length < rows.length) {
        ElMessage.warning(`${rows.length - validRows.length} 行用例名称为空已跳过`)
      }
      importData.value.rows = validRows
    } catch (err) {
      parseError.value = '文件解析失败：' + (err as Error).message
    }
  }
  reader.onerror = () => {
    parseError.value = '文件读取失败'
  }
  reader.readAsArrayBuffer(file)
}

const normalizePriority = (val: string): 'L0' | 'L1' | 'L2' | 'L3' | 'L4' => {
  const map: Record<string, 'L0' | 'L1' | 'L2' | 'L3' | 'L4'> = {
    'L0': 'L0', 'l0': 'L0', 'P0': 'L0', 'p0': 'L0',
    '高': 'L0', 'high': 'L0', 'High': 'L0', 'H': 'L0',
    'L1': 'L1', 'l1': 'L1', 'P1': 'L1', 'p1': 'L1',
    'L2': 'L2', 'l2': 'L2', 'P2': 'L2', 'p2': 'L2',
    '中': 'L2', 'medium': 'L2', 'Medium': 'L2', 'M': 'L2',
    'L3': 'L3', 'l3': 'L3', 'P3': 'L3', 'p3': 'L3',
    'L4': 'L4', 'l4': 'L4', 'P4': 'L4', 'p4': 'L4',
    '低': 'L4', 'low': 'L4', 'Low': 'L4', 'L': 'L4'
  }
  return map[val] || 'L2'
}

const confirmImport = async () => {
  if (importData.value.rows.length === 0) return
  importing.value = true
  try {
    const now = new Date().toISOString()
    const maxId = Math.max(0, ...appStore.testCases.map(c => c.id))
    const newCases: TestCase[] = importData.value.rows.map((r, idx) => ({
      id: maxId + 1 + idx,
      caseId: r.name.slice(0, 2).toUpperCase() + '-' + String(Date.now() + idx).slice(-4),
      name: r.name,
      module: r.module || '未分类',
      priority: r.priority,
      steps: r.steps || '',
      expected: r.expected || '',
      creator: r.creator || '导入用户',
      createdAt: now
    }))
    appStore.testCases.push(...newCases)
    ElMessage.success(`成功导入 ${newCases.length} 条用例`)
    importVisible.value = false
  } catch (err) {
    ElMessage.error('导入失败：' + (err as Error).message)
  } finally {
    importing.value = false
  }
}

const formatTime = (t: string) => {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

const form = ref({
  name: '',
  caseId: '',
  module: '',
  priority: 'L2' as 'L0' | 'L1' | 'L2' | 'L3' | 'L4',
  steps: '',
  expected: ''
})

const showDetail = (c: TestCase) => {
  selectedCase.value = c
  detailVisible.value = true
}

const showAddDialog = () => {
  isEditing.value = false
  editingId.value = null
  form.value = {
    name: '',
    caseId: `TC-${String(Date.now()).slice(-4)}`,
    module: '',
    priority: 'L2',
    steps: '',
    expected: ''
  }
  editVisible.value = true
}

const editCase = (c: TestCase) => {
  isEditing.value = true
  editingId.value = c.id
  form.value = {
    name: c.name,
    caseId: c.caseId,
    module: c.module,
    priority: c.priority,
    steps: c.steps,
    expected: c.expected
  }
  editVisible.value = true
}

const saveCase = () => {
  if (!form.value.name.trim()) {
    ElMessage.warning('请输入用例名称')
    return
  }
  if (isEditing.value && editingId.value !== null) {
    const idx = appStore.testCases.findIndex(c => c.id === editingId.value)
    if (idx >= 0) {
      Object.assign(appStore.testCases[idx], form.value)
      ElMessage.success('用例已更新')
    }
  } else {
    appStore.testCases.push({
      id: Date.now(),
      caseId: form.value.caseId,
      name: form.value.name,
      module: form.value.module,
      priority: form.value.priority,
      steps: form.value.steps,
      expected: form.value.expected,
      creator: '当前用户',
      createdAt: new Date().toISOString()
    })
    ElMessage.success('用例已创建')
  }
  editVisible.value = false
}

const deleteCase = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除该用例吗？', '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
    appStore.testCases = appStore.testCases.filter(c => c.id !== id)
    ElMessage.success('用例已删除')
  } catch { /* canceled */ }
}

// ==================== 用例集 ====================

const setEditVisible = ref(false)
const isEditingSet = ref(false)
const editingSetId = ref<number | null>(null)

const setForm = ref({
  name: '',
  description: '',
  caseIds: [] as number[]
})

const showAddSetDialog = () => {
  isEditingSet.value = false
  editingSetId.value = null
  setForm.value = { name: '', description: '', caseIds: [] }
  setEditVisible.value = true
}

const editSet = (s: CaseSet) => {
  isEditingSet.value = true
  editingSetId.value = s.id
  setForm.value = {
    name: s.name,
    description: s.description,
    caseIds: [...s.caseIds]
  }
  setEditVisible.value = true
}

const saveSet = () => {
  if (!setForm.value.name.trim()) {
    ElMessage.warning('请输入用例集名称')
    return
  }
  if (isEditingSet.value && editingSetId.value !== null) {
    const idx = appStore.caseSets.findIndex(s => s.id === editingSetId.value)
    if (idx >= 0) {
      appStore.caseSets[idx] = {
        ...appStore.caseSets[idx],
        name: setForm.value.name,
        description: setForm.value.description,
        caseIds: [...setForm.value.caseIds],
        caseCount: setForm.value.caseIds.length
      }
      ElMessage.success('用例集已更新')
    }
  } else {
    appStore.caseSets.push({
      id: Date.now(),
      name: setForm.value.name,
      description: setForm.value.description,
      caseIds: [...setForm.value.caseIds],
      caseCount: setForm.value.caseIds.length,
      createdAt: new Date().toISOString()
    })
    ElMessage.success('用例集已创建')
  }
  setEditVisible.value = false
}

const deleteSet = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除该用例集吗？', '确认删除', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
    appStore.caseSets = appStore.caseSets.filter(s => s.id !== id)
    ElMessage.success('用例集已删除')
  } catch { /* canceled */ }
}

onMounted(() => {
  appStore.fetchTestCases()
  appStore.fetchCaseSets()
  handleSearch()
})
</script>

<style scoped>
.testcase-page {
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

/* ==================== 统计条 ==================== */
.stats-row {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
}

.stat-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  border-radius: 10px;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: transform 0.2s;
}

.stat-chip:hover {
  transform: translateY(-2px);
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.stat-label {
  font-size: 11px;
  opacity: 0.9;
}

/* ==================== 表格 ==================== */
.table-container {
  flex: 1;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

:deep(.case-table) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.case-table .el-table__header th) {
  background: #f5f7fa;
  color: #606266;
  font-weight: 600;
  font-size: 13px;
  padding: 10px 0;
}

:deep(.case-table .el-table__row) {
  transition: background 0.2s;
  cursor: pointer;
}

:deep(.case-table .el-table__row:hover) {
  background: #f0f7ff !important;
}

:deep(.case-table .el-table__cell) {
  padding: 8px 0;
}

.case-info-cell {
  padding: 4px 0;
}

.case-id {
  font-size: 12px;
  color: #909399;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  margin-bottom: 2px;
}

.case-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.module-cell {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: #606266;
}

.creator-cell {
  display: flex;
  align-items: center;
}

.time-cell {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
}

/* ==================== 空状态 ==================== */
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

/* ==================== 详情弹窗 ==================== */
:deep(.case-dialog .el-dialog__header) {
  padding: 16px 20px;
  margin: 0;
  border-bottom: 1px solid #ebeef5;
}

:deep(.case-dialog .el-dialog__body) {
  padding: 20px;
}

.detail-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-summary {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px;
  background: linear-gradient(135deg, #f5f7fa, #eef1f6);
  border-radius: 10px;
}

.ds-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
}

.ds-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  font-size: 13px;
  color: #909399;
}

.ds-divider {
  color: #dcdfe6;
}

.detail-sections {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-block {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px 14px;
}

.section-label {
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
}

.section-content {
  font-size: 13px;
  color: #303133;
  line-height: 1.6;
  white-space: pre-wrap;
}

/* ==================== 用例集 ==================== */
.sets-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.sets-count {
  font-size: 13px;
  color: #909399;
}

.sets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 14px;
}

.set-card {
  background: #fff;
  border-radius: 12px;
  padding: 18px 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: box-shadow 0.2s;
}

.set-card:hover {
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.set-card-top {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.set-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #ecf5ff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.set-info {
  flex: 1;
  min-width: 0;
}

.set-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.set-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.set-actions {
  flex-shrink: 0;
  display: flex;
  gap: 2px;
}

.set-card-bottom {
  display: flex;
  align-items: center;
  gap: 10px;
}

.set-time {
  font-size: 12px;
  color: #c0c4cc;
}

.set-cases {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.set-case-tag {
  font-size: 11px;
  background: #f0f7ff;
  color: #409eff;
  padding: 2px 8px;
  border-radius: 4px;
}

.set-case-more {
  font-size: 11px;
  color: #c0c4cc;
  line-height: 22px;
}

.sets-empty {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

/* 页面标签 */
.page-tabs {
  background: #fff;
  border-radius: 12px;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

/* ==================== 响应式 ==================== */
@media (max-width: 1000px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 800px) {
  .page-header {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  .header-right {
    flex-wrap: wrap;
  }
}
/* ==================== 分页 ==================== */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 12px 0 4px;
}

/* ==================== 导入区域 ==================== */
.import-body {
  min-height: 160px;
}

.import-upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px dashed #dcdfe6;
  border-radius: 12px;
  padding: 40px 20px;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.import-upload-area:hover {
  border-color: #409eff;
  background: rgba(64,158,255,0.04);
}

.import-upload-hint {
  margin-top: 12px;
  font-size: 15px;
  color: #303133;
}

.import-upload-desc {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
}

.import-file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding: 8px 12px;
  background: #f0f9eb;
  border-radius: 8px;
}

.import-file-name {
  font-size: 14px;
  color: #67c23a;
  flex: 1;
}

.import-error {
  margin-bottom: 12px;
  padding: 8px 12px;
  background: #fef0f0;
  border-radius: 8px;
  color: #f56c6c;
  font-size: 13px;
}

.import-summary {
  margin-top: 10px;
  font-size: 13px;
  color: #909399;
  text-align: right;
}

.cell-preview {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
  display: inline-block;
}
</style>
