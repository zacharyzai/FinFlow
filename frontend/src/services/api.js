import axios from 'axios'
import { supabase } from './supabase'

const api = axios.create({
  baseURL: '/api',
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

export default api
