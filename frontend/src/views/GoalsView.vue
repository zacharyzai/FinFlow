<template>
  <div class="flex min-h-screen bg-slate-50 dark:bg-[#0f1a19]">
    <AppSidebar />
    <div class="flex-1 flex flex-col min-w-0">
      <AppHeader title="Savings Goals" />
      <main class="flex-1 p-6 flex flex-col gap-6">

        <!-- Add goal form -->
        <div class="bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-white/5 rounded-xl p-5">
          <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-4">New Goal</h2>
          <form @submit.prevent="submitGoal" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <input
              v-model="form.name"
              placeholder="Goal name (e.g. Emergency Fund)"
              required
              class="input-field col-span-1 lg:col-span-2"
            />
            <input
              v-model.number="form.target"
              type="number" min="1" step="0.01"
              placeholder="Target (SGD)"
              required
              class="input-field"
            />
            <input
              v-model="form.deadline"
              type="date"
              required
              class="input-field"
            />
            <input
              v-model.number="form.saved"
              type="number" min="0" step="0.01"
              placeholder="Already saved (SGD)"
              class="input-field"
            />
            <button type="submit" :disabled="saving" class="btn-primary">
              {{ saving ? 'Adding…' : 'Add Goal' }}
            </button>
          </form>
          <p v-if="formError" class="mt-2 text-sm text-red-400">{{ formError }}</p>
        </div>

        <!-- Goals list -->
        <div v-if="loading" class="text-slate-400 text-sm">Loading goals…</div>

        <p v-else-if="!goals.length" class="text-slate-500 text-sm">
          No savings goals yet. Add one above to get started.
        </p>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <div
            v-for="goal in goals"
            :key="goal.id"
            class="bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-white/5 rounded-xl p-5 flex flex-col gap-3"
          >
            <!-- Header -->
            <div class="flex items-start justify-between gap-2">
              <h3 class="font-semibold text-slate-800 dark:text-white text-sm">{{ goal.name }}</h3>
              <button
                @click="deleteGoal(goal.id)"
                class="text-slate-400 hover:text-red-400 transition-colors text-xs shrink-0"
                title="Delete goal"
              >✕</button>
            </div>

            <!-- Amount display -->
            <div class="flex items-baseline justify-between">
              <span class="text-2xl font-bold text-[#7C9E8C] tabular-nums">
                SGD {{ Number(goal.saved).toFixed(2) }}
              </span>
              <span class="text-xs text-slate-400">of SGD {{ Number(goal.target).toFixed(2) }}</span>
            </div>

            <!-- Progress bar -->
            <div class="h-2 bg-slate-200 dark:bg-white/10 rounded-full overflow-hidden">
              <div
                class="h-full bg-[#7C9E8C] rounded-full transition-all duration-500"
                :style="{ width: goal.progress_pct + '%' }"
              />
            </div>
            <div class="flex justify-between text-xs text-slate-400">
              <span>{{ goal.progress_pct }}% saved</span>
              <span>Due {{ goal.deadline }}</span>
            </div>

            <!-- Monthly required -->
            <div class="bg-slate-50 dark:bg-white/5 rounded-lg px-3 py-2 text-xs text-slate-500 dark:text-slate-400">
              Save
              <span class="text-slate-700 dark:text-slate-200 font-semibold">
                SGD {{ goal.monthly_required }}/month
              </span>
              for {{ goal.months_remaining }} month{{ goal.months_remaining !== 1 ? 's' : '' }} to reach your target
            </div>

            <!-- Update saved amount inline -->
            <div class="flex gap-2">
              <input
                v-model.number="depositAmounts[goal.id]"
                type="number" min="0" step="0.01"
                placeholder="New total saved"
                class="input-field text-xs py-1.5 flex-1"
              />
              <button @click="updateSaved(goal)" class="btn-secondary text-xs py-1.5 px-3 shrink-0">
                Update
              </button>
            </div>
          </div>
        </div>

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'
import api from '@/services/api'

const goals = ref([])
const loading = ref(true)
const saving = ref(false)
const formError = ref('')

// Tracks the "new total saved" input value per goal card
const depositAmounts = reactive({})

const form = reactive({ name: '', target: null, deadline: '', saved: 0 })

async function fetchGoals() {
  try {
    const res = await api.get('/savings')
    goals.value = res.data.goals
    goals.value.forEach(g => { depositAmounts[g.id] = Number(g.saved) })
  } catch (e) {
    console.error('Failed to load goals:', e)
  } finally {
    loading.value = false
  }
}

async function submitGoal() {
  formError.value = ''
  saving.value = true
  try {
    await api.post('/savings', {
      name: form.name,
      target: form.target,
      deadline: form.deadline,
      saved: form.saved || 0,
    })
    Object.assign(form, { name: '', target: null, deadline: '', saved: 0 })
    await fetchGoals()
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Failed to create goal.'
  } finally {
    saving.value = false
  }
}

async function updateSaved(goal) {
  const newSaved = depositAmounts[goal.id]
  if (newSaved == null || newSaved < 0) return
  try {
    await api.patch(`/savings/${goal.id}`, { saved: newSaved })
    await fetchGoals()
  } catch (e) {
    console.error('Failed to update saved amount:', e)
  }
}

async function deleteGoal(id) {
  try {
    await api.delete(`/savings/${id}`)
    goals.value = goals.value.filter(g => g.id !== id)
  } catch (e) {
    console.error('Failed to delete goal:', e)
  }
}

onMounted(fetchGoals)
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
.btn-secondary {
  @apply bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300
         font-medium rounded-lg transition-colors;
}
</style>
