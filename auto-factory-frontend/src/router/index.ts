import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard/index.vue')
  },
  {
    path: '/device',
    name: 'Device',
    component: () => import('@/views/Device/index.vue')
  },
  {
    path: '/branch',
    name: 'Branch',
    component: () => import('@/views/Branch/index.vue')
  },
  {
    path: '/flash',
    name: 'Flashing',
    component: () => import('@/views/Flashing/index.vue')
  },
  {
    path: '/version-track',
    name: 'VersionTrack',
    component: () => import('@/views/VersionTrack/index.vue')
  },
  {
    path: '/task',
    name: 'TaskCenter',
    component: () => import('@/views/Task/index.vue')
  },
  {
    path: '/testcase',
    name: 'TestCase',
    component: () => import('@/views/TestCase/index.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
