<template>
  <AuthLayout :panel="true">
    <div>

      <!-- Heading — crossfades when sign-in ↔ sign-up mode switches -->
      <Transition name="swap" mode="out-in">
        <div :key="isSignUp" class="mb-7 text-center">
          <h1 class="text-2xl font-bold text-[var(--text)] mb-1">
            {{ isSignUp ? 'Create account' : 'Sign In' }}
          </h1>
          <p class="text-sm text-[var(--text-3)]">
            {{ isSignUp ? 'Start your financial clarity journey.' : 'Your money, finally making sense.' }}
          </p>
        </div>
      </Transition>

      <form @submit.prevent="handleSubmit" class="space-y-3">

        <!-- Email -->
        <div
          class="relative input-group"
          style="animation: fade-up 240ms var(--ease-out) 60ms both"
        >
          <svg
            class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none transition-colors duration-150"
            :class="emailFocused ? 'text-[var(--brand)]' : 'text-[var(--text-3)]'"
            xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
            stroke="currentColor" stroke-width="2"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
          </svg>
          <input
            v-model="email"
            type="email"
            placeholder="Email address"
            autocomplete="email"
            required
            @focus="emailFocused = true"
            @blur="emailFocused = false"
            class="w-full pl-10 pr-4 py-3 rounded-xl
                   bg-[var(--surface-2)]
                   border border-transparent
                   text-[var(--text)] placeholder:text-[var(--text-3)] text-sm
                   focus:outline-none focus:border-[var(--brand)] focus:ring-2 focus:ring-[var(--brand)]/25
                   transition-all duration-200"
          />
        </div>

        <!-- Password -->
        <div
          class="relative input-group"
          style="animation: fade-up 240ms var(--ease-out) 110ms both"
        >
          <svg
            class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none transition-colors duration-150"
            :class="passwordFocused ? 'text-[var(--brand)]' : 'text-[var(--text-3)]'"
            xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
            stroke="currentColor" stroke-width="2"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
          </svg>
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="Password"
            autocomplete="current-password"
            required
            @focus="passwordFocused = true"
            @blur="passwordFocused = false"
            class="w-full pl-10 pr-11 py-3 rounded-xl
                   bg-[var(--surface-2)]
                   border border-transparent
                   text-[var(--text)] placeholder:text-[var(--text-3)] text-sm
                   focus:outline-none focus:border-[var(--brand)] focus:ring-2 focus:ring-[var(--brand)]/25
                   transition-all duration-200"
          />
          <!-- Show/hide toggle — icons crossfade on switch -->
          <button
            type="button"
            @click="showPassword = !showPassword"
            :aria-label="showPassword ? 'Hide password' : 'Show password'"
            class="absolute right-3.5 top-1/2 -translate-y-1/2 text-[var(--text-3)] hover:text-[var(--text)] cursor-pointer transition-colors duration-150"
          >
            <Transition name="icon-swap" mode="out-in">
              <svg v-if="!showPassword" key="eye-on" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
              <svg v-else key="eye-off" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.477 0-8.268-2.943-9.542-7a9.97 9.97 0 012.082-3.315M6.228 6.228A9.97 9.97 0 0112 5c4.477 0 8.268 2.943 9.542 7a9.97 9.97 0 01-1.13 2.257M6.228 6.228L3 3m3.228 3.228l3.65 3.65M19.772 19.772L21 21m-1.228-1.228l-3.65-3.65"/>
              </svg>
            </Transition>
          </button>
        </div>

        <!-- Forgot password — slides in/out when toggling sign-up mode -->
        <Transition name="slide-down">
          <div v-if="!isSignUp" class="text-right">
            <RouterLink
              to="/forgot-password"
              class="text-xs text-[var(--text-3)] hover:text-[var(--brand)] transition-colors duration-150 cursor-pointer"
            >
              Forgot password?
            </RouterLink>
          </div>
        </Transition>

        <!-- Error / success messages — slide in from above -->
        <Transition name="slide-down">
          <p v-if="errorMsg" key="err" role="alert"
             class="text-[var(--bad)] text-xs bg-[var(--bad-bg)] border border-[var(--bad-bd)] rounded-xl px-4 py-2.5">
            {{ errorMsg }}
          </p>
        </Transition>
        <Transition name="slide-down">
          <p v-if="signUpSuccess" key="ok" role="status"
             class="text-[var(--good)] text-xs bg-[var(--good-bg)] border border-[var(--good-bd)] rounded-xl px-4 py-2.5">
            Check your email to confirm your account.
          </p>
        </Transition>

        <!-- CTA — button label crossfades to loading dots -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full py-3 rounded-full bg-[var(--brand)] hover:bg-[var(--brand-strong)]
                 text-[var(--on-brand)] text-sm font-bold tracking-wide
                 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer
                 transition-colors duration-200 shadow-md shadow-[var(--brand)]/30 mt-1"
          style="animation: fade-up 240ms var(--ease-out) 160ms both"
        >
          <Transition name="icon-swap" mode="out-in">
            <span v-if="loading" key="loading" class="flex items-center justify-center gap-1">
              <span class="loading-dot">●</span>
              <span class="loading-dot" style="animation-delay:0.15s">●</span>
              <span class="loading-dot" style="animation-delay:0.30s">●</span>
            </span>
            <span v-else key="label">{{ isSignUp ? 'Create Account' : 'Sign In' }}</span>
          </Transition>
        </button>
      </form>

      <!-- Divider -->
      <div
        class="flex items-center gap-3 my-5"
        style="animation: fade-up 240ms var(--ease-out) 200ms both"
      >
        <div class="flex-1 h-px bg-[var(--border)]"></div>
        <span class="text-[var(--text-3)] text-xs">Or sign in with</span>
        <div class="flex-1 h-px bg-[var(--border)]"></div>
      </div>

      <!-- Google button -->
      <button
        type="button"
        @click="signInWithGoogle"
        class="w-full flex items-center justify-center gap-3 py-3 rounded-full
               border border-[var(--border)]
               bg-[var(--surface)] text-[var(--text-2)] text-sm
               hover:bg-[var(--surface-2)] cursor-pointer transition-colors duration-200"
        style="animation: fade-up 240ms var(--ease-out) 225ms both"
      >
        <svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
        Continue with Google
      </button>

      <!-- Sign-up toggle — text crossfades on mode switch -->
      <Transition name="swap" mode="out-in">
        <!-- ponytail: no inline animation — swap <Transition> owns enter/exit on every mount.
             Inline animation: would re-run the 260ms stagger delay on every mode click, silencing swap. -->
        <p :key="isSignUp" class="text-center text-sm text-[var(--text-3)] mt-6">
          {{ isSignUp ? 'Already have an account?' : "Don't have an account?" }}
          <button
            type="button"
            @click="isSignUp = !isSignUp; errorMsg = ''; signUpSuccess = false"
            class="text-[var(--brand)] font-semibold ml-1 hover:underline cursor-pointer"
          >
            {{ isSignUp ? 'Sign in' : 'Sign Up' }}
          </button>
        </p>
      </Transition>

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
const emailFocused = ref(false)
const passwordFocused = ref(false)

async function signInWithGoogle() {
  await auth.signInWithGoogle()
}

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
