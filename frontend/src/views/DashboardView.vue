<template>
  <div class="flex min-h-screen bg-slate-50 dark:bg-[#0f1a19]">
    <AppSidebar />
    <div class="flex-1 flex flex-col min-w-0">
      <AppHeader title="Dashboard" />
      <main class="flex-1 p-6 relative overflow-hidden">

        <!-- Ambient glow blobs — dark mode only, sets the "21st.dev" depth -->
        <div class="pointer-events-none absolute -top-40 right-0 w-[600px] h-[600px] rounded-full dark:bg-[#7C9E8C]/[0.05] blur-3xl" />
        <div class="pointer-events-none absolute bottom-0 -left-40 w-80 h-80 rounded-full dark:bg-[#7C9E8C]/[0.04] blur-3xl" />

        <!-- Skeleton while loading -->
        <div v-if="store.loading" class="relative grid grid-cols-1 lg:grid-cols-3 gap-4 animate-pulse">
          <div class="lg:col-span-2 bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-white/5 rounded-xl p-5">
            <div class="h-3 bg-slate-200 dark:bg-slate-700 rounded w-24 mb-4" />
            <div class="h-8 bg-slate-200 dark:bg-slate-700 rounded w-44" />
          </div>
          <div class="bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-white/5 rounded-xl p-5">
            <div class="h-3 bg-slate-200 dark:bg-slate-700 rounded w-24 mb-4" />
            <div class="h-8 bg-slate-200 dark:bg-slate-700 rounded w-36" />
          </div>
          <div class="lg:col-span-2 bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-white/5 rounded-xl p-5 space-y-4">
            <div class="h-3 bg-slate-200 dark:bg-slate-700 rounded w-36 mb-2" />
            <div v-for="i in 4" :key="i" class="h-2 bg-slate-200 dark:bg-slate-700 rounded" :style="{ width: (35 + i * 14) + '%' }" />
          </div>
          <div class="bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-white/5 rounded-xl p-5">
            <div class="h-3 bg-slate-200 dark:bg-slate-700 rounded w-24 mb-4" />
            <div class="h-8 bg-slate-200 dark:bg-slate-700 rounded w-16" />
          </div>
        </div>

        <!-- Bento grid -->
        <div v-else class="relative grid grid-cols-1 lg:grid-cols-3 gap-4">

          <!-- Total Spend — 2/3 width, wider emphasis -->
          <div
            class="lg:col-span-2 bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-white/5 rounded-xl p-5"
            style="animation: fade-up 280ms var(--ease-out) both"
          >
            <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Total Spend</p>
            <p class="text-3xl font-semibold text-slate-900 dark:text-white tabular-nums">
              SGD {{ spendDisplay.toFixed(2) }}
            </p>
            <p class="text-xs text-slate-400 mt-1">across all transactions</p>
          </div>

          <!-- Total Income — 1/3 width, sage green accent -->
          <div
            class="bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-white/5 rounded-xl p-5 relative overflow-hidden"
            style="animation: fade-up 280ms var(--ease-out) 60ms both"
          >
            <!-- Subtle green glow inside card -->
            <div class="pointer-events-none absolute -top-8 -right-8 w-32 h-32 rounded-full bg-[#7C9E8C]/10 blur-2xl" />
            <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Total Income</p>
            <p class="text-3xl font-semibold text-[#7C9E8C] tabular-nums">
              SGD {{ incomeDisplay.toFixed(2) }}
            </p>
            <p class="text-xs text-slate-400 mt-1">credits received</p>
          </div>

          <!-- Spending by Category — 2/3 width -->
          <div
            class="lg:col-span-2 bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-white/5 rounded-xl p-5"
            style="animation: fade-up 280ms var(--ease-out) 120ms both"
          >
            <CategoryChart :data="store.byCategory" />
          </div>

          <!-- Transaction count — 1/3 width -->
          <div
            class="bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-white/5 rounded-xl p-5 flex flex-col justify-between"
            style="animation: fade-up 280ms var(--ease-out) 180ms both"
          >
            <div>
              <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Transactions</p>
              <p class="text-3xl font-semibold text-slate-900 dark:text-white tabular-nums">
                {{ Math.round(txCount) }}
              </p>
              <p class="text-xs text-slate-400 mt-1">recorded entries</p>
            </div>
            <router-link
              to="/transactions"
              class="mt-4 inline-flex items-center gap-1.5 text-xs font-medium text-[#7C9E8C] hover:text-[#6a8f7c] transition-colors duration-150"
            >
              View all
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"/>
              </svg>
            </router-link>
          </div>

        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'
import CategoryChart from '@/components/CategoryChart.vue'
import { useTransactionsStore } from '@/stores/transactions'
import { useCountUp } from '@/composables/useCountUp'

const store = useTransactionsStore()
onMounted(() => store.fetch())

const spendDisplay = useCountUp(computed(() => store.totalSpend))
const incomeDisplay = useCountUp(computed(() => store.totalIncome))
const txCount = useCountUp(computed(() => store.transactions.length), 600)
</script>
