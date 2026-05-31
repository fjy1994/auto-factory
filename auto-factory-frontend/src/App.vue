<template>
  <el-container class="app-container">
    <!-- 侧边栏 -->
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <h2>🏭 自动化工厂</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="menu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataLine /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/device">
          <el-icon><Monitor /></el-icon>
          <span>设备管理</span>
        </el-menu-item>
        <el-menu-item index="/flash">
          <el-icon><Opportunity /></el-icon>
          <span>刷机管理</span>
        </el-menu-item>
        <el-menu-item index="/version-track">
          <el-icon><Collection /></el-icon>
          <span>版本跟踪</span>
        </el-menu-item>
        <el-menu-item index="/branch">
          <el-icon><Guide /></el-icon>
          <span>分支管理</span>
        </el-menu-item>
        <el-menu-item index="/task">
          <el-icon><Document /></el-icon>
          <span>任务中心</span>
        </el-menu-item>
        <el-menu-item index="/testcase">
          <el-icon><Grid /></el-icon>
          <span>用例管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="main-container">
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPageName }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-badge :value="3" class="item">
            <el-button :icon="Bell" circle />
          </el-badge>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { DataLine, Monitor, Guide, Document, Bell, Grid, Opportunity, Collection } from '@element-plus/icons-vue'

const route = useRoute()

const activeMenu = computed(() => route.path)

const currentPageName = computed(() => {
  const pathMap: Record<string, string> = {
    '/dashboard': '仪表盘',
    '/device': '设备管理',
    '/flash': '刷机管理',
    '/version-track': '版本跟踪',
    '/branch': '分支管理',
    '/task': '任务中心',
    '/testcase': '用例管理',
  }
  return pathMap[route.path] || ''
})
</script>

<style scoped>
.app-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  border-bottom: 1px solid #1f2d3d;
}

.logo h2 {
  font-size: 18px;
  margin: 0;
}

.menu {
  border: none;
  flex: 1;
}

.main-container {
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.main-content {
  background-color: #f0f2f5;
  overflow-y: auto;
  padding: 20px;
}

</style>
