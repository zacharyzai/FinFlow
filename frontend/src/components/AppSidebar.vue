<template>
  <!-- Backdrop — mobile only, dismisses the drawer on outside tap -->
  <div v-if="mobileOpen" class="ff-backdrop" @click="mobileOpen = false"></div>

  <aside class="ff-sidebar" :class="{ 'is-collapsed': !isOpen, 'is-mobile-open': mobileOpen }">

    <!-- Brand + collapse toggle -->
    <div class="ff-brand-row">
      <FinFlowLogo size="md" :wordmark="isOpen" />
      <button
        class="ff-toggle-btn"
        @click="isOpen = !isOpen; mobileOpen = false"
        :aria-label="isOpen ? 'Collapse sidebar' : 'Expand sidebar'"
        :title="isOpen ? 'Collapse' : 'Expand'"
      >
        <span class="material-symbols-outlined ff-toggle-icon">chevron_left</span>
      </button>
    </div>

    <!-- Workspace nav -->
    <div class="ff-section-label ff-fade-text">Workspace</div>
    <nav class="ff-nav">
      <router-link
        v-for="(item, i) in NAV"
        :key="item.to"
        :to="item.to"
        custom
        v-slot="{ isActive, navigate }"
      >
        <a
          @click="navigate(); mobileOpen = false"
          class="ff-nav-link"
          :class="isActive ? 'ff-nav-active' : 'ff-nav-inactive'"
          :title="!isOpen ? item.label : undefined"
          :style="`animation-delay: ${i * 30}ms`"
        >
          <span class="material-symbols-outlined ff-nav-icon">{{ item.icon }}</span>
          <span class="ff-fade-text ff-nav-label">{{ item.label }}</span>
          <span v-if="item.soon" class="ff-soon-badge ff-fade-text">soon</span>
        </a>
      </router-link>
    </nav>

    <!-- Accounts -->
    <div class="ff-section-label ff-fade-text ff-accounts-label">Accounts</div>
    <div class="ff-accounts">
      <div
        v-for="acc in accountsStore.accounts"
        :key="acc.id"
        class="ff-account-item"
        :title="!isOpen ? `${acc.name} · ${formatBalance(acc.balance)}` : undefined"
      >
        <span class="ff-account-dot" :style="`background:${acc.color}`"></span>

        <input
          v-if="editingAccountId === acc.id"
          v-model="editName"
          ref="editInput"
          class="ff-fade-text ff-account-name-input"
          @keydown.enter="saveRename(acc.id)"
          @keydown.escape="editingAccountId = null"
          @blur="saveRename(acc.id)"
        />
        <span v-else class="ff-fade-text ff-account-name">{{ acc.name }}</span>

        <span class="ff-fade-text ff-account-balance">{{ formatBalance(acc.balance) }}</span>

        <button
          v-if="editingAccountId !== acc.id"
          class="ff-fade-text ff-account-edit-btn"
          title="Rename account"
          @click="startRename(acc)"
        >
          <span class="material-symbols-outlined" style="font-size:14px">edit</span>
        </button>
      </div>
      <div v-if="!accountsStore.loading && accountsStore.accounts.length === 0" class="ff-fade-text ff-account-empty">
        No accounts yet
      </div>
    </div>

    <div class="ff-spacer"></div>

    <!-- Theme toggle -->
    <div
      @click="toggleDark()"
      role="button"
      class="ff-nav-link ff-theme-row"
      :title="!isOpen ? (isDark ? 'Switch to light' : 'Switch to dark') : undefined"
    >
      <span class="material-symbols-outlined ff-nav-icon">{{ isDark ? 'dark_mode' : 'light_mode' }}</span>
      <span class="ff-fade-text ff-theme-label">{{ isDark ? 'Dark' : 'Light' }} mode</span>
      <div class="ff-toggle-track ff-fade-text">
        <div class="ff-toggle-knob" :class="{ 'is-on': isDark }"></div>
      </div>
    </div>

    <!-- User profile -->
    <div class="ff-user-row">
      <div
        class="ff-avatar"
        :title="!isOpen ? (auth.user?.email ?? '') : undefined"
      >{{ initials }}</div>
      <div class="ff-fade-text ff-user-info">
        <div class="ff-user-name">{{ displayName }}</div>
        <div class="ff-user-email">{{ auth.user?.email }}</div>
      </div>
      <button
        @click="handleSignOut"
        title="Sign out"
        class="ff-icon-btn ff-fade-text"
        aria-label="Sign out"
      >
        <span class="material-symbols-outlined" style="font-size:19px;line-height:1">logout</span>
      </button>
    </div>

  </aside>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useDark, useToggle } from '@vueuse/core'
