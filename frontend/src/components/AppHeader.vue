<template>
  <header class="ff-topbar">
    <div style="display:flex;align-items:center;gap:10px;min-width:0">
      <!-- Menu toggle — mobile only, opens the off-canvas sidebar -->
      <button class="ff-menu-btn" @click="mobileOpen = true" aria-label="Open menu">
        <span class="material-symbols-outlined" style="font-size:22px;line-height:1">menu</span>
      </button>
      <div style="min-width:0">
        <div class="ff-topbar-title">{{ title }}</div>
        <div class="ff-topbar-sub">{{ subtitle }}</div>
      </div>
    </div>
    <div class="ff-topbar-actions">
      <!-- Search — opens command palette. Hidden below 640px; the command
           palette is still reachable via keyboard shortcut on any size. -->
      <div class="ff-search-wrap">
        <span class="material-symbols-outlined ff-search-icon">search</span>
        <input
          placeholder="Search transactions"
          class="ff-search-input"
          @click="paletteOpen = true"
          readonly
        />
      </div>
      <!-- Month picker — dashboard only. Native <select> = keyboard + screen-reader support for free -->
      <label v-if="monthPicker" class="ff-btn-ghost ff-month-picker">
        <span class="material-symbols-outlined" style="font-size:18px;line-height:1">calendar_today</span>
        <select :value="dashboard.selectedMonth ?? monthOptions[0].value" aria-label="Review month" @change="dashboard.selectMonth($event.target.value)">
          <option v-for="o in monthOptions" :key="o.value" :value="o.value">{{ o.label }}</option>
        </select>
      </label>
      <!-- Upload CTA — label hidden below 480px, icon-only button remains -->
      <router-link to="/upload" class="ff-btn-primary">
        <span class="material-symbols-outlined" style="font-size:18px;line-height:1">upload_file</span>
        <span class="ff-btn-label">Upload statement</span>
      </router-link>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { usePalette } from '@/composables/usePalette'
import { useSidebar } from '@/composables/useSidebar'

defineProps({
  title: { type: String, default: 'Dashboard' },
  monthPicker: { type: Boolean, default: false },
})

const { open: paletteOpen } = usePalette()
const { mobileOpen } = useSidebar()

const dashboard = useDashboardStore()

// Current month + the 5 before it — same 6-month window the dashboard trend chart loads
const monthOptions = computed(() => {
  const now = new Date()
  return Array.from({ length: 6 }, (_, i) => {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    return {
      value: `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`,
      label: d.toLocaleString('en-SG', { month: 'long', year: 'numeric' }),
    }
  })
})
</script>

<style scoped>
.ff-topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  min-height: 64px;
  background: var(--bg-blur);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
  padding: 0 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.ff-topbar-title {
  font: 600 18px 'IBM Plex Sans';
  letter-spacing: -.3px;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ff-topbar-sub {
  font: 400 12px 'IBM Plex Sans';
  color: var(--text-3);
  margin-top: 1px;
}
.ff-topbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

/* Menu toggle — only shown below 768px, where the sidebar becomes a drawer */
.ff-menu-btn {
  display: none;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 7px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-2);
  cursor: pointer;
  flex-shrink: 0;
}
@media (max-width: 767px) {
  .ff-menu-btn { display: flex; }
  .ff-topbar { padding: 0 14px; }
}

.ff-search-wrap {
  position: relative;
  display: flex;
  align-items: center;
}
@media (max-width: 639px) {
  .ff-search-wrap { display: none; }
}

@media (max-width: 479px) {
  .ff-btn-label { display: none; }
  .ff-btn-ghost, .ff-btn-primary { padding: 9px; }
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
.ff-month-picker { padding: 0 6px 0 11px; }
.ff-month-picker select {
  border: none;
  background: transparent;
  color: inherit;
  font: inherit;
  padding: 8px 4px;
  cursor: pointer;
  outline: none;
}
.ff-month-picker:focus-within { border-color: var(--brand); }
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
