import { useStorage } from '@vueuse/core'

// Module-level ref — all components share the same reactive instance
const isOpen = useStorage('finflow-sidebar', true)

export function useSidebar() {
  return { isOpen }
}
