import { defineStore } from 'pinia'
import { ref } from 'vue'
import { statementsApi, apiErrorMessage } from '@/services/api'
import { useToastStore } from './toast'

// Lives in a store (not component state) so an in-flight upload survives
// navigating away from /upload — the request keeps running and this state
// keeps updating regardless of which view is mounted.
export const useUploadJobStore = defineStore('uploadJob', () => {
  const phase = ref('idle')       // 'idle' | 'processing' | 'success' | 'error'
  const currentStep = ref(-1)
  const fileName = ref('')
  const result = ref(null)
  const errorMsg = ref('')

  async function upload(file, bank) {
    fileName.value = file.name
    errorMsg.value = ''
    result.value = null
    phase.value = 'processing'
    currentStep.value = 0

    // Optimistic step advancement — AI step holds until the API responds
    const t1 = setTimeout(() => { if (currentStep.value === 0) currentStep.value = 1 }, 1500)
    const t2 = setTimeout(() => { if (currentStep.value <= 1) currentStep.value = 2 }, 3500)

    const toast = useToastStore()
    try {
      const { data } = await statementsApi.upload(file, bank)
      clearTimeout(t1)
      clearTimeout(t2)
      currentStep.value = 3
      result.value = data
      phase.value = 'success'
      const skipped = data.duplicates_skipped ?? 0
      const skippedNote = skipped > 0 ? ` (${skipped} duplicate${skipped === 1 ? '' : 's'} skipped)` : ''
      toast.push(`Statement parsed — ${data.transactions_imported ?? 0} transactions imported${skippedNote}`, 'success')
    } catch (e) {
      clearTimeout(t1)
      clearTimeout(t2)
      errorMsg.value = apiErrorMessage(e)
      phase.value = 'error'
      toast.push(`Statement upload failed — ${errorMsg.value}`, 'error')
    }
  }

  function reset() {
    phase.value = 'idle'
    currentStep.value = -1
    fileName.value = ''
    result.value = null
    errorMsg.value = ''
  }

  return { phase, currentStep, fileName, result, errorMsg, upload, reset }
})
