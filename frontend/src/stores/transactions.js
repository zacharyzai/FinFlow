import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '@/services/supabase'
import { useAuthStore } from './auth'

export const useTransactionsStore = defineStore('transactions', () => {
  const transactions = ref([])
  const loading = ref(false)
  const error = ref(null)

  const byCategory = computed(() => {
    return transactions.value.reduce((acc, tx) => {
      const cat = tx.category || 'Other'
      acc[cat] = (acc[cat] || 0) + (tx.withdrawal || 0)
      return acc
    }, {})
  })

  const totalSpend = computed(() =>
    transactions.value.reduce((sum, tx) => sum + (tx.withdrawal || 0), 0)
  )

  const totalIncome = computed(() =>
    transactions.value.reduce((sum, tx) => sum + (tx.credit || 0), 0)
  )

  async function fetch() {
    const auth = useAuthStore()
    if (!auth.user) return

    loading.value = true
    error.value = null

    const { data, error: err } = await supabase
      .from('transactions')
      .select('*')
      .eq('user_id', auth.user.id)
      .order('date', { ascending: false })

    loading.value = false

    if (err) {
      error.value = err.message
      return
    }

    transactions.value = data
  }

  return { transactions, loading, error, byCategory, totalSpend, totalIncome, fetch }
})