import { useAuthStore } from '@/stores/auth'
import { useAccountsStore } from '@/stores/accounts'
import { useToastStore } from '@/stores/toast'
import { useRouter } from 'vue-router'
import { useSidebar } from '@/composables/useSidebar'
import FinFlowLogo from '@/components/FinFlowLogo.vue'

const { isOpen, mobileOpen } = useSidebar()
const toast = useToastStore()

const editingAccountId = ref(null)
const editName = ref('')
const editInput = ref(null)

function startRename(acc) {
  editingAccountId.value = acc.id
  editName.value = acc.name
  nextTick(() => editInput.value?.[0]?.focus?.() ?? editInput.value?.focus?.())
}

async function saveRename(id) {
  if (editingAccountId.value !== id) return // already saved/cancelled (blur firing after Enter)
  const name = editName.value.trim()
  editingAccountId.value = null
  if (!name) return

  try {
    await accountsStore.rename(id, name)
  } catch (e) {
    toast.push('Failed to rename account', 'error')
  }
}
const isDark = useDark()
const toggleDark = useToggle(isDark)
const auth = useAuthStore()
const accountsStore = useAccountsStore()
const router = useRouter()

onMounted(() => accountsStore.fetch())

function formatBalance(n) {
  return new Intl.NumberFormat('en-SG', { style: 'currency', currency: 'SGD', maximumFractionDigits: 0 }).format(n)
}

const initials = computed(() => (auth.user?.email ?? '').slice(0, 2).toUpperCase())
const displayName = computed(() => (auth.user?.email ?? '').split('@')[0] || 'You')

async function handleSignOut() {
  await auth.signOut()
  router.push('/login')
}

const NAV = [
  { to: '/dashboard',    label: 'Dashboard',      icon: 'dashboard' },
  { to: '/transactions', label: 'Transactions',    icon: 'receipt_long' },
  { to: '/budget',       label: 'Budget Planner',  icon: 'calendar_month' },
  { to: '/goals',        label: 'Savings Goals',   icon: 'savings' },
  { to: '/health',       label: 'Health Score',    icon: 'monitoring' },
  { to: '/upload',       label: 'Statements',      icon: 'description' },
  { to: '/settings',     label: 'Settings',        icon: 'settings' },
]

</script>

<style scoped>
/* ─── Custom easing ─────────────────────────────────── */
/* iOS-like drawer curve — from Ionic Framework */
:root { --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1); }

/* ─── Sidebar shell ─────────────────────────────────── */
.ff-sidebar {
  width: 248px;
  flex-shrink: 0;
  background: var(--surface);
  border-right: 1px solid var(--border);
  position: sticky;
  top: 0;
  height: 100dvh;
  display: flex;
  flex-direction: column;
  padding: 18px 14px;
  overflow: hidden;          /* clips text during width collapse      */

  /* Width animates with the drawer curve */
  transition: width 280ms var(--ease-drawer), padding 280ms var(--ease-drawer);
}
.ff-sidebar.is-collapsed {
  width: 64px;
  padding: 18px 10px;
}

/* ─── Mobile: off-canvas drawer instead of a permanent rail ─────── */
/* Below 768px the sidebar takes no layout space at all — it overlays
   the page and slides in only when opened via AppHeader's menu button. */
@media (max-width: 767px) {
  .ff-sidebar {
    position: fixed;
    inset: 0 auto 0 0;
    z-index: 50;
    width: 248px;
    padding: 18px 14px;
    transform: translateX(-100%);
    transition: transform 280ms var(--ease-drawer);
  }
  /* Ignore the desktop collapsed-rail state on mobile — mobile is
     either fully hidden or fully open, never an icon-only rail. */
  .ff-sidebar.is-collapsed {
    width: 248px;
    padding: 18px 14px;
  }
  .ff-sidebar.is-collapsed .ff-fade-text {
    opacity: 1;
    pointer-events: auto;
  }
  .ff-sidebar.is-mobile-open {
    transform: translateX(0);
  }
}

