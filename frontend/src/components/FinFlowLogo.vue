<template>
  <div class="ff-logo" :style="`gap:${cfg.gap}`">
    <!-- Inline SVG from /public/images/finflow-logo.svg — scales cleanly at all sizes -->
    <svg
      xmlns="http://www.w3.org/2000/svg"
      :width="cfg.markW"
      :height="cfg.markH"
      viewBox="0 0 72 68"
      aria-hidden="true"
      style="flex-shrink:0"
    >
      <g fill="none">
        <path d="M0 33.82 l0 -33.82 36 0 36 0 0 33.82 0 33.82 -36 0 -36 0 0 -33.82z m45.78 10.66 c0.78 -1.53 1.92 -3.74 2.52 -4.91 l1.09 -2.13 3.05 0 3.04 0 0.93 -1.82 c0.51 -1.01 1.38 -2.70 1.93 -3.77 2.73 -5.35 5.14 -10.08 5.14 -10.12 0 -0.02 -8.38 -0.03 -18.62 -0.03 l-18.63 0.02 -1.26 2.45 c-0.69 1.35 -1.83 3.57 -2.54 4.94 l-1.28 2.49 -3.04 0.03 -3.05 0.03 -0.29 0.55 c-0.16 0.30 -1.13 2.19 -2.15 4.19 -2.59 5.07 -3.28 6.42 -4.48 8.75 -0.58 1.11 -1.05 2.04 -1.05 2.06 0 0.02 8.39 0.03 18.63 0.03 l18.63 0 1.42 -2.78z"/>
      </g>
      <g fill="#334644">
        <path d="M18.75 36.86 c0 -0.17 0.26 -0.74 0.91 -2 3.89 -7.51 4.71 -9.09 5.64 -10.88 l1.05 -2.03 18.29 0 18.29 0 0 0.21 c0 0.14 -0.35 0.90 -1.03 2.24 -0.57 1.11 -1.47 2.86 -1.99 3.89 -1.62 3.17 -3.72 7.29 -4.13 8.06 l-0.38 0.74 -18.32 0 -18.33 0 0 -0.23z"/>
      </g>
      <g fill="#809989">
        <path d="M7.64 46.75 c0 -0.14 0.21 -0.62 0.62 -1.41 0.34 -0.65 1.98 -3.86 3.65 -7.13 1.67 -3.26 3.10 -6.01 3.17 -6.12 l0.13 -0.18 2.76 0 2.75 0 0 0.25 c0 0.25 -0.20 0.65 -2.03 4.17 l-0.57 1.10 15.41 0 15.42 0 0 0.22 c0 0.12 -0.03 0.25 -0.06 0.29 -0.03 0.03 -0.76 1.44 -1.62 3.13 -0.86 1.68 -1.88 3.70 -2.28 4.47 l-0.72 1.40 -18.32 0.02 -18.33 0.01 0 -0.22z"/>
      </g>
      <g fill="#12131b">
        <path d="M6.68 47.45 c0 -0.04 0.53 -1.11 1.19 -2.37 1.38 -2.69 2.03 -3.96 4.55 -8.88 1.02 -2 1.99 -3.89 2.15 -4.19 l0.29 -0.55 3.05 -0.03 3.04 -0.03 1.28 -2.49 c0.70 -1.37 1.85 -3.59 2.54 -4.94 l1.26 -2.45 18.98 -0.02 18.97 -0.01 -0.17 0.29 c-0.09 0.16 -1.09 2.11 -2.22 4.32 -1.13 2.22 -2.50 4.90 -3.04 5.97 -0.55 1.07 -1.42 2.76 -1.93 3.77 l-0.93 1.82 -3.04 0 -3.05 0 -1.09 2.13 c-0.60 1.17 -1.73 3.38 -2.52 4.91 l-1.42 2.78 -18.78 0 c-10.33 0 -18.85 0.02 -18.93 0.04 -0.10 0.03 -0.16 0.01 -0.16 -0.04z m38.11 -2.11 c0.40 -0.77 1.42 -2.78 2.28 -4.47 0.86 -1.69 1.59 -3.11 1.63 -3.15 0.05 -0.07 -3.05 -0.09 -15.46 -0.09 l-15.52 0 0.73 -1.41 c0.40 -0.78 1.03 -2 1.40 -2.72 0.38 -0.72 0.68 -1.33 0.68 -1.35 0 -0.02 -1.15 -0.04 -2.55 -0.04 l-2.56 0 -0.13 0.19 c-0.08 0.10 -1.50 2.86 -3.17 6.12 -1.67 3.27 -3.31 6.47 -3.65 7.13 -0.34 0.65 -0.62 1.20 -0.62 1.21 0 0.01 8.15 0.01 18.12 0.01 l18.12 -0.02 0.72 -1.40z m10.78 -9.19 c0.41 -0.77 2.52 -4.89 4.13 -8.06 0.52 -1.03 1.42 -2.79 1.99 -3.90 l1.04 -2.03 -18.09 0 -18.09 0 -1.05 2.03 c-0.93 1.79 -1.75 3.36 -5.64 10.88 -0.50 0.97 -0.91 1.77 -0.91 1.79 0 0.01 8.15 0.03 18.12 0.03 l18.12 0 0.38 -0.74z"/>
      </g>
    </svg>

    <span v-if="wordmark" :style="`font-size:${cfg.fontSize};font-weight:700;letter-spacing:-.3px;color:${wordmarkColor}`">
      FinFlow
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useDark } from '@vueuse/core'

const props = defineProps({
  /** 'light' | 'dark' | 'auto' — controls wordmark colour only */
  variant: { type: String, default: 'auto' },
  /** 'sm' | 'md' | 'lg' */
  size: { type: String, default: 'md' },
  /** hide the "FinFlow" text — useful in collapsed sidebars */
  wordmark: { type: Boolean, default: true },
})

const isDark = useDark()

const wordmarkColor = computed(() => {
  const dark = props.variant === 'auto' ? isDark.value : props.variant === 'dark'
  return dark ? '#FFFFFF' : '#1A1A2E'
})

const cfg = computed(() => {
  switch (props.size) {
    case 'sm': return { markW: 20, markH: 19, gap: '8px',  fontSize: '14px' }
    case 'lg': return { markW: 40, markH: 38, gap: '14px', fontSize: '24px' }
    default:   return { markW: 28, markH: 26, gap: '10px', fontSize: '18px' }
  }
})
</script>

<style scoped>
.ff-logo {
  display: flex;
  align-items: center;
}
</style>
