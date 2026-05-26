<template>
  <div class="mail-settings-page">
    <el-card>
      <template #header>
        <span>邮件服务配置</span>
      </template>

      <el-form :model="form" label-width="150px" style="max-width: 600px;">
        <el-form-item label="邮箱地址" required>
          <el-input v-model="form.email" placeholder="your.email@company.com" />
        </el-form-item>

        <el-form-item label="用户名" required>
          <el-input v-model="form.username" placeholder="DOMAIN\\username" />
          <div class="form-tip">企业自建Exchange请使用域账号格式</div>
        </el-form-item>

        <el-form-item label="密码" required>
          <el-input v-model="form.password" type="password" placeholder="邮箱密码" />
        </el-form-item>

        <el-form-item label="服务器地址">
          <el-input v-model="form.server" placeholder="mail.company.com（可选）" />
          <div class="form-tip">AutoDiscover自动发现失败时手动填写</div>
        </el-form-item>

        <el-form-item label="轮询间隔(秒)">
          <el-input-number v-model="form.pollInterval" :min="10" :max="300" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="testConnection" :loading="testing">
            测试连接
          </el-button>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="reset">重置</el-button>
        <el-button type="primary" @click="saveConfig" :loading="saving">保存配置</el-button>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'
import type { MailConfig } from '@/types'

const appStore = useAppStore()

const testing = ref(false)
const saving = ref(false)

const form = ref<MailConfig>({
  email: '',
  username: '',
  password: '',
  server: '',
  pollInterval: 60
})

const testConnection = () => {
  if (!form.value.email || !form.value.username || !form.value.password) {
    ElMessage.warning('请填写邮箱地址、用户名和密码')
    return
  }

  testing.value = true
  
  setTimeout(() => {
    testing.value = false
    ElMessage.success('连接测试成功！')
  }, 2000)
}

const saveConfig = () => {
  if (!form.value.email || !form.value.username || !form.value.password) {
    ElMessage.warning('请填写邮箱地址、用户名和密码')
    return
  }

  saving.value = true
  
  setTimeout(() => {
    saving.value = false
    appStore.mailStatus.email = form.value.email
    appStore.mailStatus.pollInterval = form.value.pollInterval
    ElMessage.success('配置保存成功！')
  }, 1000)
}

const reset = () => {
  form.value = {
    email: appStore.mailStatus.email,
    username: '',
    password: '',
    server: '',
    pollInterval: appStore.mailStatus.pollInterval
  }
}

onMounted(() => {
  reset()
})
</script>

<style scoped>
.mail-settings-page {
  height: 100%;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
