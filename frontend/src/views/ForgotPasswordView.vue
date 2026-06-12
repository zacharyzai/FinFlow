<template>
    <div class="min-h-screen flex flex-col bg-[#2D4A47] dark:bg-[#1e3330] transition-colors duration-300">
  
      <!-- TOP BAR -->
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
          <!-- moon icon -->
          <svg v-if="!isDark" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 12.79A9 9 0 1111.21 3a7 7 0 009.79 9.79z"/>
          </svg>
          <!-- sun icon -->
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z"/>
          </svg>
          {{ isDark ? 'Light' : 'Dark' }}
        </button>
      </header>
  
      <main class="flex-1 flex items-center justify-center p-6 pb-12">
        <div class="flex w-full max-w-[860px] rounded-2xl overflow-hidden shadow-[0_32px_80px_rgba(0,0,0,0.35)]">
  
          <!-- LEFT PANEL -->
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
  
          <!-- RIGHT PANEL -->
          <div class="flex flex-col justify-center w-full md:w-1/2 bg-white dark:bg-[#1a2433] p-10 transition-colors duration-300">
            <div class="max-w-xs mx-auto w-full">
  
              <div class="flex justify-center mb-5">
                <img src="/images/finflow-logo.svg" alt="FinFlow" class="w-14 h-14 object-contain" />
              </div>
  
              <h1 class="text-2xl font-bold text-center text-zinc-900 dark:text-white mb-1">
                Reset your password
              </h1>
              <p class="text-center text-sm text-zinc-400 dark:text-zinc-500 mb-7">
                Enter your email and we'll send you a reset link.
              </p>
  
              <!-- Success state — shown after submission -->
              <div
                v-if="submitted"
                class="text-center text-sm text-[#7C9E8C] bg-green-50 dark:bg-green-950/40
                       border border-green-200 dark:border-green-900 rounded-xl px-4 py-4 mb-5"
              >
                If that email is registered, you'll receive a reset link shortly.
              </div>
  
              <form v-else @submit.prevent="handleSubmit" class="space-y-3">
  
                <!-- Email input -->
                <div class="relative">
                  <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400 pointer-events-none"
                       xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                  </svg>
                  <input
                    v-model="email"
                    type="email"
                    placeholder="Email address"
                    class="w-full pl-10 pr-4 py-3 rounded-xl
                           bg-zinc-100 dark:bg-zinc-800
                           border focus:border-[#7C9E8C]
                           text-zinc-900 dark:text-white placeholder:text-zinc-400 text-sm
                           focus:outline-none focus:ring-2 focus:ring-[#7C9E8C]/30
                           transition"
                    :class="validationError ? 'border-red-400' : 'border-transparent'"
                  />
                </div>
  
                <!-- Inline validation error -->
                <p v-if="validationError" class="text-red-500 text-xs px-1">{{ validationError }}</p>
  
                <!-- API error -->
                <p v-if="errorMsg" class="text-red-500 text-xs bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 rounded-xl px-4 py-2.5">
                  {{ errorMsg }}
                </p>
  
                <button
                  type="submit"
                  :disabled="loading"
                  class="w-full py-3 rounded-full bg-[#7C9E8C] hover:bg-[#6a8f7c] active:bg-[#5d8070]
                         text-white text-sm font-bold tracking-wide
                         disabled:opacity-50 disabled:cursor-not-allowed
                         transition duration-200 shadow-md shadow-[#7C9E8C]/30 mt-1"
                >
                  <span v-if="loading">Sending…</span>
                  <span v-else>Send Reset Link</span>
                </button>
              </form>
  
              <p class="text-center text-sm text-zinc-400 dark:text-zinc-500 mt-6">
                Remembered it?
                <RouterLink to="/login" class="text-[#7C9E8C] font-semibold ml-1 hover:underline">
                  Back to Sign In
                </RouterLink>
              </p>
  
            </div>
          </div>
  
        </div>
      </main>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { useAuthStore } from '@/stores/auth'
  
  const auth = useAuthStore()
  
  const email = ref('')
  const loading = ref(false)
  const submitted = ref(false)
  const validationError = ref('')
  const errorMsg = ref('')
  const isDark = ref(false)
  
  function toggleDark() {
    isDark.value = !isDark.value
    document.documentElement.classList.toggle('dark', isDark.value)
  }
  
  function validate() {
    if (!email.value.trim()) {
      validationError.value = 'Email is required.'
      return false
    }
    if (!/.+@.+\..+/.test(email.value)) {
      validationError.value = 'Please enter a valid email address.'
      return false
    }
    validationError.value = ''
    return true
  }
  
  async function handleSubmit() {
    if (!validate()) return
  
    loading.value = true
    errorMsg.value = ''
    try {
      await auth.resetPassword(email.value)
      submitted.value = true  // show success message regardless
    } catch (e) {
      // don't reveal whether email exists — show generic error only for network-level failures
      errorMsg.value = 'Something went wrong. Please try again.'
    } finally {
      loading.value = false
    }
  }
  </script>
  