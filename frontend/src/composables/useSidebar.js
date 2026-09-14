import { ref } from 'vue'
import { useStorage } from '@vueuse/core'

// Module-level refs — all components share the same reactive instance
const isOpen = useStorage('finflow-sidebar', true)

// Mobile drawer open/closed state — deliberately NOT persisted (unlike isOpen)
// since it controls a transient overlay, not a layout preference.
const mobileOpen = ref(false)

export function useSidebar() {
  return { isOpen, mobileOpen }
}
