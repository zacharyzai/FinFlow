import { defineStore } from 'pinia'
import { ref } from 'vue'
import { analyticsApi, budgetApi, healthScoreApi, apiErrorMessage } from '@/services/api'

const pad = n => String(n).padStart(2, '0')
const todayStr = () => {
  const d = new Date()
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

export const useDashboardStore = defineStore('dashboard', () => {
  const loading = ref(false)
  const error = ref(null)

  // Raw API responses
  const budget = ref(null)                          // /budget/daily
  const categories = ref({ categories: [], total_spent: 0 }) // /analytics/categories
  const monthlyTrend = ref([])                      // /analytics/spending-over-time
  const anomalies = ref([])                         // /analytics/anomalies
  const upcoming = ref([])                          // /budget/upcoming
  const selectedMonth = ref(null)                  // 'YYYY-MM' being viewed in the category breakdown; null = current month
  const healthScore = ref(null)                     // /health-score (slow: calls Claude)

  async function load() {
    loading.value = true
    error.value = null
    selectedMonth.value = null

    const now = new Date()
    const today = todayStr()
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
      error.value = apiErrorMessage(e)
    } finally {
      loading.value = false
    }

    // Health score runs separately — it calls Claude and can take 2-3s
    // ponytail: fire-and-forget so it doesn't block the main dashboard load
    healthScoreApi.get()
      .then(res => { healthScore.value = res.data })
      .catch(() => {})
  }

  // Re-fetch the category breakdown for a past month. monthEnd = a trend data_point's date (last day of month).
  async function selectMonth(monthEnd) {
    const ym = monthEnd.slice(0, 7)
    const today = todayStr()
    selectedMonth.value = ym
    try {
      const res = await analyticsApi.categories({
        date_from: `${ym}-01`,
        date_to: monthEnd < today ? monthEnd : today,
      })
      if (selectedMonth.value === ym) categories.value = res.data // ignore stale response if user clicked another bar
    } catch (e) {
      error.value = apiErrorMessage(e)
    }
  }

  return { selectedMonth, selectMonth, loading, error, budget, categories, monthlyTrend, anomalies, upcoming, healthScore, load }
})
