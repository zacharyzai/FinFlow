<template>
  <div class="flex min-h-screen bg-slate-50 dark:bg-[#0f1a19]">
    <AppSidebar />
    <div class="flex-1 flex flex-col min-w-0">
      <AppHeader title="Transactions" />
      <main class="flex-1 p-6">
        <div v-if="store.loading" class="text-slate-400 text-sm">Loading...</div>
        <p v-else-if="store.error" class="text-red-400 text-sm">{{ store.error }}</p>
        <TransactionTable v-else :transactions="store.transactions" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'
import TransactionTable from '@/components/TransactionTable.vue'
import { useTransactionsStore } from '@/stores/transactions'

const store = useTransactionsStore()
onMounted(() => store.fetch())
</script>
