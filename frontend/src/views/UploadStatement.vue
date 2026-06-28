<template>
  <Transition name="phase-swap" mode="out-in">

    <!-- ── PROCESSING ───────────────────────────────────────────────── -->
    <div
      v-if="phase === 'processing'"
      key="processing"
      class="bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-[#7C9E8C]/20 rounded-2xl p-8"
    >
      <p class="text-slate-900 dark:text-white font-semibold mb-1">Parsing your statement…</p>
      <p class="text-slate-500 dark:text-slate-400 text-sm mb-8">
        Usually 10–20 seconds while Claude reads each transaction.
      </p>

      <div class="space-y-1">
        <div
          v-for="(step, i) in STEPS"
          :key="step.label"
          class="relative flex items-center gap-4 rounded-xl px-3 py-3 transition-colors duration-300"
          :class="i === currentStep ? 'step-shimmer' : ''"
        >
          <!-- Step indicator circle -->
          <div
            class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 transition-all duration-300"
            :class="i <= currentStep
              ? 'bg-[#7C9E8C]/20 text-[#7C9E8C]'
              : 'bg-slate-100 dark:bg-slate-700/60 text-slate-400'"
          >
            <!-- Done: stroke draws in on mount -->
            <svg v-if="i < currentStep" viewBox="0 0 16 16" fill="none" class="w-4 h-4">
              <path
                d="M3 8l3.5 3.5L13 5"
                stroke="currentColor" stroke-width="2.2"
                stroke-linecap="round" stroke-linejoin="round"
                stroke-dasharray="20" stroke-dashoffset="20"
                style="animation: draw-stroke 220ms var(--ease-out) both"
              />
            </svg>
            <!-- Active: solid dot (no spinner) -->
            <div v-else-if="i === currentStep" class="w-2.5 h-2.5 rounded-full bg-[#7C9E8C]" />
            <!-- Pending: step number -->
            <span v-else class="text-xs font-medium select-none">{{ i + 1 }}</span>
          </div>

          <!-- Step label -->
          <div>
            <p
              class="text-sm font-medium transition-colors duration-300"
              :class="i <= currentStep
                ? 'text-slate-900 dark:text-white'
                : 'text-slate-400 dark:text-slate-500'"
            >{{ step.label }}</p>
            <p class="text-xs text-slate-500 dark:text-slate-400">{{ step.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ── SUCCESS ────────────────────────────────────────────────────── -->
    <div
      v-else-if="phase === 'success'"
      key="success"
      class="bg-white dark:bg-[#1a2e2b] border border-[#7C9E8C]/30 rounded-2xl p-10 text-center"
    >
      <!-- Animated check: circle draws first, then the tick -->
      <svg class="w-16 h-16 mx-auto mb-6" viewBox="0 0 48 48" fill="none" aria-hidden="true">
        <circle
          cx="24" cy="24" r="20"
          stroke="#7C9E8C" stroke-width="2"
          stroke-dasharray="126" stroke-dashoffset="126"
          style="animation: draw-stroke 460ms var(--ease-out) 80ms both; --stroke-length:126"
        />
        <path
          d="M15 24.5l6 6 12-13"
          stroke="#7C9E8C" stroke-width="2.5"
          stroke-linecap="round" stroke-linejoin="round"
          stroke-dasharray="28" stroke-dashoffset="28"
          style="animation: draw-stroke 260ms var(--ease-out) 460ms both; --stroke-length:28"
        />
      </svg>

      <h2 class="text-xl font-bold text-slate-900 dark:text-white mb-3">Statement parsed</h2>

      <div class="mb-6">
        <span class="text-4xl font-bold text-[#7C9E8C] tabular-nums">{{ Math.round(displayCount) }}</span>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">transactions imported to your ledger</p>
      </div>

      <!-- Privacy confirmation -->
      <div class="flex items-center justify-center gap-1.5 text-xs text-slate-400 dark:text-slate-500 mb-8">
        <svg class="w-3.5 h-3.5 text-[#7C9E8C] shrink-0" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 1.944A11.954 11.954 0 012.166 5C2.056 5.649 2 6.319 2 7c0 5.225 3.34 9.67 8 11.317C14.66 16.67 18 12.225 18 7c0-.682-.057-1.35-.166-2.001A11.954 11.954 0 0110 1.944zM11 14a1 1 0 11-2 0 1 1 0 012 0zm0-7a1 1 0 10-2 0v3a1 1 0 102 0V7z" clip-rule="evenodd"/>
        </svg>
        Raw statement file permanently deleted from our servers
      </div>

      <button
        @click="$emit('uploaded')"
        class="w-full py-3 rounded-xl bg-[#7C9E8C] hover:bg-[#6a8f7c] text-white text-sm font-semibold transition-colors duration-200 cursor-pointer shadow-sm shadow-[#7C9E8C]/30"
      >
        View Transactions
      </button>
      <button
        type="button"
        @click="reset"
        class="w-full mt-3 py-2.5 rounded-xl text-sm text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors duration-150 cursor-pointer"
      >
        Upload another statement
      </button>
    </div>

    <!-- ── FORM ───────────────────────────────────────────────────────── -->
    <form v-else key="form" @submit.prevent="handleSubmit" class="space-y-6">

      <!-- Bank selector -->
      <div>
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">Bank</label>
        <div class="grid grid-cols-4 gap-2">
          <button
            v-for="b in BANKS"
            :key="b.value"
            type="button"
            @click="bank = b.value"
            class="py-2.5 rounded-lg border text-sm font-medium transition-all duration-150 cursor-pointer"
            :class="bank === b.value
              ? 'border-[#7C9E8C] bg-[#7C9E8C]/10 text-[#7C9E8C]'
              : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-400 hover:border-[#7C9E8C]/40 hover:text-slate-700 dark:hover:text-white'"
          >
            {{ b.label }}
          </button>
        </div>
      </div>

      <!-- Drop zone -->
      <div>
        <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
          Statement file
        </label>
        <div
          class="relative border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all duration-200"
          :class="zoneClass"
          @dragover.prevent="dragOver = true"
          @dragleave.prevent="dragOver = false"
          @drop.prevent="onDrop"
          @click="fileInput?.click()"
          role="button"
          :aria-label="file ? `${file.name} selected — click to change` : 'Click or drag to upload a statement'"
        >
          <input
            ref="fileInput"
            type="file"
            accept=".pdf,.csv"
            class="hidden"
            @change="onFile"
          />

          <!-- Inner content crossfades between idle and file-selected -->
          <Transition name="zone-content" mode="out-in">

            <!-- File selected state -->
            <div v-if="file" key="selected" class="flex items-center justify-center gap-3">
              <div class="w-10 h-10 rounded-lg bg-[#7C9E8C]/20 flex items-center justify-center shrink-0">
                <svg class="w-5 h-5 text-[#7C9E8C]" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd"/>
                </svg>
              </div>
              <div class="text-left">
                <p class="text-sm font-medium text-slate-900 dark:text-white truncate max-w-[200px]">{{ file.name }}</p>
                <p class="text-xs text-slate-400 mt-0.5">{{ fileSize }} · Click to change</p>
              </div>
            </div>

            <!-- Idle / drag-hover state -->
            <div v-else key="idle">
              <div
                class="w-12 h-12 rounded-xl bg-slate-100 dark:bg-slate-700 flex items-center justify-center mx-auto mb-4 transition-transform duration-200"
                :class="dragOver ? '-translate-y-1.5' : ''"
              >
                <svg class="w-6 h-6 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/>
                </svg>
              </div>
              <p class="text-sm font-medium text-slate-900 dark:text-white mb-1 transition-all duration-150">
                {{ dragOver ? 'Release to upload' : 'Drop your statement here' }}
              </p>
              <p class="text-xs text-slate-500">or click to browse · PDF or CSV · max 10 MB</p>
            </div>

          </Transition>
        </div>
      </div>

      <!-- Validation error (slide-down is already in style.css from login) -->
      <Transition name="slide-down">
        <p
          v-if="errorMsg"
          role="alert"
          class="text-sm text-red-400 bg-red-400/10 border border-red-400/20 rounded-lg px-4 py-3"
        >
          {{ errorMsg }}
        </p>
      </Transition>

      <!-- Submit CTA -->
      <button
        type="submit"
        :disabled="!file"
        class="w-full py-3 rounded-xl text-sm font-semibold transition-all duration-200"
        :class="file
          ? 'bg-[#7C9E8C] hover:bg-[#6a8f7c] text-white cursor-pointer shadow-sm shadow-[#7C9E8C]/30'
          : 'bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-500 cursor-not-allowed'"
      >
        Parse with Claude AI
      </button>

    </form>
  </Transition>
</template>

<script setup>
import { ref, computed } from 'vue'
import { statementsApi } from '@/services/api'
import { useCountUp } from '@/composables/useCountUp'

const emit = defineEmits(['uploaded'])

const BANKS = [
  { label: 'DBS',   value: 'DBS' },
  { label: 'OCBC',  value: 'OCBC' },
  { label: 'UOB',   value: 'UOB' },
  { label: 'Other', value: 'Unknown' },
]

const STEPS = [
  { label: 'Uploading',  description: 'Sending your statement securely' },
  { label: 'Extracting', description: 'Reading tables and rows from the file' },
  { label: 'AI Parsing', description: 'Claude is categorising each transaction' },
  { label: 'Saving',     description: 'Writing entries to your double-entry ledger' },
]

const MAX_SIZE = 10 * 1024 * 1024 // 10 MB — ponytail: native File API, no library

const bank        = ref('DBS')
const file        = ref(null)
const fileInput   = ref(null)
const dragOver    = ref(false)
const phase       = ref('form')       // 'form' | 'processing' | 'success'
const currentStep = ref(-1)
const errorMsg    = ref('')
const txCount     = ref(0)
const displayCount = useCountUp(txCount, 800)

const fileSize = computed(() => {
  if (!file.value) return ''
  const kb = file.value.size / 1024
  return kb >= 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${Math.round(kb)} KB`
})

const zoneClass = computed(() => {
  if (dragOver.value) return 'border-[#7C9E8C] bg-[#7C9E8C]/10 scale-[1.01]'
  if (file.value)     return 'border-[#7C9E8C]/40 bg-[#7C9E8C]/5'
  return 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/50 hover:border-[#7C9E8C]/30 hover:bg-slate-50 dark:hover:bg-slate-800'
})

// ponytail: native File API for validation — PDF MIME type + CSV by extension, size cap
function validateFile(f) {
  if (f.type !== 'application/pdf' && !f.name.toLowerCase().endsWith('.csv')) {
    return 'Only PDF and CSV files are supported'
  }
  if (f.size > MAX_SIZE) return 'File must be under 10 MB'
  return null
}

function onFile(e) {
  const f = e.target.files[0]
  if (!f) return
  const err = validateFile(f)
  if (err) { errorMsg.value = err; return }
  errorMsg.value = ''
  file.value = f
}

function onDrop(e) {
  dragOver.value = false
  const f = e.dataTransfer.files[0]
  if (!f) return
  const err = validateFile(f)
  if (err) { errorMsg.value = err; return }
  errorMsg.value = ''
  file.value = f
}

function reset() {
  phase.value     = 'form'
  file.value      = null
  txCount.value   = 0
  errorMsg.value  = ''
  currentStep.value = -1
  if (fileInput.value) fileInput.value.value = ''
}

async function handleSubmit() {
  if (!file.value) return
  errorMsg.value = ''
  phase.value    = 'processing'
  currentStep.value = 0

  // Optimistic step advancement — AI step holds until the API responds
  const t1 = setTimeout(() => { if (currentStep.value === 0) currentStep.value = 1 }, 1500)
  const t2 = setTimeout(() => { if (currentStep.value <= 1)  currentStep.value = 2 }, 3500)

  try {
    const { data } = await statementsApi.upload(file.value, bank.value)
    clearTimeout(t1)
    clearTimeout(t2)
    currentStep.value = 3
    // Brief hold so step 4 checkmark draws before the phase transitions
    setTimeout(() => {
      txCount.value = data.transactions_imported ?? 0
      phase.value   = 'success'
    }, 700)
  } catch (e) {
    clearTimeout(t1)
    clearTimeout(t2)
    // FastAPI returns the human-readable reason in detail
    errorMsg.value = e.response?.data?.detail ?? e.message
    phase.value    = 'form'
    currentStep.value = -1
  }
}
</script>
