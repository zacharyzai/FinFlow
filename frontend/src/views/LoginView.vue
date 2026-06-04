<template>
  <div class="login-page">
    <h1>FinFlow</h1>
    <form @submit.prevent="handleSubmit">
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Password" required />
      <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
      <button type="submit" :disabled="loading">
        {{ isSignUp ? 'Sign Up' : 'Log In' }}
      </button>
      <button type="button" @click="isSignUp = !isSignUp">
        {{ isSignUp ? 'Already have an account? Log in' : "Don't have an account? Sign up" }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const isSignUp = ref(false)
const loading = ref(false)
const errorMsg = ref('')

async function handleSubmit() {
  errorMsg.value = ''
  loading.value = true
  try {
    if (isSignUp.value) {
      await auth.signUp(email.value, password.value)
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
