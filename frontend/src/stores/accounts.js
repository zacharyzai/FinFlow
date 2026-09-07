import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '@/services/supabase'
import { useAuthStore } from './auth'

const PALETTE = ['var(--brand)', 'var(--sage)', 'var(--good)', 'var(--warn)']

export const useAccountsStore = defineStore('accounts', () => {
  const accounts = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetch() {
    const auth = useAuthStore()
    if (!auth.user) return

    loading.value = true
    error.value = null

    const [{ data: accts, error: acctErr }, { data: txs, error: txErr }] = await Promise.all([
      supabase.from('accounts').select('*').eq('user_id', auth.user.id),
      supabase.from('transactions').select('account_id, withdrawal, credit, balance, date')
        .eq('user_id', auth.user.id).order('date', { ascending: true }),
    ])

    loading.value = false

    if (acctErr || txErr) {
      error.value = (acctErr ?? txErr).message
      return
    }

    // Balance = latest known running balance from the statement if we have one,
    // else the net of credits/withdrawals we've recorded (no opening balance available).
    accounts.value = accts.map((acc, i) => {
      const accTxs = txs.filter(t => t.account_id === acc.id)
      const withRunningBalance = accTxs.filter(t => t.balance != null)
      const balance = withRunningBalance.length
        ? withRunningBalance[withRunningBalance.length - 1].balance
        : accTxs.reduce((sum, t) => sum + (t.credit || 0) - (t.withdrawal || 0), 0)

      return { ...acc, balance, color: PALETTE[i % PALETTE.length] }
    })
  }

  return { accounts, loading, error, fetch }
})
