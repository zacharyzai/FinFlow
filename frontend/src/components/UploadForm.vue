<template>
  <!-- Progress overlay while parsing -->
  <div v-if="loading" class="bg-white dark:bg-[#1a2e2b] border border-slate-200 dark:border-[#7C9E8C]/20 rounded-2xl p-8">
    <p class="text-slate-900 dark:text-white font-semibold mb-1">Processing your statement…</p>
    <p class="text-slate-500 dark:text-slate-400 text-sm mb-8">This can take 10–15 seconds while Claude reads each transaction.</p>
    <div class="space-y-5">
      <div v-for="(step, i) in STEPS" :key="step.label" class="flex items-center gap-4">
        <div
          class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 transition-all duration-300"
          :class="stepCircleClass(i)"
        >
          <!-- Done -->
          <svg v-if="i < currentStep" class="w-4 h-4" viewBox="0 0 16 16" fill="none">
            <path d="M3 8l3.5 3.5L13 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <!-- Active spinner -->
          <svg v-else-if="i === currentStep" class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          <!-- Pending -->
          <div v-else class="w-2 h-2 rounded-full bg-slate-400 dark:bg-slate-500" />
        </div>
        <div>
          <p class="text-sm font-medium transition-colors" :class="i <= currentStep ? 'text-slate-900 dark:text-white' : 'text-slate-400 dark:text-slate-500'">
            {{ step.label }}
          </p>
          <p class="text-xs text-slate-500">{{ step.description }}</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Upload form -->
  <form v-else @submit.prevent="handleSubmit" class="space-y-6">
    <!-- Bank selector -->
    <div>
      <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">Bank</label>
      <div class="grid grid-cols-4 gap-2">
        <button
          v-for="b in BANKS"
          :key="b.value"
          type="button"
          @click="bank = b.value"
          class="py-2.5 rounded-lg border text-sm font-medium transition-all"
          :class="bank === b.value
            ? 'border-[#7C9E8C] bg-[#7C9E8C]/10 text-[#7C9E8C]'
            : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-600 hover:text-slate-700 dark:hover:text-white'"
        >
          {{ b.label }}
        </button>
      </div>
    </div>

    <!-- Drop zone -->
    <div>
      <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">Statement file</label>
      <div
        class="relative border-2 border-dashed rounded-xl p-10 text-center transition-all cursor-pointer"
        :class="dragOver
          ? 'border-[#7C9E8C] bg-[#7C9E8C]/10'
          : file
            ? 'border-[#7C9E8C]/50 bg-[#7C9E8C]/5'
            : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/50 hover:border-slate-300 dark:hover:border-slate-600'"
        @dragover.prevent="dragOver = true"
        @dragleave="dragOver = false"
        @drop.prevent="onDrop"
        @click="fileInput?.click()"
      >
        <input ref="fileInput" type="file" accept=".pdf,.csv" class="hidden" @change="onFile" />

        <!-- File selected state -->
        <template v-if="file">
          <div class="flex items-center justify-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-[#7C9E8C]/20 flex items-center justify-center shrink-0">
              <svg class="w-5 h-5 text-[#7C9E8C]" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd"/>
              </svg>
            </div>
            <div class="text-left">
              <p class="text-sm font-medium text-slate-900 dark:text-white truncate max-w-xs">{{ file.name }}</p>
              <p class="text-xs text-slate-400 mt-0.5">{{ fileSize }} · Click to change</p>
            </div>
          </div>
        </template>

        <!-- Empty state -->
        <template v-else>
          <div class="w-12 h-12 rounded-xl bg-slate-100 dark:bg-slate-700 flex items-center justify-center mx-auto mb-4">
            <svg class="w-6 h-6 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/>
            </svg>
          </div>
          <p class="text-sm font-medium text-slate-900 dark:text-white mb-1">Drop your statement here</p>
          <p class="text-xs text-slate-500">or click to browse · PDF or CSV · DBS, OCBC, UOB</p>
        </template>
      </div>
    </div>

    <!-- Error message -->
    <p v-if="errorMsg" class="text-sm text-red-400 bg-red-400/10 border border-red-400/20 rounded-lg px-4 py-3">
      {{ errorMsg }}
    </p>

    <!-- Submit -->
    <button
      type="submit"
      :disabled="!file"
      class="w-full py-3 rounded-xl text-sm font-semibold transition-all"
      :class="file
        ? 'bg-[#7C9E8C] hover:bg-[#6a8f7c] text-white cursor-pointer'
        : 'bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-500 cursor-not-allowed'"
    >
      Parse with Claude AI
    </button>
  </form>
</template>

<script setup>
import { ref, computed } from 'vue'
import { statementsApi } from '@/services/api'

const emit = defineEmits(['uploaded'])

const BANKS = [
  { label: 'DBS', value: 'DBS' },
  { label: 'OCBC', value: 'OCBC' },
  { label: 'UOB', value: 'UOB' },
  { label: 'Other', value: 'Unknown' },
]

const STEPS = [
  { label: 'Uploading', description: 'Sending your statement securely' },
  { label: 'Extracting', description: 'Reading tables and rows from the file' },
  { label: 'AI Parsing', description: 'Claude is categorising each transaction' },
  { label: 'Saving', description: 'Writing entries to your ledger' },
]

const bank = ref('DBS')
const file = ref(null)
const fileInput = ref(null)
const dragOver = ref(false)
const loading = ref(false)
const currentStep = ref(-1)
const errorMsg = ref('')

const fileSize = computed(() => {
  if (!file.value) return ''
  const kb = file.value.size / 1024
  return kb >= 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${Math.round(kb)} KB`
})

function stepCircleClass(i) {
  return i <= currentStep.value ? 'bg-[#7C9E8C]/20 text-[#7C9E8C]' : 'bg-slate-100 dark:bg-slate-700 text-slate-400 dark:text-slate-500'
}

function onFile(e) {
  file.value = e.target.files[0] ?? null
}

function onDrop(e) {
  dragOver.value = false
  const dropped = e.dataTransfer.files[0]
  if (dropped && (dropped.type === 'application/pdf' || dropped.name.endsWith('.csv'))) {
    file.value = dropped
  }
}

async function handleSubmit() {
  if (!file.value) return
  errorMsg.value = ''
  loading.value = true
  currentStep.value = 0

  // Advance steps optimistically — stays at step 2 (AI Parsing) until the API responds
  const t1 = setTimeout(() => { if (currentStep.value === 0) currentStep.value = 1 }, 1500)
  const t2 = setTimeout(() => { if (currentStep.value <= 1) currentStep.value = 2 }, 3500)

  try {
    const { data } = await statementsApi.upload(file.value, bank.value)
    clearTimeout(t1)
    clearTimeout(t2)
    currentStep.value = 3
    setTimeout(() => emit('uploaded', data), 900)
  } catch (e) {
    clearTimeout(t1)
    clearTimeout(t2)
    errorMsg.value = e.response?.data?.detail ?? e.message
    loading.value = false
    currentStep.value = -1
  }
}
</script>
