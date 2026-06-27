<template>
  <AuthLayout>

        <div class="flex justify-center mb-5">
          <img src="/images/finflow-logo.svg" alt="FinFlow" class="w-14 h-14 object-contain" />
        </div>

        <!-- Invalid session -->
        <div v-if="state === 'invalid'" class="text-center">
          <p class="text-red-500 text-sm bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 rounded-xl px-4 py-4 mb-5">
            Session expired. Please request a new code.
          </p>
          <RouterLink to="/forgot-password" class="text-[#7C9E8C] text-sm font-semibold hover:underline">
            Back to Forgot Password
          </RouterLink>
        </div>

        <!-- Done -->
        <div v-else-if="state === 'done'" class="text-center">
          <p class="text-[#7C9E8C] text-sm bg-green-50 dark:bg-green-950/40 border border-green-200 dark:border-green-900 rounded-xl px-4 py-4">
            Password updated. Redirecting you to sign in…
          </p>
        </div>

        <!-- Form -->
        <template v-else>
          <h1 class="text-2xl font-bold text-center text-zinc-900 dark:text-white mb-1">
            Set new password
          </h1>
          <p class="text-center text-sm text-zinc-400 dark:text-zinc-500 mb-7">
            Must be at least 8 characters.
          </p>

          <form @submit.prevent="handleSubmit" class="space-y-3">

            <!-- New password -->
            <div class="relative">
              <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400 pointer-events-none"
                   xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
              <input
                v-model="newPassword"
                :type="showNew ? 'text' : 'password'"
                placeholder="New password"
                class="w-full pl-10 pr-11 py-3 rounded-xl bg-zinc-100 dark:bg-zinc-800
                       border focus:border-[#7C9E8C] text-zinc-900 dark:text-white
                       placeholder:text-zinc-400 text-sm focus:outline-none
                       focus:ring-2 focus:ring-[#7C9E8C]/30 transition"
                :class="validationError ? 'border-red-400' : 'border-transparent'"
              />
              <button type="button" @click="showNew = !showNew"
                class="absolute right-3.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 transition">
                <svg v-if="!showNew" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.477 0-8.268-2.943-9.542-7a9.97 9.97 0 012.082-3.315M6.228 6.228A9.97 9.97 0 0112 5c4.477 0 8.268 2.943 9.542 7a9.97 9.97 0 01-1.13 2.257M6.228 6.228L3 3m3.228 3.228l3.65 3.65M19.772 19.772L21 21m-1.228-1.228l-3.65-3.65"/>
                </svg>
              </button>
            </div>

            <!-- Confirm password -->
            <div class="relative">
              <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400 pointer-events-none"
                   xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
              <input
                v-model="confirmPassword"
                :type="showConfirm ? 'text' : 'password'"
                placeholder="Confirm new password"
                class="w-full pl-10 pr-11 py-3 rounded-xl bg-zinc-100 dark:bg-zinc-800
                       border focus:border-[#7C9E8C] text-zinc-900 dark:text-white
                       placeholder:text-zinc-400 text-sm focus:outline-none
                       focus:ring-2 focus:ring-[#7C9E8C]/30 transition"
                :class="validationError ? 'border-red-400' : 'border-transparent'"
              />
              <button type="button" @click="showConfirm = !showConfirm"
                class="absolute right-3.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 transition">
                <svg v-if="!showConfirm" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.477 0-8.268-2.943-9.542-7a9.97 9.97 0 012.082-3.315M6.228 6.228A9.97 9.97 0 0112 5c4.477 0 8.268 2.943 9.542 7a9.97 9.97 0 01-1.13 2.257M6.228 6.228L3 3m3.228 3.228l3.65 3.65M19.772 19.772L21 21m-1.228-1.228l-3.65-3.65"/>
                </svg>
              </button>
            </div>

            <p v-if="validationError" class="text-red-500 text-xs px-1">{{ validationError }}</p>
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
              <span v-if="loading">Updating…</span>
              <span v-else>Update Password</span>
            </button>
          </form>
        </template>

  </AuthLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { supabase } from '@/services/supabase'
import { useAuthStore } from '@/stores/auth'
import AuthLayout from '@/components/AuthLayout.vue'

const auth = useAuthStore()
const router = useRouter()

const state = ref('ready')
const newPassword = ref('')
const confirmPassword = ref('')
const showNew = ref(false)
const showConfirm = ref(false)
const loading = ref(false)
const validationError = ref('')
const errorMsg = ref('')

onMounted(async () => {
  const { data } = await supabase.auth.getSession()
  if (!data.session) state.value = 'invalid'
})

function validate() {
  if (!newPassword.value || !confirmPassword.value) {
    validationError.value = 'Both fields are required.'
    return false
  }
  if (newPassword.value.length < 8) {
    validationError.value = 'Password must be at least 8 characters.'
    return false
  }
  if (newPassword.value !== confirmPassword.value) {
    validationError.value = 'Passwords do not match.'
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
    await auth.updatePassword(newPassword.value)
    state.value = 'done'
    await auth.signOut()
    setTimeout(() => router.push({ name: 'Login' }), 2000)
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
