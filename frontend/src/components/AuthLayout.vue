<template>
  <div class="min-h-screen flex flex-col bg-[#2D4A47] dark:bg-[#1e3330] transition-colors duration-300">

    <header class="flex items-center justify-between px-8 py-5">
      <div class="flex items-center gap-2">
        <img src="/images/finflow-logo.svg" alt="FinFlow" class="w-7 h-7 object-contain" />
        <span class="text-white font-bold text-lg tracking-tight">FinFlow</span>
      </div>
      <button
        @click="toggleDark"
        class="flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 hover:bg-white/20
               text-white text-sm transition duration-200"
      >
        <svg v-if="!isDark" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 12.79A9 9 0 1111.21 3a7 7 0 009.79 9.79z"/>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z"/>
        </svg>
        {{ isDark ? 'Light' : 'Dark' }}
      </button>
    </header>

    <main class="flex-1 flex items-center justify-center p-6 pb-12">

      <!-- Split layout: left panel + right slot -->
      <div v-if="panel" class="flex w-full max-w-[860px] rounded-2xl overflow-hidden shadow-[0_32px_80px_rgba(0,0,0,0.35)]">
        <div class="hidden md:flex flex-col justify-between w-1/2 bg-[#243d3a] dark:bg-[#182e2b] p-10 relative overflow-hidden">
          <div class="absolute -top-16 -right-16 w-64 h-64 rounded-full border border-white/10 pointer-events-none"></div>
          <div class="absolute -top-8 -right-8 w-40 h-40 rounded-full border border-white/10 pointer-events-none"></div>
          <div class="absolute -bottom-12 -left-12 w-52 h-52 rounded-full border border-white/10 pointer-events-none"></div>
          <div class="flex items-center gap-2 relative z-10">
            <img src="/images/finflow-logo.svg" alt="FinFlow" class="w-6 h-6 object-contain" />
            <span class="text-white font-bold text-base">FinFlow</span>
          </div>
          <div class="relative z-10">
            <h2 class="text-white text-4xl font-bold leading-snug mb-4">
              Statements in.<br/>
              <span class="text-[#7C9E8C]">Clarity out.</span>
            </h2>
            <p class="text-white/40 text-sm leading-relaxed">
              Upload your DBS, OCBC, or UOB statement and get instant spending insights — powered by AI.
            </p>
          </div>
          <div class="relative z-10 space-y-4">
            <div v-for="feat in features" :key="feat.title" class="flex items-start gap-3">
              <div class="w-8 h-8 rounded-lg bg-[#7C9E8C]/20 flex items-center justify-center shrink-0 mt-0.5">
                <svg class="w-4 h-4 text-[#7C9E8C]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" :d="feat.icon"/>
                </svg>
              </div>
              <div>
                <p class="text-white text-sm font-semibold">{{ feat.title }}</p>
                <p class="text-white/40 text-xs leading-relaxed mt-0.5">{{ feat.desc }}</p>
              </div>
            </div>
          </div>
        </div>
        <div class="flex flex-col justify-center w-full md:w-1/2 bg-white dark:bg-[#1a2433] p-10 transition-colors duration-300">
          <div class="max-w-xs mx-auto w-full" style="animation: fade-up 300ms var(--ease-out) both">
            <slot />
          </div>
        </div>
      </div>

      <!-- Card layout: centred card -->
      <div v-else class="w-full max-w-sm bg-white dark:bg-[#1a2433] rounded-2xl shadow-[0_32px_80px_rgba(0,0,0,0.35)] p-10 transition-colors duration-300"
           style="animation: fade-up 300ms var(--ease-out) both">
        <slot />
      </div>

    </main>
  </div>
</template>

<script setup>
import { useDark, useToggle } from '@vueuse/core'

defineProps({ panel: { type: Boolean, default: false } })

const isDark = useDark()
const toggleDark = useToggle(isDark)

const features = [
  {
    title: 'AI-Powered Parsing',
    desc: 'Claude reads your PDF statement and categorises every transaction instantly.',
    icon: 'M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z',
  },
  {
    title: 'Daily Budget Calculator',
    desc: 'Know exactly how much you can spend today, updated in real time.',
    icon: 'M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  {
    title: 'Bank-Grade Privacy',
    desc: 'Your raw statement is deleted the moment it\'s parsed. We store insights, not files.',
    icon: 'M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z',
  },
]
</script>
