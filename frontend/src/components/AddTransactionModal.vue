<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4">

        <!-- Backdrop: click to dismiss -->
        <div class="absolute inset-0 bg-black/50" @click="emit('close')"></div>

        <!-- Card. Modals keep transform-origin center (not trigger-anchored like popovers) -->
        <div class="modal-card relative w-full max-w-sm bg-[var(--surface)] border border-[var(--border)]
                    rounded-2xl p-6 shadow-[0_24px_64px_rgba(0,0,0,0.3)]">
          <h2 class="text-lg font-bold text-[var(--text)] mb-4">Add transaction</h2>

          <form @submit.prevent="handleSubmit" class="space-y-3">

            <div>
              <label for="tx-desc" class="field-label">Description</label>
              <input id="tx-desc" ref="firstField" v-model="description" type="text"
                     required placeholder="e.g. Ya Kun Kaya Toast" class="field" />
            </div>

            <div class="flex gap-3">
              <div class="flex-1">
                <label for="tx-amount" class="field-label">Amount (SGD)</label>
                <input id="tx-amount" v-model="amount" type="number" inputmode="decimal"
                       min="0.01" step="0.01" required placeholder="0.00" class="field" />
              </div>
              <div class="flex-1">
                <label for="tx-type" class="field-label">Type</label>
                <select id="tx-type" v-model="type" class="field">
                  <option value="withdrawal">Withdrawal</option>
                  <option value="credit">Income (Credit)</option>
                </select>
              </div>
            </div>

            <div class="flex gap-3">
              <div class="flex-1">
                <label for="tx-category" class="field-label">Category</label>
                <select id="tx-category" v-model="category" class="field">
                  <option v-for="c in CATEGORIES" :key="c" :value="c">{{ c }}</option>
                </select>
              </div>
              <div class="flex-1">
                <label for="tx-date" class="field-label">Date</label>
                <input id="tx-date" v-model="date" type="date" required class="field" />
              </div>
            </div>

            <!-- Error lives next to the action that caused it -->
            <p v-if="errorMsg" role="alert"
               class="text-[var(--bad)] text-xs bg-[var(--bad-bg)] border border-[var(--bad-bd)] rounded-xl px-4 py-2.5">
              {{ errorMsg }}
            </p>

            <div class="flex gap-3 pt-1">
              <button type="button" @click="emit('close')"
                      class="flex-1 py-2.5 rounded-full border border-[var(--border)]
                             text-[var(--text-2)] text-sm font-semibold cursor-pointer
                             hover:bg-[var(--surface-2)] transition-colors duration-150">
                Cancel
              </button>
              <button type="submit" :disabled="loading"
                      class="flex-1 py-2.5 rounded-full bg-[var(--brand)] hover:bg-[var(--brand-strong)]
                             text-[var(--on-brand)] text-sm font-semibold cursor-pointer
                             disabled:opacity-50 disabled:cursor-not-allowed
                             transition-colors duration-150">
                {{ loading ? 'Saving…' : 'Save' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { onKeyStroke } from '@vueuse/core'
import { useTransactionsStore } from '@/stores/transactions'
import { CATEGORIES } from '@/constants'

const props = defineProps({ open: { type: Boolean, default: false } })
const emit = defineEmits(['close'])

const store = useTransactionsStore()

const today = () => new Date().toISOString().slice(0, 10)

const description = ref('')
const amount = ref('')
const type = ref('withdrawal')
const category = ref(CATEGORIES[0])
const date = ref(today())
const loading = ref(false)
const errorMsg = ref('')
const firstField = ref(null)

// Esc closes; focus first field on open (keyboard users land inside the modal)
onKeyStroke('Escape', () => props.open && emit('close'))
watch(() => props.open, async (isOpen) => {
  if (isOpen) {
    errorMsg.value = ''
    await nextTick()
    firstField.value?.focus()
  }
})

async function handleSubmit() {
  errorMsg.value = ''
  loading.value = true
  try {
    await store.add({
      date: date.value,
      description: description.value.trim(),
      amount: +amount.value,
      category: category.value,
      type: type.value, // server maps this to withdrawal/credit + ledger DR/CR
    })
    // Reset for next time, keep the chosen date (common when back-filling a day)
    description.value = ''
    amount.value = ''
    emit('close')
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || e.message || 'Failed to save transaction.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Shared field styling — same recipe as the login inputs */
.field-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-2);
  margin-bottom: 4px;
}
.field {
  width: 100%;
  padding: 10px 14px;
  border-radius: 12px;
  background: var(--surface-2);
  border: 1px solid transparent;
  color: var(--text);
  font-size: 14px;
}
.field::placeholder { color: var(--text-3); }
.field:focus {
  outline: none;
  border-color: var(--brand);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--brand) 25%, transparent);
}

/* Enter 200ms, exit faster (120ms). Card scales from 0.95 — never from 0. */
.modal-enter-active { transition: opacity 200ms var(--ease-out); }
.modal-leave-active { transition: opacity 120ms var(--ease-out); }
.modal-enter-from,
.modal-leave-to { opacity: 0; }
.modal-enter-active .modal-card { transition: transform 200ms var(--ease-out); }
.modal-enter-from .modal-card { transform: scale(0.95); }
</style>
