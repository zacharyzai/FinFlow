import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const toasts = ref([])
  let nextId = 0

  function push(message, type = 'info') {
    const id = ++nextId
    toasts.value.push({ id, message, type })
    setTimeout(() => dismiss(id), 5000)
  }

  function dismiss(id) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  return { toasts, push, dismiss }
})
