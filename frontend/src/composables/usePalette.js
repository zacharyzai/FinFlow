import { ref } from 'vue'

// Module-level singleton — same pattern as useSidebar
const open = ref(false)

export function usePalette() {
  return { open }
}
