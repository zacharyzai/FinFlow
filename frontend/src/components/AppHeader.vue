<template>
  <header class="ff-topbar">
    <div>
      <div class="ff-topbar-title">{{ title }}</div>
      <div class="ff-topbar-sub">{{ subtitle }}</div>
    </div>
    <div style="display:flex;align-items:center;gap:10px">
      <!-- Search — opens command palette -->
      <div style="position:relative;display:flex;align-items:center">
        <span class="material-symbols-outlined ff-search-icon">search</span>
        <input
          placeholder="Search transactions"
          class="ff-search-input"
          @click="paletteOpen = true"
          readonly
        />
      </div>
      <!-- Month filter -->
      <button class="ff-btn-ghost">
        <span class="material-symbols-outlined" style="font-size:18px;line-height:1">calendar_today</span>
        {{ currentMonth }}
      </button>
      <!-- Upload CTA -->
      <router-link to="/upload" class="ff-btn-primary">
        <span class="material-symbols-outlined" style="font-size:18px;line-height:1">upload_file</span>
        Upload statement
      </router-link>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { usePalette } from '@/composables/usePalette'

defineProps({ title: { type: String, default: 'Dashboard' } })

const { open: paletteOpen } = usePalette()

const currentMonth = computed(() =>
  new Date().toLocaleString('en-SG', { month: 'long' })
)
</script>

<style scoped>
.ff-topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  height: 64px;
  background: var(--bg-blur);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
  padding: 0 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.ff-topbar-title {
  font: 600 18px 'IBM Plex Sans';
  letter-spacing: -.3px;
  color: var(--text);
}
.ff-topbar-sub {
  font: 400 12px 'IBM Plex Sans';
  color: var(--text-3);
  margin-top: 1px;
}
.ff-search-icon {
  position: absolute;
  left: 10px;
  font-size: 18px;
  color: var(--text-3);
  pointer-events: none;
}
.ff-search-input {
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: 8px 12px 8px 34px;
  font: 400 13px 'IBM Plex Sans';
  width: 210px;
  background: var(--surface);
  color: var(--text);
  outline: none;
  cursor: pointer;
}
.ff-search-input:focus { border-color: var(--brand); }
.ff-btn-ghost {
  display: flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-2);
  border-radius: 7px;
  padding: 8px 11px;
  font: 500 13px 'IBM Plex Sans';
  cursor: pointer;
}
.ff-btn-ghost:hover { background: var(--surface-3); color: var(--text); }
.ff-btn-primary {
  display: flex;
  align-items: center;
  gap: 7px;
  border: none;
  background: var(--brand);
  color: var(--on-brand);
  border-radius: 7px;
  padding: 9px 14px;
  font: 600 13px 'IBM Plex Sans';
  cursor: pointer;
  text-decoration: none;
}
.ff-btn-primary:hover { background: var(--brand-strong); }
</style>