.ff-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 40;
}
@media (min-width: 768px) {
  .ff-backdrop { display: none; }
}

/* ─── Text that fades out on collapse ───────────────── */
/* Exits at 150ms — finishes before width collapses, so nothing gets visually clipped */
.ff-fade-text {
  transition: opacity 150ms ease-out;
  white-space: nowrap;
  overflow: hidden;
}
.ff-sidebar.is-collapsed .ff-fade-text {
  opacity: 0;
  pointer-events: none;
}

/* ─── Brand row ─────────────────────────────────────── */
.ff-brand-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 2px 16px;
  transition: justify-content 280ms var(--ease-drawer);
}
.ff-sidebar.is-collapsed .ff-brand-row {
  flex-direction: column;
  gap: 10px;
  align-items: center;
  justify-content: center;
}

/* Toggle button */
.ff-toggle-btn {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-3);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 150ms ease-out, color 150ms ease-out, transform 160ms ease-out;
}
.ff-toggle-btn:hover { background: var(--surface-3); color: var(--text); }
.ff-toggle-btn:active { transform: scale(0.93); }

/* Chevron rotates 180° when collapsed */
.ff-toggle-icon {
  font-size: 18px;
  line-height: 1;
  transition: transform 280ms var(--ease-drawer);
}
.ff-sidebar.is-collapsed .ff-toggle-icon {
  transform: rotate(-180deg);
}

/* ─── Section labels ────────────────────────────────── */
.ff-section-label {
  font: 600 10px 'IBM Plex Sans';
  letter-spacing: .08em;
  color: var(--text-3);
  text-transform: uppercase;
  padding: 8px 10px 6px;
  overflow: hidden;
  transition: opacity 150ms ease-out, padding 280ms var(--ease-drawer), max-height 280ms var(--ease-drawer);
  max-height: 40px;
  white-space: nowrap;
}
.ff-accounts-label { padding-top: 18px; }

/* Collapse section labels when sidebar is closed */
.ff-sidebar.is-collapsed .ff-section-label {
  max-height: 0;
  padding: 0;
  opacity: 0;
}

/* Hide accounts list entirely when collapsed — dots alone aren't useful */
.ff-sidebar.is-collapsed .ff-accounts {
  display: none;
}

/* ─── Nav ───────────────────────────────────────────── */
.ff-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.ff-nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 11px;
  border-radius: 7px;
  text-decoration: none;
  cursor: pointer;
  font-size: 13.5px;
  position: relative;

  /* Emil: transitions on specific props only */
  transition: background 150ms ease-out, color 150ms ease-out, transform 160ms ease-out, padding 280ms var(--ease-drawer), gap 280ms var(--ease-drawer);
}
.ff-nav-active  { background: var(--surface-2); color: var(--text); font-weight: 600; }
.ff-nav-inactive { color: var(--text-2); font-weight: 500; }
.ff-nav-link:hover { background: var(--surface-3); color: var(--text); }

/* Emil: buttons must feel responsive — press feedback */
.ff-nav-link:active { transform: scale(0.97); }

/* Center icon when collapsed */
.ff-sidebar.is-collapsed .ff-nav-link {
  justify-content: center;
  padding: 9px;
  gap: 0;
}

/* Stagger nav items on mount */
.ff-nav a {
  animation: ff-fade-up 220ms var(--ease-out, cubic-bezier(0.23, 1, 0.32, 1)) both;
}
.ff-nav a:nth-child(1) { animation-delay: 30ms; }
.ff-nav a:nth-child(2) { animation-delay: 60ms; }
.ff-nav a:nth-child(3) { animation-delay: 90ms; }
.ff-nav a:nth-child(4) { animation-delay: 120ms; }
.ff-nav a:nth-child(5) { animation-delay: 150ms; }
.ff-nav a:nth-child(6) { animation-delay: 180ms; }

