<!-- frontend/src/views/SettingsView.vue -->
<template>
  <div class="flex min-h-screen bg-slate-50 dark:bg-[#0f1a19]">
    <AppSidebar />
    <div class="flex-1 flex flex-col min-w-0">
      <AppHeader title="Settings" />
      <main class="flex-1 p-6 max-w-3xl mx-auto w-full">
        <div class="rounded-2xl border border-slate-200 dark:border-white/5 bg-white dark:bg-[#1a2e2b] p-5">
          <h2 class="text-sm font-semibold text-[var(--text)] mb-1">Telegram</h2>
          <p class="text-xs text-[var(--text-3)] mb-4">
            Connect Telegram to check your budget and goals from chat: /goal, /dbudget, /mbudget, /recommendation.
          </p>

          <div v-if="loading" class="text-xs text-[var(--text-3)]">Checking status…</div>

          <div v-else-if="connected" class="flex items-center justify-between">
            <span class="text-sm text-[var(--good)] font-medium">Connected</span>
            <button @click="disconnect" :disabled="busy"
                    class="px-4 py-1.5 rounded-full border border-[var(--border)] text-[var(--text-2)] text-sm hover:bg-[var(--surface-3)] disabled:opacity-50 cursor-pointer transition-colors">
              {{ busy ? 'Disconnecting…' : 'Disconnect' }}
            </button>
          </div>

          <div v-else>
            <button @click="connect" :disabled="busy"
                    class="px-4 py-2 rounded-full bg-[var(--brand)] hover:bg-[var(--brand-strong)] text-white text-sm font-semibold disabled:opacity-50 cursor-pointer transition-colors">
              {{ busy ? 'Connecting…' : 'Connect Telegram' }}
            </button>
          </div>

          <p v-if="error" class="text-[var(--bad)] text-xs mt-3">{{ error }}</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'
import { telegramApi, apiErrorMessage } from '@/services/api'

const loading = ref(true)
const connected = ref(false)
const busy = ref(false)
const error = ref('')

async function refreshStatus() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await telegramApi.status()
    connected.value = data.connected
  } catch (e) {
    error.value = apiErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function connect() {
  busy.value = true
  error.value = ''
  try {
    const { data } = await telegramApi.linkUrl()
    window.open(data.link_url, '_blank')
    // The user finishes linking in Telegram, outside this tab — poll once
    // they've had a moment to tap "Start" so the UI catches up without
    // requiring a manual refresh.
    setTimeout(refreshStatus, 4000)
  } catch (e) {
    error.value = apiErrorMessage(e)
  } finally {
    busy.value = false
  }
}

async function disconnect() {
  busy.value = true
  error.value = ''
  try {
    await telegramApi.disconnect()
    connected.value = false
  } catch (e) {
    error.value = apiErrorMessage(e)
  } finally {
    busy.value = false
  }
}

onMounted(refreshStatus)
</script>
