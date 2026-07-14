<template>
  <aside class="ff-sidebar" :class="{ 'is-collapsed': !isOpen }">

    <!-- Brand + collapse toggle -->
    <div class="ff-brand-row">
      <FinFlowLogo size="md" :wordmark="isOpen" />
      <button
        class="ff-toggle-btn"
        @click="isOpen = !isOpen"
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
          @click="navigate"
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
        v-for="acc in accounts"
        :key="acc.name"
        class="ff-account-item"
        :title="!isOpen ? `${acc.name} · ${acc.balance}` : undefined"
      >
        <span class="ff-account-dot" :style="`background:${acc.color}`"></span>
        <span class="ff-fade-text ff-account-name">{{ acc.name }}</span>
        <span class="ff-fade-text ff-account-balance">{{ acc.balance }}</span>
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
import { computed } from 'vue'
import { useDark, useToggle } from '@vueuse/core'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { useSidebar } from '@/composables/useSidebar'
import FinFlowLogo from '@/components/FinFlowLogo.vue'

const { isOpen } = useSidebar()
const isDark = useDark()
const toggleDark = useToggle(isDark)
const auth = useAuthStore()
const router = useRouter()

const initials = computed(() => (auth.user?.email ?? '').slice(0, 2).toUpperCase())
const displayName = computed(() => (auth.user?.email ?? '').split('@')[0] || 'You')

async function handleSignOut() {
  await auth.signOut()
  router.push('/login')
}

const NAV = [
  { to: '/dashboard',    label: 'Dashboard',      icon: 'dashboard' },
  { to: '/transactions', label: 'Transactions',    icon: 'receipt_long' },
  { to: '/budget',       label: 'Budget Planner',  icon: 'calendar_month', soon: true },
  { to: '/goals',        label: 'Savings Goals',   icon: 'savings',        soon: true },
  { to: '/health',       label: 'Health Score',    icon: 'monitoring',     soon: true },
  { to: '/upload',       label: 'Statements',      icon: 'description' },
]

// ponytail: hardcoded until accounts store is wired up
const accounts = [
  { name: 'DBS Multiplier', color: 'var(--brand)', balance: '$8,420' },
  { name: 'OCBC 360',       color: 'var(--sage)',  balance: '$3,115' },
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
  height: 100vh;
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
}
.ff-accounts-label { padding-top: 18px; }

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
.ff-account-name { flex: 1; }
.ff-account-balance {
  font: 500 11px 'IBM Plex Mono';
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
.ff-theme-label {
  flex: 1;
  font: 500 13px 'IBM Plex Sans';
  color: var(--text-2);
}
.ff-toggle-track {
  width: 40px;
  height: 22px;
  border-radius: 999px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  position: relative;
  flex-shrink: 0;
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
  transition: background 150ms ease-out, color 150ms ease-out, transform 160ms ease-out;
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
  .ff-nav a {
    transition-duration: 0ms !important;
    animation-duration: 0ms !important;
  }
}
</style>
