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
          <th class="px-4 py-3 w-10"></th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-100 dark:divide-white/5 bg-white dark:bg-transparent">
        <tr
          v-for="tx in transactions"
          :key="tx.id"
          class="hover:bg-slate-50 dark:hover:bg-white/[0.03] transition-colors duration-150"
          style="animation: fade-up 200ms var(--ease-out) both"
        >
          <template v-if="editingId === tx.id">
            <td class="px-4 py-2">
              <input v-model="draft.date" type="date" class="edit-field w-[130px]" />
            </td>
            <td class="px-4 py-2">
              <input v-model="draft.description" type="text" class="edit-field w-full" />
            </td>
            <td class="px-4 py-2">
              <select v-model="draft.category" class="edit-field">
                <option v-for="c in CATEGORIES" :key="c" :value="c">{{ c }}</option>
              </select>
            </td>
            <td class="px-4 py-2" colspan="2">
              <div class="flex items-center justify-end gap-2">
                <select v-model="draft.type" class="edit-field w-[110px]">
                  <option value="withdrawal">Withdrawal</option>
                  <option value="credit">Credit</option>
                </select>
                <input v-model="draft.amount" type="number" min="0.01" step="0.01" class="edit-field w-24 text-right" />
              </div>
            </td>
            <td class="px-4 py-2">
              <div class="flex items-center gap-1 justify-end">
                <button title="Save" :disabled="savingId === tx.id" @click="save(tx.id)"
                        class="w-7 h-7 flex items-center justify-center rounded-lg text-[#7C9E8C] hover:bg-[#7C9E8C]/15 cursor-pointer disabled:opacity-50">
                  <span class="material-symbols-outlined" style="font-size:18px">check</span>
                </button>
                <button title="Cancel" @click="cancel"
                        class="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-white/10 cursor-pointer">
                  <span class="material-symbols-outlined" style="font-size:18px">close</span>
                </button>
              </div>
            </td>
          </template>

          <template v-else>
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
            <td class="px-4 py-3">
              <button title="Edit" @click="startEdit(tx)"
                      class="w-7 h-7 flex items-center justify-center rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 cursor-pointer">
                <span class="material-symbols-outlined" style="font-size:16px">edit</span>
              </button>
            </td>
          </template>
        </tr>
        <tr v-if="!transactions.length">
          <td colspan="6" class="px-4 py-16 text-center text-slate-400 text-sm">
            No transactions yet — upload a statement to get started.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useTransactionsStore } from '@/stores/transactions'
import { useToastStore } from '@/stores/toast'
import { CATEGORIES } from '@/constants'

defineProps({
  transactions: {
    type: Array,
    default: () => [],
  },
})

const store = useTransactionsStore()
const toast = useToastStore()

const editingId = ref(null)
const savingId = ref(null)
const draft = ref({ date: '', description: '', category: '', type: 'withdrawal', amount: '' })

function startEdit(tx) {
  editingId.value = tx.id
  draft.value = {
    date: tx.date,
    description: tx.description,
    category: tx.category,
    type: tx.withdrawal != null ? 'withdrawal' : 'credit',
    amount: tx.withdrawal ?? tx.credit ?? '',
  }
}

function cancel() {
  editingId.value = null
}

async function save(id) {
  savingId.value = id
  try {
    await store.update(id, {
      date: draft.value.date,
      description: draft.value.description.trim(),
      category: draft.value.category,
      type: draft.value.type,
      amount: +draft.value.amount,
    })
    editingId.value = null
  } catch (e) {
    toast.push(e.response?.data?.detail ?? e.message ?? 'Failed to update transaction', 'error')
  } finally {
    savingId.value = null
  }
}
</script>

<style scoped>
.edit-field {
  padding: 6px 8px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-size: 13px;
}
.edit-field:focus {
  outline: none;
  border-color: var(--brand);
}
</style>
