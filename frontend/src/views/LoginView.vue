<template>
  <AuthLayout :panel="true">
    <div>

            <!-- Icon mark -->
            <div class="flex justify-center mb-5">
              <img src="/images/finflow-logo.svg" alt="FinFlow" class="w-14 h-14 object-contain" />
            </div>

            <!-- Heading + subtext -->
            <h1 class="text-2xl font-bold text-center text-zinc-900 dark:text-white mb-1">
              {{ isSignUp ? 'Create account' : 'Sign In' }}
            </h1>
            <p class="text-center text-sm text-zinc-400 dark:text-zinc-500 mb-7">
              Your money, finally making sense.
            </p>

            <form @submit.prevent="handleSubmit" class="space-y-3">

              <!-- Email input with mail icon -->
              <div class="relative">
                <!-- Mail icon — absolutely positioned on the left inside the input -->
                <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400 pointer-events-none" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                </svg>
                <input
                  v-model="email"
                  type="email"
                  placeholder="Email address"
                  required
                  class="w-full pl-10 pr-4 py-3 rounded-xl
                         bg-zinc-100 dark:bg-zinc-800
                         border border-transparent focus:border-[#7C9E8C]
                         text-zinc-900 dark:text-white placeholder:text-zinc-400 text-sm
                         focus:outline-none focus:ring-2 focus:ring-[#7C9E8C]/30
                         transition"
                />
              </div>

              <!-- Password input with lock icon + show/hide -->
              <div class="relative">
                <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400 pointer-events-none" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
                <input
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="Password"
                  required
                  class="w-full pl-10 pr-11 py-3 rounded-xl
                         bg-zinc-100 dark:bg-zinc-800
                         border border-transparent focus:border-[#7C9E8C]
                         text-zinc-900 dark:text-white placeholder:text-zinc-400 text-sm
                         focus:outline-none focus:ring-2 focus:ring-[#7C9E8C]/30
                         transition"
                />
                <button type="button" @click="showPassword = !showPassword"
                  class="absolute right-3.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 transition">
                  <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.477 0-8.268-2.943-9.542-7a9.97 9.97 0 012.082-3.315M6.228 6.228A9.97 9.97 0 0112 5c4.477 0 8.268 2.943 9.542 7a9.97 9.97 0 01-1.13 2.257M6.228 6.228L3 3m3.228 3.228l3.65 3.65M19.772 19.772L21 21m-1.228-1.228l-3.65-3.65"/>
                  </svg>
                </button>
              </div>

              <!-- Forgot password -->
              <div v-if="!isSignUp" class="text-right">
                <RouterLink to="/forgot-password" class="text-xs text-zinc-400 hover:text-[#7C9E8C] transition">Forgot password?</RouterLink>
              </div>

              <!-- Error / success -->
              <p v-if="errorMsg" class="text-red-500 text-xs bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 rounded-xl px-4 py-2.5">
                {{ errorMsg }}
              </p>
              <p v-if="signUpSuccess" class="text-[#7C9E8C] text-xs bg-green-50 dark:bg-green-950/40 border border-green-200 dark:border-green-900 rounded-xl px-4 py-2.5">
                Check your email to confirm your account.
              </p>

              <!-- CTA button -->
              <button
                type="submit"
                :disabled="loading"
                class="w-full py-3 rounded-full bg-[#7C9E8C] hover:bg-[#6a8f7c] active:bg-[#5d8070]
                       text-white text-sm font-bold tracking-wide
                       disabled:opacity-50 disabled:cursor-not-allowed
                       transition duration-200 shadow-md shadow-[#7C9E8C]/30 mt-1"
              >
                <span v-if="loading">{{ isSignUp ? 'Creating account…' : 'Signing in…' }}</span>
                <span v-else>{{ isSignUp ? 'Create Account' : 'Sign In' }}</span>
              </button>
            </form>

            <!-- Divider -->
            <div class="flex items-center gap-3 my-5">
              <div class="flex-1 h-px bg-zinc-200 dark:bg-zinc-700"></div>
              <span class="text-zinc-400 text-xs">Or sign in with</span>
              <div class="flex-1 h-px bg-zinc-200 dark:bg-zinc-700"></div>
            </div>

            <!-- Google button -->
            <button
              type="button"
              disabled
              class="w-full flex items-center justify-center gap-3 py-3 rounded-full
                     border border-zinc-200 dark:border-zinc-700
                     bg-white dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400 text-sm
                     opacity-60 cursor-not-allowed"
            >
              <svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Continue with Google
            </button>
            <p class="text-center text-xs text-zinc-400 italic mt-2">More options coming soon</p>

            <!-- Sign up toggle -->
            <p class="text-center text-sm text-zinc-400 dark:text-zinc-500 mt-6">
              {{ isSignUp ? 'Already have an account?' : "Don't have an account?" }}
              <button
                @click="isSignUp = !isSignUp; errorMsg = ''; signUpSuccess = false"
                class="text-[#7C9E8C] font-semibold ml-1 hover:underline"
              >
                {{ isSignUp ? 'Sign in' : 'Sign Up' }}
              </button>
            </p>

    </div>
  </AuthLayout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AuthLayout from '@/components/AuthLayout.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const email = ref('')
const password = ref('')
const isSignUp = ref(route.name === 'Signup')
const loading = ref(false)
const errorMsg = ref('')
const signUpSuccess = ref(false)
const showPassword = ref(false)

async function handleSubmit() {
  errorMsg.value = ''
  signUpSuccess.value = false
  loading.value = true
  try {
    if (isSignUp.value) {
      await auth.signUp(email.value, password.value)
      signUpSuccess.value = true
    } else {
      await auth.signIn(email.value, password.value)
      router.push('/dashboard')
    }
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
