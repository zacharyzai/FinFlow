<template>
  <div class="flex min-h-screen bg-slate-50 dark:bg-[#0f1a19]">
    <AppSidebar />
    <div class="flex-1 flex flex-col min-w-0">
      <AppHeader title="Health Score" />
      <main class="flex-1 p-6 max-w-3xl mx-auto w-full">

        <!-- Loading -->
        <div v-if="loading" class="rounded-2xl border border-slate-200 dark:border-white/5 bg-white dark:bg-[#1a2e2b] p-8 text-center animate-pulse">
          <div class="h-20 w-20 bg-slate-200 dark:bg-slate-700 rounded-full mx-auto mb-4" />
          <div class="h-4 bg-slate-200 dark:bg-slate-700 rounded w-48 mx-auto mb-2" />
          <div class="h-3 bg-slate-100 dark:bg-slate-800 rounded w-32 mx-auto" />
          <p class="text-[var(--text-3)] text-xs mt-4">Analysing your finances with AI…</p>
        </div>

        <p v-else-if="error" class="text-[var(--bad)] text-sm">{{ error }}</p>

        <template v-else-if="data">
          <!-- Score card -->
          <div class="rounded-2xl border border-slate-200 dark:border-white/5 bg-white dark:bg-[#1a2e2b] p-8 mb-6 text-center">
            <div class="text-6xl font-bold mb-1" :class="scoreColor">{{ data.score }}</div>
            <div class="text-[var(--text-3)] text-sm">out of 100 · {{ data.month }}</div>
            <div class="mt-2 text-xs font-medium px-3 py-1 rounded-full inline-block"
                 :class="scoreBadgeClass">{{ scoreLabel }}</div>
          </div>

          <!-- Dimensions -->
          <div class="rounded-2xl border border-slate-200 dark:border-white/5 bg-white dark:bg-[#1a2e2b] p-6 mb-6">
            <h2 class="font-semibold text-[var(--text)] mb-4">Breakdown</h2>
            <div class="space-y-4">
              <div v-for="(dim, key) in data.dimensions" :key="key">
                <div class="flex justify-between text-sm mb-1.5">
                  <span class="text-[var(--text)]">{{ dim.label }}</span>
                  <span class="font-medium text-[var(--text)]">{{ dim.score }}<span class="text-[var(--text-3)]">/{{ dim.max }}</span></span>
                </div>
                <div class="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-700"
                       :class="key === data.weakest_dimension ? 'bg-[var(--warn)]' : 'bg-[var(--good)]'"
                       :style="`width: ${(dim.score / dim.max) * 100}%`" />
                </div>
              </div>
            </div>
          </div>

          <!-- AI tip -->
          <div class="rounded-2xl border border-[var(--warn-bd)] bg-[var(--warn-bg)] p-5">
            <div class="text-xs font-semibold text-[var(--warn)] uppercase tracking-wide mb-2">AI tip · improve {{ data.dimensions[data.weakest_dimension]?.label }}</div>
            <p class="text-sm text-[var(--text-2)] leading-relaxed">{{ data.ai_tip }}</p>
          </div>
        </template>

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'
import { healthScoreApi } from '@/services/api'

const loading = ref(true)
const error = ref(null)
const data = ref(null)

const scoreColor = computed(() => {
  if (!data.value) return ''
  const s = data.value.score
  if (s >= 75) return 'text-[var(--good)]'
  if (s >= 50) return 'text-[var(--warn)]'
  return 'text-[var(--bad)]'
})

const scoreLabel = computed(() => {
  if (!data.value) return ''
  const s = data.value.score
  if (s >= 75) return 'Healthy'
  if (s >= 50) return 'Needs attention'
  return 'At risk'
})

const scoreBadgeClass = computed(() => {
  if (!data.value) return ''
  const s = data.value.score
  if (s >= 75) return 'bg-[var(--good-bg)] text-[var(--good)]'
  if (s >= 50) return 'bg-[var(--warn-bg)] text-[var(--warn)]'
  return 'bg-[var(--bad-bg)] text-[var(--bad)]'
})

onMounted(async () => {
  try {
    const res = await healthScoreApi.get()
    data.value = res.data
  } catch (e) {
    error.value = e?.response?.data?.detail ?? e.message
  } finally {
    loading.value = false
  }
})
</script>
