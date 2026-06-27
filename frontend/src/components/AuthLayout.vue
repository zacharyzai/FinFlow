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
          <div class="relative z-10 rounded-xl bg-white/5 border border-white/10 h-36 flex items-center justify-center">
            <span class="text-white/20 text-xs">Dashboard preview coming soon</span>
          </div>
        </div>
        <div class="flex flex-col justify-center w-full md:w-1/2 bg-white dark:bg-[#1a2433] p-10 transition-colors duration-300">
          <div class="max-w-xs mx-auto w-full">
            <slot />
          </div>
        </div>
      </div>

      <!-- Card layout: centred card -->
      <div v-else class="w-full max-w-sm bg-white dark:bg-[#1a2433] rounded-2xl shadow-[0_32px_80px_rgba(0,0,0,0.35)] p-10 transition-colors duration-300">
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
</script>
