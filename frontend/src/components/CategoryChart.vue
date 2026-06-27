<template>
  <div>
    <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">Spending by Category</p>

    <template v-if="sortedEntries.length">
      <div v-for="[category, amount] in sortedEntries" :key="category" class="mb-3 last:mb-0">
        <div class="flex items-center justify-between mb-1">
          <span class="text-sm text-slate-700 dark:text-slate-300 font-medium">{{ category }}</span>
          <span class="text-xs text-slate-500 tabular-nums">SGD {{ amount.toFixed(2) }}</span>
        </div>
        <div class="h-1.5 bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
          <div
            class="h-full bg-[#7C9E8C] rounded-full"
            :style="{ width: mounted ? pct(amount) + '%' : '0%', transition: 'width 600ms var(--ease-out)' }"
          />
        </div>
      </div>
    </template>

    <p v-else class="text-sm text-slate-400">No spending data yet.</p>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'

const props = defineProps({
  data: { type: Object, default: () => ({}) },
})

// Trigger width transition after mount (bars animate in from 0)
const mounted = ref(false)
onMounted(() => requestAnimationFrame(() => { mounted.value = true }))

const sortedEntries = computed(() =>
  Object.entries(props.data).sort(([, a], [, b]) => b - a)
)

const max = computed(() => Math.max(...Object.values(props.data), 1))
const pct = (amount) => Math.round((amount / max.value) * 100)
</script>
