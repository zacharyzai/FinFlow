import { defineStore } from 'pinia'
import { ref } from 'vue'
import { analyticsApi, budgetApi } from '@/services/api'

export const useDashboardStore = defineStore('dashboard', () => {
  const loading = ref(false)
  const error = ref(null)

  // Raw API responses
  const budget = ref(null)                          // /budget/daily
  const categories = ref({ categories: [], total_spent: 0 }) // /analytics/categories
  const monthlyTrend = ref([])                      // /analytics/spending-over-time
  const anomalies = ref([])                         // /analytics/anomalies
  const upcoming = ref([])                          // /budget/upcoming

  async function load() {
    loading.value = true
    error.value = null

    const now = new Date()
    const pad = n => String(n).padStart(2, '0')
    const today = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
    const monthStart = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-01`
    // 6-month window for bar chart
    const trendStart = new Date(now.getFullYear(), now.getMonth() - 5, 1)
    const trendFrom = `${trendStart.getFullYear()}-${pad(trendStart.getMonth() + 1)}-01`

    try {
      const [b, cats, trend, anoms, upco] = await Promise.all([
        budgetApi.daily(),
        analyticsApi.categories({ date_from: monthStart, date_to: today }),
        analyticsApi.spendingOverTime({ date_from: trendFrom, date_to: today, granularity: 'monthly' }),
        analyticsApi.anomalies({ date_from: monthStart, date_to: today }),
        budgetApi.upcoming(),
      ])
      budget.value = b.data
      categories.value = cats.data
      monthlyTrend.value = trend.data.data_points
      anomalies.value = anoms.data.anomalies
      upcoming.value = upco.data.expenses
    } catch (e) {
      error.value = e?.response?.data?.detail ?? e.message
    } finally {
      loading.value = false
    }
  }

  return { loading, error, budget, categories, monthlyTrend, anomalies, upcoming, load }
})