@keyframes ff-fade-up {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

.ff-nav-icon {
  font-size: 20px;
  line-height: 1;
  flex-shrink: 0;
}
.ff-nav-label { flex: 1; }
.ff-soon-badge {
  font: 700 9px 'IBM Plex Sans';
  letter-spacing: .06em;
  text-transform: uppercase;
  color: var(--text-3);
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1px 5px;
}

/* ─── Accounts ──────────────────────────────────────── */
.ff-accounts { display: flex; flex-direction: column; gap: 2px; }
.ff-account-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 11px;
  border-radius: 7px;
  font: 500 13px 'IBM Plex Sans';
  color: var(--text-2);
  transition: padding 280ms var(--ease-drawer), gap 280ms var(--ease-drawer);
}
.ff-sidebar.is-collapsed .ff-account-item {
  justify-content: center;
  padding: 8px;
  gap: 0;
}
.ff-account-dot {
  width: 7px;
  height: 7px;
  border-radius: 2px;
  flex-shrink: 0;
}
.ff-account-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ff-account-name-input {
  flex: 1;
  min-width: 0;
  font: 500 13px 'IBM Plex Sans';
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--brand);
  border-radius: 5px;
  padding: 1px 5px;
  outline: none;
}
.ff-account-balance {
  font: 500 11px 'IBM Plex Mono';
  color: var(--text-3);
}
.ff-account-edit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  border-radius: 5px;
  color: var(--text-3);
  opacity: 0;
  transition: opacity 150ms ease-out;
  cursor: pointer;
}
.ff-account-item:hover .ff-account-edit-btn { opacity: 1; }
.ff-account-edit-btn:hover { color: var(--text); background: var(--surface-3); }
.ff-account-empty {
  padding: 8px 11px;
  font: 400 12px 'IBM Plex Sans';
  color: var(--text-3);
}

/* ─── Spacer ────────────────────────────────────────── */
.ff-spacer { flex: 1; }

/* ─── Theme toggle ──────────────────────────────────── */
.ff-theme-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}
.ff-sidebar.is-collapsed .ff-theme-row {
  justify-content: center;
}
.ff-sidebar.is-collapsed .ff-theme-label {
  flex: 0;
  width: 0;
}
.ff-sidebar.is-collapsed .ff-toggle-track {
  width: 0;
  overflow: hidden;
}
.ff-theme-label {
  flex: 1;
  font: 500 13px 'IBM Plex Sans';
  color: var(--text-2);
  transition: flex 280ms var(--ease-drawer), width 280ms var(--ease-drawer), opacity 150ms ease-out;
  overflow: hidden;
  white-space: nowrap;
}
.ff-toggle-track {
  width: 40px;
  height: 22px;
  border-radius: 999px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  position: relative;
  flex-shrink: 0;
  transition: width 280ms var(--ease-drawer), opacity 150ms ease-out;
}
.ff-toggle-knob {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--brand);
  transition: left 220ms ease;
}
.ff-toggle-knob.is-on { left: 20px; }

/* ─── User row ──────────────────────────────────────── */
.ff-user-row {
  border-top: 1px solid var(--border);
  padding-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: gap 280ms var(--ease-drawer);
}
.ff-sidebar.is-collapsed .ff-user-row {
  justify-content: center;
  gap: 0;
}
.ff-sidebar.is-collapsed .ff-icon-btn {
  width: 0;
  padding: 0;
  border: none;
  overflow: hidden;
}
.ff-avatar {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: var(--brand);
  color: var(--on-brand);
  display: flex;
  align-items: center;
  justify-content: center;
  font: 600 12px 'IBM Plex Mono';
  flex-shrink: 0;
}
.ff-user-info {
  min-width: 0;
  flex: 1;
}
.ff-user-name {
  font: 600 13px 'IBM Plex Sans';
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ff-user-email {
  font: 400 11px 'IBM Plex Sans';
  color: var(--text-3);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ff-icon-btn {
  width: 32px;
  height: 32px;
  border-radius: 7px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 150ms ease-out, color 150ms ease-out, transform 160ms ease-out, width 280ms var(--ease-drawer), padding 280ms var(--ease-drawer), border 280ms var(--ease-drawer);
}
.ff-icon-btn:hover { background: var(--surface-3); color: var(--text); }
.ff-icon-btn:active { transform: scale(0.93); }

/* ─── Reduced motion ────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
  .ff-sidebar,
  .ff-fade-text,
  .ff-nav-link,
  .ff-toggle-btn,
  .ff-toggle-icon,
  .ff-account-item,
  .ff-toggle-knob,
  .ff-icon-btn,
  .ff-section-label,
  .ff-nav a {
    transition-duration: 0ms !important;
    animation-duration: 0ms !important;
  }
}
</style>
