import axios from 'axios'
import { supabase } from './supabase'

// In dev, '/api' goes through the Vite proxy (vite.config.js) to localhost:8000.
// In production there's no proxy, so VITE_API_URL must point at the deployed
// FastAPI backend directly (e.g. https://finflow-api.up.railway.app).
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
})

// Attach the Supabase JWT to every request
api.interceptors.request.use(async (config) => {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const statementsApi = {
  upload(file, bank) {
    const form = new FormData()
    form.append('file', file)
    form.append('bank', bank)
    return api.post('/statements/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export const analyticsApi = {
  categories: (params) => api.get('/analytics/categories', { params }),
  spendingOverTime: (params) => api.get('/analytics/spending-over-time', { params }),
  anomalies: (params) => api.get('/analytics/anomalies', { params }),
}

export const budgetApi = {
  daily: () => api.get('/budget/daily'),
  upcoming: () => api.get('/budget/upcoming'),
  addExpense: (data) => api.post('/budget/expenses', data),
  deleteExpense: (id) => api.delete(`/budget/expenses/${id}`),
}

export const savingsApi = {
  list: () => api.get('/savings'),
  create: (data) => api.post('/savings', data),
  updateSaved: (id, saved) => api.patch(`/savings/${id}`, { saved }),
  delete: (id) => api.delete(`/savings/${id}`),
}

export const healthScoreApi = {
  get: () => api.get('/health-score'),
}

export const telegramApi = {
  linkUrl: () => api.post('/telegram/link-token'),
  status: () => api.get('/telegram/status'),
  disconnect: () => api.delete('/telegram/link'),
}

export default api

export const transactionApi = {
  create(data) {
    return api.post('/transactions', data)
  },
  update(id, data) {
    return api.patch(`/transactions/${id}`, data)
  },
}

// Backend errors carry a `code` alongside the message (see app_error() in
// app/core/errors.py) so the user can tell what kind of failure this is —
// AI provider down vs bad input vs rate limited — not just a generic message.
const ERROR_LABELS = {
  invalid_input: 'Invalid input',
  not_found: 'Not found',
  auth_error: 'Authentication error',
  unprocessable_file: 'File error',
  ai_provider_error: 'AI provider error',
  rate_limited: 'Rate limited',
  server_error: 'Server error',
}

export function apiErrorMessage(e) {
  const detail = e?.response?.data?.detail
  if (detail && typeof detail === 'object') {
    const label = ERROR_LABELS[detail.code]
    return label ? `${label}: ${detail.message}` : detail.message
  }
  return detail || e?.message || 'Something went wrong'
}
