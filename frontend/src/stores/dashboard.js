import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { analyticsApi, budgetApi, healthScoreApi, apiErrorMessage } from '@/services/api'

const pad = n => String(n).padStart(2, '0')
const todayStr = () => {
  const d = new Date()
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}
const currentYm = () => todayStr().slice(0, 7)
const emptyCategories = () => ({ categories: [], total_spent: 0 })

export const useDashboardStore = defineStore('dashboard', () => {
  const loading = ref(false)
  const error = ref(null)

  // Always-current data (the daily budget and upcoming bills only make sense for "today")
  const budget = ref(null)                          // /budget/daily
  const monthlyTrend = ref([])                      // /analytics/spending-over-time
  const upcoming = ref([])                          // /budget/upcoming

  // Month-scoped data, kept in two slots so switching back to the current month is instant
  // and doesn't re-run the health score (it calls Claude)
  const curCategories = ref(emptyCategories())      // /analytics/categories
  const curAnomalies = ref([])                      // /analytics/anomalies
  const curHealth = ref(null)                       // /health-score (slow: calls Claude)
  const past = ref({ categories: emptyCategories(), anomalies: [], healthScore: null })

  const selectedMonth = ref(null)                   // 'YYYY-MM' being reviewed; null = current month
  const isPastMonth = computed(() => selectedMonth.value !== null)

  // The rest of the app reads these and doesn't care which slot they come from
  const categories = computed(() => isPastMonth.value ? past.value.categories : curCategories.value)
  const anomalies = computed(() => isPastMonth.value ? past.value.anomalies : curAnomalies.value)
  const healthScore = computed(() => isPastMonth.value ? past.value.healthScore : curHealth.value)

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
      curCategories.value = cats.data
      monthlyTrend.value = trend.data.data_points
      curAnomalies.value = anoms.data.anomalies
      upcoming.value = upco.data.expenses
    } catch (e) {
      error.value = apiErrorMessage(e)
    } finally {
      loading.value = false
    }

    // Health score runs separately — it calls Claude and can take 2-3s
    // ponytail: fire-and-forget so it doesn't block the main dashboard load
    healthScoreApi.get()
      .then(res => { curHealth.value = res.data })
      .catch(() => {})
  }

  // Review a past month ('YYYY-MM'). null (or the current month) returns to the live dashboard.
  async function selectMonth(ym) {
    if (!ym || ym === currentYm()) {
      selectedMonth.value = null
      return
    }
    selectedMonth.value = ym
    past.value = { categories: emptyCategories(), anomalies: [], healthScore: null } // clear the previous month's data

    const [y, m] = ym.split('-').map(Number)
    const params = { date_from: `${ym}-01`, date_to: `${ym}-${pad(new Date(y, m, 0).getDate())}` }
    const stale = () => selectedMonth.value !== ym // user clicked another month while this was in flight

    healthScoreApi.get(ym)
      .then(res => { if (!stale()) past.value.healthScore = res.data })
      .catch(() => {})

    try {
      const [cats, anoms] = await Promise.all([
        analyticsApi.categories(params),
        analyticsApi.anomalies(params),
      ])
      if (stale()) return
      past.value.categories = cats.data
      past.value.anomalies = anoms.data.anomalies
    } catch (e) {
      if (!stale()) error.value = apiErrorMessage(e)
    }
  }

  return {
    loading, error, budget, categories, monthlyTrend, anomalies, upcoming, healthScore,
    selectedMonth, isPastMonth, selectMonth, load,
  }
})
