<template>
  <div class="flex min-h-screen bg-slate-50 dark:bg-[#0f1a19]">
    <AppSidebar />
    <div class="flex-1 flex flex-col min-w-0">
      <AppHeader title="Budget Planner" />
      <main class="flex-1 p-6 flex flex-col gap-6">

        <div v-if="loading" class="text-slate-400 text-sm">Loading budget…</div>

        <template v-else>

          <!-- Daily budget + breakdown -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">

            <!-- Daily budget — hero card -->
            <div class="lg:col-span-1 bg-white dark:bg-[#1a2e2b] border border-[#7C9E8C]/30 rounded-xl p-6 flex flex-col gap-1">
              <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Daily Budget</p>
              <p class="text-4xl font-bold text-[#7C9E8C] tabular-nums mt-1">
                SGD {{ budget.daily_budget?.toFixed(2) ?? '—' }}
              </p>
              <p class="text-xs text-slate-400 mt-1">
                {{ budget.breakdown?.days_remaining }} days remaining this month
              </p>
            </div>

            <!-- Breakdown table -->
            <div class="lg:col-span-2 bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-white/5 rounded-xl p-5">
              <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">How it's calculated</p>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between text-slate-600 dark:text-slate-300">
                  <span>Monthly income</span>
                  <span class="tabular-nums text-[#7C9E8C]">+ SGD {{ budget.breakdown?.income?.toFixed(2) }}</span>
                </div>
                <div class="flex justify-between text-slate-600 dark:text-slate-300">
                  <span>Fixed bills</span>
                  <span class="tabular-nums text-red-400">− SGD {{ budget.breakdown?.fixed_bills?.toFixed(2) }}</span>
                </div>
                <div class="flex justify-between text-slate-600 dark:text-slate-300">
                  <span>Planned expenses</span>
                  <span class="tabular-nums text-red-400">− SGD {{ budget.breakdown?.planned_expenses?.toFixed(2) }}</span>
                </div>
                <div class="border-t border-slate-200 dark:border-white/10 pt-2 flex justify-between font-semibold text-slate-800 dark:text-white">
                  <span>Spendable pool</span>
                  <span class="tabular-nums">SGD {{ budget.breakdown?.available?.toFixed(2) }}</span>
                </div>
                <div class="flex justify-between text-xs text-slate-400">
                  <span>÷ {{ budget.breakdown?.days_remaining }} days remaining</span>
                  <span class="tabular-nums font-semibold text-[#7C9E8C]">= SGD {{ budget.daily_budget?.toFixed(2) }}/day</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Add expense form -->
          <div class="bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-white/5 rounded-xl p-5">
            <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-4">Add Planned Expense</h2>
            <form @submit.prevent="submitExpense" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
              <input
                v-model="form.name"
                placeholder="Expense name"
                required
                class="input-field lg:col-span-2"
              />
              <input
                v-model.number="form.amount"
                type="number" min="0.01" step="0.01"
                placeholder="Amount (SGD)"
                required
                class="input-field"
              />
              <input
                v-model="form.due_date"
                type="date"
                required
                class="input-field"
              />
              <select v-model="form.category" class="input-field">
                <option v-for="cat in CATEGORIES" :key="cat" :value="cat">{{ cat }}</option>
              </select>
              <button type="submit" :disabled="saving" class="btn-primary lg:col-span-1">
                {{ saving ? 'Adding…' : 'Add Expense' }}
              </button>
            </form>
            <p v-if="formError" class="mt-2 text-sm text-red-400">{{ formError }}</p>
          </div>

          <!-- Upcoming expenses list -->
          <div class="bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-white/5 rounded-xl p-5">
            <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-4">Upcoming This Month</h2>

            <p v-if="!upcoming.length" class="text-slate-400 text-sm">
              No upcoming expenses. Add one above.
            </p>

            <div v-else class="divide-y divide-slate-200 dark:divide-white/5">
              <div
                v-for="exp in upcoming"
                :key="exp.id"
                class="flex items-center justify-between py-3 gap-4"
              >
                <div class="flex flex-col gap-0.5 min-w-0">
                  <span class="text-sm text-slate-800 dark:text-slate-200 truncate">{{ exp.name }}</span>
                  <span class="text-xs text-slate-400">{{ exp.due_date }} · {{ exp.category }}</span>
                </div>
                <div class="flex items-center gap-3 shrink-0">
                  <span class="tabular-nums text-sm font-semibold text-slate-700 dark:text-white">
                    SGD {{ Number(exp.amount).toFixed(2) }}
                  </span>
                  <button
                    @click="deleteExpense(exp.id)"
                    class="text-slate-400 hover:text-red-400 transition-colors text-xs"
                    title="Remove"
                  >✕</button>
                </div>
              </div>
            </div>
          </div>

        </template>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'
import api from '@/services/api'

const CATEGORIES = [
  'Bills & Utilities', 'Food & Dining', 'Transport', 'Shopping',
  'Healthcare', 'Entertainment', 'Travel', 'Education', 'Other',
]

const budget = ref({})
const upcoming = ref([])
const loading = ref(true)
const saving = ref(false)
const formError = ref('')

const form = reactive({
  name: '',
  amount: null,
  due_date: '',
  category: 'Bills & Utilities',
})

async function fetchAll() {
  try {
    const [budgetRes, upcomingRes] = await Promise.all([
      api.get('/budget/daily'),
      api.get('/budget/upcoming'),
    ])
    budget.value = budgetRes.data
    upcoming.value = upcomingRes.data.expenses ?? []
  } catch (e) {
    console.error('Failed to load budget:', e)
  } finally {
    loading.value = false
  }
}

async function submitExpense() {
  formError.value = ''
  saving.value = true
  try {
    await api.post('/budget/expenses', {
      name: form.name,
      amount: form.amount,
      due_date: form.due_date,
      category: form.category,
    })
    Object.assign(form, { name: '', amount: null, due_date: '', category: 'Bills & Utilities' })
    await fetchAll()
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Failed to add expense.'
  } finally {
    saving.value = false
  }
}

async function deleteExpense(id) {
  try {
    await api.delete(`/budget/expenses/${id}`)
    upcoming.value = upcoming.value.filter(e => e.id !== id)
    // Refetch budget since removing an expense changes the daily budget number
    const res = await api.get('/budget/daily')
    budget.value = res.data
  } catch (e) {
    console.error('Failed to delete expense:', e)
  }
}

onMounted(fetchAll)
</script>

<style scoped>
@reference "../style.css";

.input-field {
  @apply bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10
         text-slate-800 dark:text-slate-200 placeholder-slate-400
         rounded-lg px-3 py-2 text-sm outline-none
         focus:ring-2 focus:ring-[#7C9E8C]/40 focus:border-[#7C9E8C] transition;
}
.btn-primary {
  @apply bg-[#7C9E8C] hover:bg-[#6a8f7c] text-white font-semibold
         rounded-lg px-4 py-2 text-sm transition-colors disabled:opacity-50;
}
</style>
