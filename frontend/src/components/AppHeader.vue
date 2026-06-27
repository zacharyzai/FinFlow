<template>
  <header class="flex items-center gap-4 px-6 py-4 bg-white dark:bg-[#0f1a19] border-b border-slate-200 dark:border-white/5 shrink-0">
    <!-- Sidebar toggle — plain hamburger, sidebar state is the visual feedback -->
    <button
      @click="isOpen = !isOpen"
      class="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-white/5 hover:text-slate-700 dark:hover:text-white transition-colors duration-150 shrink-0"
      aria-label="Toggle sidebar"
    >
      <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5M3.75 17.25h16.5"/>
      </svg>
    </button>

    <h2 class="text-sm font-semibold text-slate-900 dark:text-white flex-1">{{ title }}</h2>

    <div class="flex items-center gap-3">
      <!-- Dark / light toggle -->
      <button
        @click="toggleDark()"
        class="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-white/5 hover:text-slate-700 dark:hover:text-white transition-colors duration-150"
        :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
      >
        <!-- Sun: shown in dark mode (click to go light) -->
        <svg v-if="isDark" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z"/>
        </svg>
        <!-- Moon: shown in light mode (click to go dark) -->
        <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z"/>
        </svg>
      </button>

      <span class="text-sm text-slate-500 hidden sm:block">{{ auth.user?.email }}</span>
      <button
        @click="handleSignOut"
        class="px-3 py-1.5 text-sm font-medium rounded-full border border-slate-300 dark:border-slate-700
               text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5 transition-colors duration-150"
      >
        Sign out
      </button>
    </div>
  </header>
</template>

<script setup>
import { useDark, useToggle } from '@vueuse/core'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { useSidebar } from '@/composables/useSidebar'

defineProps({ title: String })

const isDark = useDark()
const toggleDark = useToggle(isDark)
const auth = useAuthStore()
const router = useRouter()
const { isOpen } = useSidebar()

async function handleSignOut() {
  await auth.signOut()
  router.push('/login')
}
</script>
