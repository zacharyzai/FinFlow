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

export default api

export const transactionApi = {
  create(data) {
    return api.post('/transactions', data)
  },
  update(id, data) {
    return api.patch(`/transactions/${id}`, data)
  },
}
