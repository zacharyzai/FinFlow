<template>
  <div class="overflow-x-auto rounded-xl border border-slate-200 dark:border-white/5">
    <table class="w-full text-sm">
      <thead class="bg-slate-50 dark:bg-[#1a2e2b]">
        <tr>
          <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Date</th>
          <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Description</th>
          <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Category</th>
          <th class="px-4 py-3 text-right text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Withdrawal</th>
          <th class="px-4 py-3 text-right text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Credit</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-100 dark:divide-white/5 bg-white dark:bg-transparent">
        <tr
          v-for="tx in transactions"
          :key="tx.id"
          class="hover:bg-slate-50 dark:hover:bg-white/[0.03] transition-colors duration-150"
          style="animation: fade-up 200ms var(--ease-out) both"
        >
          <td class="px-4 py-3 text-slate-500 dark:text-slate-400 whitespace-nowrap tabular-nums">{{ tx.date }}</td>
          <td class="px-4 py-3 text-slate-800 dark:text-white font-medium max-w-xs truncate">{{ tx.description }}</td>
          <td class="px-4 py-3">
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-[#7C9E8C]/15 text-[#7C9E8C]">
              {{ tx.category }}
            </span>
          </td>
          <td class="px-4 py-3 text-right text-slate-600 dark:text-slate-300 tabular-nums">
            {{ tx.withdrawal ? tx.withdrawal.toFixed(2) : '—' }}
          </td>
          <td class="px-4 py-3 text-right font-medium text-[#7C9E8C] tabular-nums">
            {{ tx.credit ? tx.credit.toFixed(2) : '—' }}
          </td>
        </tr>
        <tr v-if="!transactions.length">
          <td colspan="5" class="px-4 py-16 text-center text-slate-400 text-sm">
            No transactions yet — upload a statement to get started.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  transactions: {
    type: Array,
    default: () => [],
  },
})
</script>
