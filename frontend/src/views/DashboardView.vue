<template>
  <div class="layout">
    <AppSidebar />
    <main>
      <AppHeader title="Dashboard" />
      <div v-if="store.loading">Loading...</div>
      <div v-else class="dashboard-grid">
        <div class="stat-card">
          <h3>Total Spend</h3>
          <p>SGD {{ store.totalSpend.toFixed(2) }}</p>
        </div>
        <div class="stat-card">
          <h3>Total Income</h3>
          <p>SGD {{ store.totalIncome.toFixed(2) }}</p>
        </div>
        <CategoryChart :data="store.byCategory" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'
import CategoryChart from '@/components/CategoryChart.vue'
import { useTransactionsStore } from '@/stores/transactions'

const store = useTransactionsStore()
onMounted(() => store.fetch())
</script>
