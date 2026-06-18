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
      <div class="w-full max-w-sm bg-white dark:bg-[#1a2433] rounded-2xl shadow-[0_32px_80px_rgba(0,0,0,0.35)] p-10 transition-colors duration-300">

        <div class="flex justify-center mb-5">
          <img src="/images/finflow-logo.svg" alt="FinFlow" class="w-14 h-14 object-contain" />
        </div>

        <h1 class="text-2xl font-bold text-center text-zinc-900 dark:text-white mb-1">
          Check your email
        </h1>
        <p class="text-center text-sm text-zinc-400 dark:text-zinc-500 mb-2">
          We sent a 6-digit code to
        </p>
        <p class="text-center text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-8">
          {{ email }}
        </p>

        <!-- 6-digit boxes -->
        <div class="flex justify-center gap-3 mb-6">
          <input
            v-for="(_, i) in digits"
            :key="i"
            :ref="el => { if (el) inputs[i] = el }"
            v-model="digits[i]"
            type="text"
            inputmode="numeric"
            maxlength="1"
            @input="onInput(i)"
            @keydown="onKeydown($event, i)"
            @paste="onPaste($event)"
            class="w-11 h-14 text-center text-xl font-bold rounded-xl
                   bg-zinc-100 dark:bg-zinc-800
                   border-2 focus:border-[#7C9E8C]
                   text-zinc-900 dark:text-white
                   focus:outline-none focus:ring-2 focus:ring-[#7C9E8C]/30
                   transition"
            :class="errorMsg ? 'border-red-400' : 'border-transparent'"
          />
        </div>

        <!-- Error -->
        <p v-if="errorMsg" class="text-red-500 text-xs text-center bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 rounded-xl px-4 py-2.5 mb-4">
          {{ errorMsg }}
        </p>

        <!-- Loading state -->
        <p v-if="loading" class="text-center text-sm text-zinc-400 dark:text-zinc-500">
          Verifying…
        </p>

        <p class="text-center text-sm text-zinc-400 dark:text-zinc-500 mt-6">
          Didn't get a code?
          <button @click="resend" :disabled="resendCooldown > 0" class="text-[#7C9E8C] font-semibold ml-1 hover:underline disabled:opacity-50 disabled:cursor-not-allowed">
            {{ resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend' }}
          </button>
        </p>

        <p class="text-center text-sm text-zinc-400 dark:text-zinc-500 mt-3">
          <RouterLink to="/forgot-password" class="text-[#7C9E8C] font-semibold hover:underline">
            Back
          </RouterLink>
        </p>

      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const email = history.state.email
const digits = ref(['', '', '', '', '', ''])
const inputs = ref([])
const loading = ref(false)
const errorMsg = ref('')
const isDark = ref(false)
const resendCooldown = ref(0)
let cooldownTimer = null

// If user lands here without an email (e.g. direct URL access), send them back
onMounted(() => {
  if (!email) router.push({ name: 'ForgotPassword' })
})

onUnmounted(() => {
  clearInterval(cooldownTimer)
})

function toggleDark() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
}

function onInput(i) {
  // Strip anything that isn't a digit
  digits.value[i] = digits.value[i].replace(/\D/g, '').slice(0, 1)

  if (digits.value[i] && i < 5) {
    inputs.value[i + 1].focus()
  }

  if (digits.value.every(d => d !== '') && !loading.value) {
    submit()
  }
}

function onKeydown(e, i) {
  if (e.key === 'Backspace' && !digits.value[i] && i > 0) {
    inputs.value[i - 1].focus()
  }
}

function onPaste(e) {
  e.preventDefault()
  const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
  pasted.split('').forEach((char, i) => {
    digits.value[i] = char
  })
  // Focus the box after the last pasted digit
  const next = Math.min(pasted.length, 5)
  inputs.value[next].focus()

  if (pasted.length === 6 && !loading.value) submit()
}

async function submit() {
  loading.value = true
  errorMsg.value = ''
  try {
    await auth.verifyOtp(email, digits.value.join(''))
    router.push({ name: 'ResetPassword' })
  } catch (e) {
    errorMsg.value = 'Invalid or expired code. Please try again.'
    digits.value = ['', '', '', '', '', '']
    inputs.value[0].focus()
  } finally {
    loading.value = false
  }
}

async function resend() {
  try {
    await auth.resetPassword(email)
    // 30-second cooldown to prevent spam
    resendCooldown.value = 30
    cooldownTimer = setInterval(() => {
      resendCooldown.value--
      if (resendCooldown.value <= 0) clearInterval(cooldownTimer)
    }, 1000)
  } catch (e) {
    errorMsg.value = 'Could not resend code. Please try again.'
  }
}
</script>
