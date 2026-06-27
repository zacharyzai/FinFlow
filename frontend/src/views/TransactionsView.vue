<template>
  <div class="flex min-h-screen bg-slate-50 dark:bg-[#0f1a19]">
    <AppSidebar />
    <div class="flex-1 flex flex-col min-w-0">
      <AppHeader title="Transactions" />
      <main class="flex-1 p-6">
        <!-- Skeleton — matches real table shape so there's no layout jump -->
        <div v-if="store.loading" class="overflow-x-auto rounded-xl border border-slate-200 dark:border-white/5 animate-pulse">
          <table class="w-full text-sm">
            <thead class="bg-slate-50 dark:bg-[#1a2e2b]">
              <tr>
                <th v-for="w in ['w-16','w-36','w-20','w-20','w-16']" :key="w" class="px-4 py-3 text-left">
                  <div class="h-2.5 bg-slate-200 dark:bg-slate-700 rounded" :class="w" />
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-white/5 bg-white dark:bg-transparent">
              <tr v-for="i in 10" :key="i">
                <td class="px-4 py-3"><div class="h-3 bg-slate-200 dark:bg-slate-700 rounded w-20" /></td>
                <td class="px-4 py-3"><div class="h-3 bg-slate-200 dark:bg-slate-700 rounded w-48" /></td>
                <td class="px-4 py-3"><div class="h-5 bg-slate-200 dark:bg-slate-700 rounded-full w-16" /></td>
                <td class="px-4 py-3"><div class="h-3 bg-slate-200 dark:bg-slate-700 rounded w-16 ml-auto" /></td>
                <td class="px-4 py-3"><div class="h-3 bg-slate-200 dark:bg-slate-700 rounded w-16 ml-auto" /></td>
              </tr>
            </tbody>
          </table>
        </div>

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
