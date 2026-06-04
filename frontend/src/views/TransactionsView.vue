<template>
  <div class="layout">
    <AppSidebar />
    <main>
      <AppHeader title="Transactions" />
      <div v-if="store.loading">Loading...</div>
      <p v-else-if="store.error" class="error">{{ store.error }}</p>
      <TransactionTable v-else :transactions="store.transactions" />
    </main>
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
