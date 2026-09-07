<template>
  <div class="ff-toast-stack">
    <TransitionGroup name="toast">
      <div v-for="t in toastStore.toasts" :key="t.id" class="ff-toast" :class="`ff-toast-${t.type}`">
        <span class="material-symbols-outlined ff-toast-icon">{{ icon(t.type) }}</span>
        <span class="ff-toast-msg">{{ t.message }}</span>
        <button class="ff-toast-close" @click="toastStore.dismiss(t.id)" aria-label="Dismiss">
          <span class="material-symbols-outlined" style="font-size:16px">close</span>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()

function icon(type) {
  if (type === 'success') return 'check_circle'
  if (type === 'error') return 'error'
  return 'info'
}
</script>

<style scoped>
.ff-toast-stack {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 340px;
}
.ff-toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 10px;
  background: var(--surface);
  border: 1px solid var(--border);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  font: 500 13px 'IBM Plex Sans';
  color: var(--text);
}
.ff-toast-icon { font-size: 18px; flex-shrink: 0; }
.ff-toast-success .ff-toast-icon { color: var(--good); }
.ff-toast-error .ff-toast-icon { color: var(--bad); }
.ff-toast-info .ff-toast-icon { color: var(--brand); }
.ff-toast-msg { flex: 1; }
.ff-toast-close {
  background: none;
  border: none;
  color: var(--text-3);
  cursor: pointer;
  display: flex;
  padding: 2px;
}
.ff-toast-close:hover { color: var(--text); }

.toast-enter-active, .toast-leave-active { transition: opacity 200ms ease, transform 200ms ease; }
.toast-enter-from { opacity: 0; transform: translateY(8px); }
.toast-leave-to { opacity: 0; transform: translateX(20px); }
</style>
