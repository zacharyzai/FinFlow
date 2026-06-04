<template>
  <header class="app-header">
    <h2>{{ title }}</h2>
    <div class="header-actions">
      <span>{{ auth.user?.email }}</span>
      <button @click="auth.signOut()">Sign out</button>
    </div>
  </header>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

defineProps({ title: String })
const auth = useAuthStore()
</script>
