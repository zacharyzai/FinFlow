<template>
  <div class="flex min-h-screen bg-slate-50 dark:bg-[#0f1a19]">
    <AppSidebar />
    <div class="flex-1 flex flex-col min-w-0">
      <AppHeader title="Goals" />
      <main class="flex-1 p-6 max-w-3xl mx-auto w-full">

        <div class="flex justify-end mb-4">
          <button @click="showForm = !showForm"
                  class="px-4 py-2 rounded-full bg-[var(--brand)] hover:bg-[var(--brand-strong)] text-white text-sm font-semibold cursor-pointer transition-colors">
            + New goal
          </button>
        </div>

        <!-- Add goal form -->
        <form v-if="showForm" @submit.prevent="createGoal"
              class="mb-6 p-4 rounded-2xl border border-slate-200 dark:border-white/5 bg-white dark:bg-[#1a2e2b] grid grid-cols-2 gap-3 text-sm">
          <input v-model="form.name" placeholder="Goal name" required
                 class="col-span-2 px-3 py-2 rounded-lg border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-[#234a44] text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-[var(--brand)]" />
          <input v-model.number="form.target" type="number" step="0.01" min="0.01" placeholder="Target ($)" required
                 class="px-3 py-2 rounded-lg border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-[#234a44] text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-[var(--brand)]" />
          <input v-model.number="form.saved" type="number" step="0.01" min="0" placeholder="Already saved ($)"
                 class="px-3 py-2 rounded-lg border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-[#234a44] text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-[var(--brand)]" />
          <div class="col-span-2">
            <label class="text-[var(--text-3)] text-xs mb-1 block">Deadline</label>
            <input v-model="form.deadline" type="date" required
                   class="w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-[#234a44] text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-[var(--brand)]" />
          </div>
          <p v-if="formError" class="col-span-2 text-[var(--bad)] text-xs">{{ formError }}</p>
          <div class="col-span-2 flex gap-2 justify-end">
            <button type="button" @click="showForm = false"
                    class="px-3 py-1.5 text-[var(--text-2)] hover:text-[var(--text)] cursor-pointer">Cancel</button>
            <button type="submit" :disabled="saving"
                    class="px-4 py-1.5 rounded-full bg-[var(--brand)] text-white text-sm hover:bg-[var(--brand-strong)] disabled:opacity-50 cursor-pointer transition-colors">
              {{ saving ? 'Saving…' : 'Create' }}
            </button>
          </div>
        </form>

        <!-- Loading -->
        <div v-if="loading" class="space-y-4">
          <div v-for="i in 3" :key="i" class="rounded-2xl border border-slate-200 dark:border-white/5 bg-white dark:bg-[#1a2e2b] p-5 animate-pulse">
            <div class="h-3 bg-slate-200 dark:bg-slate-700 rounded w-40 mb-3" />
            <div class="h-2 bg-slate-100 dark:bg-slate-800 rounded-full mb-3" />
            <div class="h-3 bg-slate-200 dark:bg-slate-700 rounded w-24" />
          </div>
        </div>

        <p v-else-if="error" class="text-[var(--bad)] text-sm">{{ error }}</p>

        <p v-else-if="goals.length === 0 && !showForm" class="text-[var(--text-3)] text-sm text-center py-12">
          No savings goals yet. Add one to get started.
        </p>

        <!-- Goals list -->
        <div v-else class="space-y-4">
          <div v-for="goal in goals" :key="goal.id"
               class="rounded-2xl border border-slate-200 dark:border-white/5 bg-white dark:bg-[#1a2e2b] p-5">
            <div class="flex items-start justify-between mb-3">
              <div>
                <div class="font-semibold text-[var(--text)]">{{ goal.name }}</div>
                <div class="text-xs text-[var(--text-3)] mt-0.5">
                  Deadline: {{ goal.deadline }} · {{ goal.months_remaining }} month{{ goal.months_remaining !== 1 ? 's' : '' }} left
                </div>
              </div>
              <button @click="deleteGoal(goal.id)"
                      class="text-[var(--text-3)] hover:text-[var(--bad)] transition-colors cursor-pointer text-xs ml-4 shrink-0">✕</button>
            </div>

            <!-- Progress bar -->
            <div class="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden mb-3">
              <div class="h-full rounded-full transition-all duration-500"
                   :class="goal.progress_pct >= 100 ? 'bg-[var(--good)]' : 'bg-[var(--brand)]'"
                   :style="`width: ${Math.min(goal.progress_pct, 100)}%`" />
            </div>

            <div class="flex items-center justify-between text-sm">
              <span class="text-[var(--text-3)]">
                ${{ Number(goal.saved).toFixed(2) }} of ${{ Number(goal.target).toFixed(2) }}
                <span class="ml-1 text-[var(--brand)] font-medium">({{ goal.progress_pct }}%)</span>
              </span>
              <span class="text-[var(--text-3)] text-xs">${{ goal.monthly_required }}/mo needed</span>
            </div>

            <!-- Update saved amount -->
            <div class="mt-3 flex items-center gap-2">
              <input v-model.number="goal._newSaved" type="number" step="0.01" min="0"
                     :placeholder="`Update saved ($${Number(goal.saved).toFixed(2)})`"
                     class="flex-1 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-[#234a44] text-[var(--text)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--brand)]" />
              <button @click="updateSaved(goal)" :disabled="goal._saving"
                      class="px-3 py-1.5 rounded-full text-sm bg-[var(--brand)] text-white hover:bg-[var(--brand-strong)] disabled:opacity-50 cursor-pointer transition-colors shrink-0">
                {{ goal._saving ? '…' : 'Update' }}
              </button>
            </div>
          </div>
        </div>

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'
import { savingsApi } from '@/services/api'

const loading = ref(true)
const error = ref(null)
const goals = ref([])
const showForm = ref(false)
const saving = ref(false)
const formError = ref(null)
const form = ref({ name: '', target: '', saved: 0, deadline: '' })

async function load() {
  loading.value = true
  error.value = null
  try {
    const res = await savingsApi.list()
    // _newSaved and _saving are local UI state, not from API
    goals.value = res.data.goals.map(g => ({ ...g, _newSaved: null, _saving: false }))
  } catch (e) {
    error.value = e?.response?.data?.detail ?? e.message
  } finally {
    loading.value = false
  }
}

async function createGoal() {
  saving.value = true
  formError.value = null
  try {
    await savingsApi.create(form.value)
    form.value = { name: '', target: '', saved: 0, deadline: '' }
    showForm.value = false
    await load()
  } catch (e) {
    formError.value = e?.response?.data?.detail ?? e.message
  } finally {
    saving.value = false
  }
}

async function updateSaved(goal) {
  if (goal._newSaved === null || goal._newSaved === '') return
  goal._saving = true
  try {
    const res = await savingsApi.updateSaved(goal.id, goal._newSaved)
    const updated = res.data.goal
    Object.assign(goal, { ...updated, _newSaved: null, _saving: false })
  } catch (e) {
    goal._saving = false
  }
}

async function deleteGoal(id) {
  goals.value = goals.value.filter(g => g.id !== id)
  await savingsApi.delete(id)
}

onMounted(load)
</script>
