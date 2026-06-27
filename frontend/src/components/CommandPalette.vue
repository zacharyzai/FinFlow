<template>
  <Teleport to="body">
    <Transition name="palette">
      <div v-if="open" class="fixed inset-0 z-50 flex items-start justify-center pt-[18vh]" @mousedown.self="$emit('close')">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')" />

        <!-- Panel -->
        <div
          class="relative w-full max-w-md mx-4 bg-white dark:bg-[#1a2e2b] rounded-2xl shadow-2xl border border-slate-200 dark:border-white/10 overflow-hidden"
          style="animation: fade-up 140ms var(--ease-out) both"
        >
          <!-- Search row -->
          <div class="flex items-center gap-3 px-4 py-3.5 border-b border-slate-100 dark:border-white/5">
            <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            <input
              ref="inputRef"
              v-model="query"
              type="text"
              placeholder="Go to..."
              class="flex-1 bg-transparent text-slate-900 dark:text-white placeholder-slate-400 text-sm outline-none"
              @keydown.enter="selectActive"
              @keydown.up.prevent="move(-1)"
              @keydown.down.prevent="move(1)"
              @keydown.escape="$emit('close')"
            />
            <kbd class="text-[11px] text-slate-400 bg-slate-100 dark:bg-white/5 px-1.5 py-0.5 rounded font-mono leading-none">esc</kbd>
          </div>

          <!-- Results -->
          <ul class="py-1.5 max-h-72 overflow-y-auto" v-if="results.length">
            <li
              v-for="(item, i) in results"
              :key="item.to"
              @click="navigate(item)"
              @mouseenter="active = i"
              class="flex items-center gap-3 px-4 py-2.5 cursor-pointer text-sm transition-colors duration-100 mx-1.5 rounded-lg"
              :class="i === active
                ? 'bg-[#7C9E8C]/15 text-[#7C9E8C]'
                : 'text-slate-700 dark:text-slate-300'"
            >
              <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" v-html="item.icon" />
              {{ item.label }}
            </li>
          </ul>
          <p v-else class="px-4 py-8 text-sm text-slate-400 text-center">No results for "{{ query }}"</p>

          <!-- Footer hint -->
          <div class="px-4 py-2 border-t border-slate-100 dark:border-white/5 flex items-center gap-3 text-[11px] text-slate-400">
            <span><kbd class="font-mono">↑↓</kbd> navigate</span>
            <span><kbd class="font-mono">↵</kbd> open</span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({ open: Boolean })
const emit = defineEmits(['close'])

const router = useRouter()
const query = ref('')
const active = ref(0)
const inputRef = ref(null)

const COMMANDS = [
  {
    label: 'Dashboard',
    to: '/dashboard',
    icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"/>',
  },
  {
    label: 'Transactions',
    to: '/transactions',
    icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M8.25 6.75h12M8.25 12h12m-12 5.25h12M3.75 6.75h.007v.008H3.75V6.75zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zM3.75 12h.007v.008H3.75V12zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm-.375 5.25h.007v.008H3.75v-.008zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z"/>',
  },
  {
    label: 'Upload Statement',
    to: '/upload',
    icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/>',
  },
  {
    label: 'Budget',
    to: '/budget',
    icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75"/>',
  },
  {
    label: 'Health Score',
    to: '/health',
    icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"/>',
  },
  {
    label: 'Goals',
    to: '/goals',
    icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M3 3v1.5M3 21v-6m0 0l2.77-.693a9 9 0 016.208.682l.108.054a9 9 0 006.086.71l3.114-.732a48.524 48.524 0 01-.005-10.499l-3.11.732a9 9 0 01-6.085-.711l-.108-.054a9 9 0 00-6.208-.682L3 4.5M3 15V4.5"/>',
  },
]

const results = computed(() => {
  if (!query.value.trim()) return COMMANDS
  const q = query.value.toLowerCase()
  return COMMANDS.filter(c => c.label.toLowerCase().includes(q))
})

watch(results, () => { active.value = 0 })

// Auto-focus input when palette opens
watch(() => props.open, (val) => {
  if (val) {
    query.value = ''
    active.value = 0
    nextTick(() => inputRef.value?.focus())
  }
})

function move(dir) {
  active.value = (active.value + dir + results.value.length) % results.value.length
}

function navigate(item) {
  router.push(item.to)
  emit('close')
}

function selectActive() {
  if (results.value[active.value]) navigate(results.value[active.value])
}
</script>

<style scoped>
.palette-enter-active { transition: opacity 150ms var(--ease-out); }
.palette-leave-active { transition: opacity 100ms var(--ease-out); }
.palette-enter-from, .palette-leave-to { opacity: 0; }
</style>
