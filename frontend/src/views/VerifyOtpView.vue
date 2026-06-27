<template>
  <AuthLayout>

        <h1 class="text-2xl font-bold text-center text-zinc-900 dark:text-white mb-1">
          Check your email
        </h1>
        <p class="text-center text-sm text-zinc-400 dark:text-zinc-500 mb-2">
          We sent an 8-digit code to
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
            class="w-11 h-14 text-center text-lg font-bold rounded-xl
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

  </AuthLayout>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AuthLayout from '@/components/AuthLayout.vue'

const auth = useAuthStore()
const router = useRouter()

const email = history.state.email
const digits = ref(['', '', '', '', '', '', '', ''])
const inputs = ref([])
const loading = ref(false)
const errorMsg = ref('')
const resendCooldown = ref(0)
let cooldownTimer = null

// If user lands here without an email (e.g. direct URL access), send them back
onMounted(() => {
  if (!email) router.push({ name: 'ForgotPassword' })
})

onUnmounted(() => {
  clearInterval(cooldownTimer)
})

function onInput(i) {
  // Strip anything that isn't a digit
  digits.value[i] = digits.value[i].replace(/\D/g, '').slice(0, 1)

  if (digits.value[i] && i < 7) {
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
  const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 8)
  pasted.split('').forEach((char, i) => {
    digits.value[i] = char
  })
  // Focus the box after the last pasted digit
  const next = Math.min(pasted.length, 7)
  inputs.value[next].focus()

  if (pasted.length === 8 && !loading.value) submit()
}

async function submit() {
  loading.value = true
  errorMsg.value = ''
  try {
    await auth.verifyOtp(email, digits.value.join(''))
    router.push({ name: 'ResetPassword' })
  } catch (e) {
    errorMsg.value = 'Invalid or expired code. Please try again.'
    digits.value = Array(8).fill('')
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
