<template>
  <header class="flex items-center justify-between px-6 py-4 bg-white border-b border-zinc-200">
    <h2 class="text-lg font-semibold text-zinc-900">{{ title }}</h2>
    <div class="flex items-center gap-4">
      <span class="text-sm text-zinc-500">{{ auth.user?.email }}</span>
      <button
        @click="handleSignOut"
        class="px-4 py-1.5 text-sm font-medium rounded-full border border-zinc-200
              text-zinc-600 hover:bg-zinc-100 transition">
        Sign out
      </button>
    </div>
  </header>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
const router = useRouter()

async function handleSignOut() {
  await auth.signOut()      
  router.push('/login')     
}
defineProps({ title: String })
const auth = useAuthStore()
</script>
