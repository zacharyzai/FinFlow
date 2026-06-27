import { ref, watch, onUnmounted } from 'vue'

/**
 * Animates a number from its current value to a new target whenever source changes.
 * Returns a reactive ref you can use directly in templates.
 *
 * Emil principle: this is a "data arrived" animation — acceptable because it runs
 * once on load, not on every interaction.
 */
export function useCountUp(source, duration = 900) {
  const display = ref(0)
  let raf

  watch(source, (to) => {
    const from = display.value
    const start = performance.now()
    cancelAnimationFrame(raf)

    function step(now) {
      const t = Math.min((now - start) / duration, 1)
      const eased = 1 - (1 - t) ** 3   // ease-out cubic
      display.value = from + (to - from) * eased
      if (t < 1) raf = requestAnimationFrame(step)
      else display.value = to
    }
    raf = requestAnimationFrame(step)
  }, { immediate: true })

  onUnmounted(() => cancelAnimationFrame(raf))

  return display
}
