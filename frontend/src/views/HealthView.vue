<template>
  <div class="flex min-h-screen bg-slate-50 dark:bg-[#0f1a19]">
    <AppSidebar />
    <div class="flex-1 flex flex-col min-w-0">
      <AppHeader title="Health Score" />
      <main class="flex-1 p-6 flex flex-col gap-6">

        <!-- Loading -->
        <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-3 text-slate-400">
          <div class="w-8 h-8 border-2 border-[#7C9E8C] border-t-transparent rounded-full animate-spin" />
          <p class="text-sm">Calculating your score… (AI tip takes a moment)</p>
        </div>

        <template v-else-if="data">

          <!-- Score + month -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">

            <!-- Big score card -->
            <div class="bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-white/5 rounded-xl p-6 flex flex-col items-center justify-center gap-2">
              <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">{{ data.month }}</p>
              <div class="relative flex items-center justify-center w-32 h-32 mt-2">
                <!-- SVG donut gauge -->
                <svg class="w-full h-full -rotate-90" viewBox="0 0 36 36">
                  <circle cx="18" cy="18" r="15.9" fill="none" stroke="#1f2937" stroke-width="3" />
                  <circle
                    cx="18" cy="18" r="15.9" fill="none"
                    stroke="#7C9E8C" stroke-width="3"
                    stroke-dasharray="100" stroke-linecap="round"
                    :stroke-dashoffset="100 - data.score"
                    class="transition-all duration-700"
                  />
                </svg>
                <span class="absolute text-3xl font-bold text-slate-800 dark:text-white tabular-nums">
                  {{ Math.round(data.score) }}
                </span>
              </div>
              <p class="text-sm font-medium" :class="scoreLabel.color">{{ scoreLabel.text }}</p>
            </div>

            <!-- Dimensions -->
            <div class="lg:col-span-2 bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-white/5 rounded-xl p-5">
              <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Score Breakdown</p>
              <div class="space-y-4">
                <div v-for="(dim, key) in data.dimensions" :key="key">
                  <div class="flex justify-between text-sm mb-1">
                    <span
                      class="text-slate-700 dark:text-slate-300 font-medium"
                      :class="key === data.weakest_dimension ? 'text-amber-400' : ''"
                    >
                      {{ dim.label }}
                      <span v-if="key === data.weakest_dimension" class="text-[10px] ml-1 text-amber-400 font-normal">← weakest</span>
                    </span>
                    <span class="tabular-nums text-slate-500 dark:text-slate-400 text-xs">
                      {{ dim.score }} / {{ dim.max }}
                    </span>
                  </div>
                  <div class="h-2 bg-slate-200 dark:bg-white/10 rounded-full overflow-hidden">
                    <div
                      class="h-full rounded-full transition-all duration-700"
                      :class="key === data.weakest_dimension ? 'bg-amber-400' : 'bg-[#7C9E8C]'"
                      :style="{ width: (dim.score / dim.max * 100) + '%' }"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- AI tip -->
          <div class="bg-white dark:bg-[#1a2e2b] border border-amber-200 dark:border-amber-500/20 rounded-xl p-5">
            <p class="text-xs font-semibold text-amber-500 uppercase tracking-wider mb-2">AI Tip — Improve Your Weakest Area</p>
            <p class="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">{{ data.ai_tip }}</p>
          </div>

        </template>

        <div v-else class="text-slate-400 text-sm">Could not load health score. Make sure you've uploaded a statement first.</div>

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'
import api from '@/services/api'

const data = ref(null)
const loading = ref(true)

const scoreLabel = computed(() => {
  const s = data.value?.score ?? 0
  if (s >= 80) return { text: 'Excellent', color: 'text-[#7C9E8C]' }
  if (s >= 60) return { text: 'Good', color: 'text-blue-400' }
  if (s >= 40) return { text: 'Fair', color: 'text-amber-400' }
  return { text: 'Needs Work', color: 'text-red-400' }
})

onMounted(async () => {
  try {
    const res = await api.get('/health-score')
    data.value = res.data
  } catch (e) {
    console.error('Failed to load health score:', e)
  } finally {
    loading.value = false
  }
})
</script>
