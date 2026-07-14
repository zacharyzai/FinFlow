<template>
  <div class="flex min-h-screen bg-slate-50 dark:bg-[#0f1a19]">
    <AppSidebar />
    <div class="flex-1 flex flex-col min-w-0">
      <AppHeader title="Budget" />
      <main class="flex-1 p-6 max-w-3xl mx-auto w-full">

        <!-- Daily budget card -->
        <div v-if="loading" class="rounded-2xl border border-slate-200 dark:border-white/5 bg-white dark:bg-[#1a2e2b] p-6 mb-6 animate-pulse">
          <div class="h-3 bg-slate-200 dark:bg-slate-700 rounded w-32 mb-3" />
          <div class="h-10 bg-slate-200 dark:bg-slate-700 rounded w-48 mb-4" />
          <div class="grid grid-cols-2 gap-3">
            <div v-for="i in 4" :key="i" class="h-14 bg-slate-100 dark:bg-slate-800 rounded-xl" />
          </div>
        </div>

        <div v-else-if="budget" class="rounded-2xl border border-slate-200 dark:border-white/5 bg-white dark:bg-[#1a2e2b] p-6 mb-6">
          <div class="text-sm text-[var(--text-3)] mb-1">Safe daily budget</div>
          <div class="text-4xl font-bold text-[var(--good)] mb-5">
            ${{ budget.daily_budget.toFixed(2) }}
          </div>
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div class="bg-slate-50 dark:bg-[#234a44] rounded-xl p-3">
              <div class="text-[var(--text-3)]">Monthly income</div>
              <div class="font-semibold text-[var(--text)] mt-0.5">${{ budget.breakdown.income.toFixed(2) }}</div>
            </div>
            <div class="bg-slate-50 dark:bg-[#234a44] rounded-xl p-3">
              <div class="text-[var(--text-3)]">Fixed bills</div>
              <div class="font-semibold text-[var(--bad)] mt-0.5">-${{ budget.breakdown.fixed_bills.toFixed(2) }}</div>
            </div>
            <div class="bg-slate-50 dark:bg-[#234a44] rounded-xl p-3">
              <div class="text-[var(--text-3)]">Planned expenses</div>
              <div class="font-semibold text-[var(--warn)] mt-0.5">-${{ budget.breakdown.planned_expenses.toFixed(2) }}</div>
            </div>
            <div class="bg-slate-50 dark:bg-[#234a44] rounded-xl p-3">
              <div class="text-[var(--text-3)]">Days remaining</div>
              <div class="font-semibold text-[var(--text)] mt-0.5">{{ budget.breakdown.days_remaining }}</div>
            </div>
          </div>
        </div>

        <p v-else-if="error" class="text-[var(--bad)] text-sm mb-6">{{ error }}</p>

        <!-- Planned expenses -->
        <div class="rounded-2xl border border-slate-200 dark:border-white/5 bg-white dark:bg-[#1a2e2b] p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="font-semibold text-[var(--text)]">Planned this month</h2>
            <button @click="showForm = !showForm"
                    class="text-sm px-3 py-1.5 rounded-full bg-[var(--brand)] text-white hover:bg-[var(--brand-strong)] transition-colors cursor-pointer">
              + Add
            </button>
          </div>

          <form v-if="showForm" @submit.prevent="addExpense"
                class="mb-4 p-4 rounded-xl bg-slate-50 dark:bg-[#234a44] grid grid-cols-2 gap-3 text-sm">
            <input v-model="form.name" placeholder="Name" required
                   class="col-span-2 px-3 py-2 rounded-lg border border-slate-200 dark:border-white/10 bg-white dark:bg-[#1a2e2b] text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-[var(--brand)]" />
            <input v-model.number="form.amount" type="number" step="0.01" min="0.01" placeholder="Amount ($)" required
                   class="px-3 py-2 rounded-lg border border-slate-200 dark:border-white/10 bg-white dark:bg-[#1a2e2b] text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-[var(--brand)]" />
            <input v-model="form.due_date" type="date" required
                   class="px-3 py-2 rounded-lg border border-slate-200 dark:border-white/10 bg-white dark:bg-[#1a2e2b] text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-[var(--brand)]" />
            <select v-model="form.category" required
                    class="col-span-2 px-3 py-2 rounded-lg border border-slate-200 dark:border-white/10 bg-white dark:bg-[#1a2e2b] text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-[var(--brand)]">
              <option v-for="cat in CATEGORIES" :key="cat" :value="cat">{{ cat }}</option>
            </select>
            <p v-if="formError" class="col-span-2 text-[var(--bad)] text-xs">{{ formError }}</p>
            <div class="col-span-2 flex gap-2 justify-end">
              <button type="button" @click="showForm = false"
                      class="px-3 py-1.5 text-[var(--text-2)] hover:text-[var(--text)] cursor-pointer">Cancel</button>
              <button type="submit" :disabled="saving"
                      class="px-4 py-1.5 rounded-full bg-[var(--brand)] text-white text-sm hover:bg-[var(--brand-strong)] disabled:opacity-50 cursor-pointer transition-colors">
                {{ saving ? 'Saving…' : 'Save' }}
              </button>
            </div>
          </form>

          <p v-if="upcoming.length === 0 && !showForm" class="text-sm text-[var(--text-3)] py-4 text-center">
            No planned expenses this month.
          </p>
          <ul class="divide-y divide-slate-100 dark:divide-white/5">
            <li v-for="exp in upcoming" :key="exp.id" class="flex items-center justify-between py-3 text-sm">
              <div>
                <div class="font-medium text-[var(--text)]">{{ exp.name }}</div>
                <div class="text-[var(--text-3)] text-xs mt-0.5">{{ exp.category }} · due {{ exp.due_date }}</div>
              </div>
              <div class="flex items-center gap-3">
                <span class="font-semibold text-[var(--text)]">${{ Number(exp.amount).toFixed(2) }}</span>
                <button @click="deleteExpense(exp.id)"
                        class="text-[var(--text-3)] hover:text-[var(--bad)] transition-colors cursor-pointer text-xs">✕</button>
              </div>
            </li>
          </ul>
        </div>

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'
import { budgetApi } from '@/services/api'

const CATEGORIES = ['Bills & Utilities', 'Food & Dining', 'Transport', 'Shopping', 'Healthcare', 'Entertainment', 'Travel', 'Education', 'Other']

const loading = ref(true)
const error = ref(null)
const budget = ref(null)
const upcoming = ref([])
const showForm = ref(false)
const saving = ref(false)
const formError = ref(null)
const form = ref({ name: '', amount: '', due_date: '', category: 'Bills & Utilities' })

async function load() {
  loading.value = true
  error.value = null
  try {
    const [b, u] = await Promise.all([budgetApi.daily(), budgetApi.upcoming()])
    budget.value = b.data
    upcoming.value = u.data.expenses
  } catch (e) {
    error.value = e?.response?.data?.detail ?? e.message
  } finally {
    loading.value = false
  }
}

async function addExpense() {
  saving.value = true
  formError.value = null
  try {
    await budgetApi.addExpense(form.value)
    form.value = { name: '', amount: '', due_date: '', category: 'Bills & Utilities' }
    showForm.value = false
    await load()
  } catch (e) {
    formError.value = e?.response?.data?.detail ?? e.message
  } finally {
    saving.value = false
  }
}

async function deleteExpense(id) {
  upcoming.value = upcoming.value.filter(e => e.id !== id)
  await budgetApi.deleteExpense(id)
  const b = await budgetApi.daily()
  budget.value = b.data
}

onMounted(load)
</script>
