<template>
  <div class="flex min-h-screen bg-slate-50 dark:bg-[#0f1a19]">
    <AppSidebar />
    <div class="flex-1 flex flex-col min-w-0">
      <AppHeader title="Dashboard" />
      <main class="flex-1 p-6">
        <div v-if="store.loading" class="text-slate-400 text-sm">Loading...</div>
        <div v-else class="flex flex-col gap-6">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-white/5 rounded-xl p-5">
              <p class="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">Total Spend</p>
              <p class="text-2xl font-semibold text-slate-900 dark:text-white">SGD {{ store.totalSpend.toFixed(2) }}</p>
            </div>
            <div class="bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-white/5 rounded-xl p-5">
              <p class="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">Total Income</p>
              <p class="text-2xl font-semibold text-[#7C9E8C]">SGD {{ store.totalIncome.toFixed(2) }}</p>
            </div>
          </div>
          <CategoryChart :data="store.byCategory" />
        </div>
      </main>
    </div>
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
