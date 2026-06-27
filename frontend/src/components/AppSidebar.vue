<template>
  <nav
    class="flex flex-col h-screen shrink-0 bg-[#0f1a19] border-r border-white/5 overflow-hidden transition-[width] duration-300 ease-in-out"
    :class="isOpen ? 'w-64' : 'w-16'"
  >
    <!-- Brand -->
    <div
      class="flex items-center h-16 border-b border-white/5 shrink-0 transition-all duration-300"
      :class="isOpen ? 'px-5 gap-3' : 'justify-center px-0'"
    >
      <img src="/images/finflow-logo.svg" alt="FinFlow" class="w-6 h-6 object-contain shrink-0" />
      <span
        class="font-bold text-white tracking-tight whitespace-nowrap transition-opacity duration-200"
        :class="isOpen ? 'opacity-100' : 'opacity-0 w-0 overflow-hidden'"
      >FinFlow</span>
    </div>

    <!-- Nav items -->
    <ul class="flex-1 px-2 py-4 space-y-0.5 overflow-y-auto">
      <li v-for="item in NAV" :key="item.to">
        <router-link
          :to="item.to"
          :title="!isOpen ? item.label : undefined"
          class="flex items-center rounded-lg text-sm font-medium transition-colors duration-150"
          :class="[
            isOpen ? 'gap-3 px-3 py-2.5' : 'justify-center p-3',
            $route.path === item.to
              ? 'bg-[#7C9E8C]/15 text-[#7C9E8C]'
              : 'text-slate-400 hover:bg-white/5 hover:text-white'
          ]"
        >
          <svg
            class="w-5 h-5 shrink-0"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="1.5"
            v-html="item.icon"
          />
          <span
            class="whitespace-nowrap transition-opacity duration-200"
            :class="isOpen ? 'opacity-100' : 'opacity-0 w-0 overflow-hidden'"
          >{{ item.label }}</span>
          <span
            v-if="item.soon && isOpen"
            class="ml-auto text-[9px] font-bold tracking-widest uppercase text-slate-600 bg-slate-800 rounded px-1.5 py-0.5"
          >soon</span>
        </router-link>
      </li>
    </ul>

    <!-- Footer -->
    <div
      class="py-4 border-t border-white/5 shrink-0 overflow-hidden transition-all duration-200"
      :class="isOpen ? 'px-5' : 'flex justify-center px-0'"
    >
      <p v-if="isOpen" class="text-xs text-slate-700 whitespace-nowrap">FinFlow · Singapore</p>
      <div v-else class="w-1.5 h-1.5 rounded-full bg-slate-800" />
    </div>
  </nav>
</template>

<script setup>
import { useSidebar } from '@/composables/useSidebar'

const { isOpen } = useSidebar()

const NAV = [
  {
    to: '/dashboard',
    label: 'Dashboard',
    icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"/>',
  },
  {
    to: '/transactions',
    label: 'Transactions',
    icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M8.25 6.75h12M8.25 12h12m-12 5.25h12M3.75 6.75h.007v.008H3.75V6.75zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zM3.75 12h.007v.008H3.75V12zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm-.375 5.25h.007v.008H3.75v-.008zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z"/>',
  },
  {
    to: '/upload',
    label: 'Upload',
    icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/>',
  },
  {
    to: '/budget',
    label: 'Budget',
    soon: true,
    icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75"/>',
  },
  {
    to: '/health',
    label: 'Health Score',
    soon: true,
    icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"/>',
  },
  {
    to: '/goals',
    label: 'Goals',
    soon: true,
    icon: '<path stroke-linecap="round" stroke-linejoin="round" d="M3 3v1.5M3 21v-6m0 0l2.77-.693a9 9 0 016.208.682l.108.054a9 9 0 006.086.71l3.114-.732a48.524 48.524 0 01-.005-10.499l-3.11.732a9 9 0 01-6.085-.711l-.108-.054a9 9 0 00-6.208-.682L3 4.5M3 15V4.5"/>',
  },
]
</script>

<style scoped>
/* Stagger nav items on mount — plays once since sidebar stays mounted across routes */
li { animation: fade-up 220ms var(--ease-out) both; }
li:nth-child(1) { animation-delay: 30ms; }
li:nth-child(2) { animation-delay: 60ms; }
li:nth-child(3) { animation-delay: 90ms; }
li:nth-child(4) { animation-delay: 120ms; }
li:nth-child(5) { animation-delay: 150ms; }
li:nth-child(6) { animation-delay: 180ms; }
</style>
