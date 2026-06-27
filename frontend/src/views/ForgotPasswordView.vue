<template>
  <AuthLayout :panel="true">
    <div>

              <h1 class="text-2xl font-bold text-center text-zinc-900 dark:text-white mb-1">
                Reset your password
              </h1>
              <p class="text-center text-sm text-zinc-400 dark:text-zinc-500 mb-7">
                Enter your email and we'll send you a 6-digit code.
              </p>

              <form @submit.prevent="handleSubmit" class="space-y-3">
  
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
                  <span v-else>Send Code</span>
                </button>
              </form>
  
              <p class="text-center text-sm text-zinc-400 dark:text-zinc-500 mt-6">
                Remembered it?
                <RouterLink to="/login" class="text-[#7C9E8C] font-semibold ml-1 hover:underline">
                  Back to Sign In
                </RouterLink>
              </p>
  
    </div>
  </AuthLayout>
</template>
  
  <script setup>
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '@/stores/auth'
  import AuthLayout from '@/components/AuthLayout.vue'

  const auth = useAuthStore()
  const router = useRouter()

  const email = ref('')
  const loading = ref(false)
  const validationError = ref('')
  const errorMsg = ref('')
  
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
      router.push({ name: 'VerifyOtp', state: { email: email.value } })
    } catch (e) {
      // don't reveal whether email exists — show generic error only for network-level failures
      errorMsg.value = e.message
    } finally {
      loading.value = false
    }
  }
  </script>
  