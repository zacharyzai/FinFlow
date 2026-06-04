<template>
  <form class="upload-form" @submit.prevent="handleSubmit">
    <label>
      Bank
      <select v-model="bank">
        <option value="DBS">DBS</option>
        <option value="OCBC">OCBC</option>
        <option value="UOB">UOB</option>
        <option value="Unknown">Other</option>
      </select>
    </label>
    <label>
      Statement file (PDF or CSV)
      <input type="file" accept=".pdf,.csv" @change="onFile" required />
    </label>
    <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
    <button type="submit" :disabled="!file || loading">
      {{ loading ? 'Uploading…' : 'Upload' }}
    </button>
  </form>
</template>

<script setup>
import { ref } from 'vue'
import { statementsApi } from '@/services/api'

const emit = defineEmits(['uploaded'])

const bank = ref('DBS')
const file = ref(null)
const loading = ref(false)
const errorMsg = ref('')

function onFile(e) {
  file.value = e.target.files[0] ?? null
}

async function handleSubmit() {
  if (!file.value) return
  errorMsg.value = ''
  loading.value = true
  try {
    const { data } = await statementsApi.upload(file.value, bank.value)
    emit('uploaded', data)
  } catch (e) {
    errorMsg.value = e.response?.data?.detail ?? e.message
  } finally {
    loading.value = false
  }
}
</script>
