<template>
  <div class="flex min-h-screen bg-slate-50 dark:bg-[#0f1a19]">
    <AppSidebar />
    <div class="flex-1 flex flex-col min-w-0">
      <AppHeader :title="headerTitle" />
      <main class="flex-1 flex items-center justify-center">
        <div class="text-center" style="animation: fade-up 280ms var(--ease-out) both">
          <div class="w-12 h-12 rounded-xl bg-slate-200 dark:bg-slate-800 flex items-center justify-center mx-auto mb-4">
            <svg class="w-6 h-6 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" :d="iconPath" />
            </svg>
          </div>
          <p class="text-slate-900 dark:text-white font-medium mb-1">{{ heading }}</p>
          <p class="text-slate-500 text-sm">{{ description }}</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'

defineProps({
  headerTitle: String,
  heading: String,
  description: String,
  iconPath: String,
})
</script>
