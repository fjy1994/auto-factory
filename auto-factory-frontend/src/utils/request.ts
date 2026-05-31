import axios from 'axios'
import { ElMessage } from 'element-plus'

/**
 * 递归将对象的 snake_case 键转换为 camelCase
 */
function toCamelCase(obj: any): any {
  if (obj === null || obj === undefined) return obj
  if (Array.isArray(obj)) return obj.map(toCamelCase)
  if (typeof obj !== 'object') return obj

  const result: Record<string, any> = {}
  for (const key of Object.keys(obj)) {
    const camelKey = key.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
    result[camelKey] = toCamelCase(obj[key])
  }
  return result
}

const request = axios.create({
  baseURL: '/arkweb/',
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 自动给 URL 添加尾斜杠，避免 Django PUT/DELETE 重定向问题
    if (config.url && !config.url.startsWith('http') && !config.url.endsWith('/')) {
      const qIndex = config.url.indexOf('?')
      if (qIndex >= 0) {
        config.url = config.url.slice(0, qIndex) + '/' + config.url.slice(qIndex)
      } else {
        config.url = config.url + '/'
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    let body = response.data
    // 后端列表接口返回纯数组时，包装成 { data: [...] } 以统一格式
    if (Array.isArray(body)) {
      body = { data: body }
    }
    // 自动将后端返回的 snake_case 键转为 camelCase
    if (body && typeof body === 'object') {
      body = toCamelCase(body)
    }
    return body
  },
  (error) => {
    ElMessage.error(error.response?.data?.message || '请求失败')
    return Promise.reject(error)
  }
)

export default request
