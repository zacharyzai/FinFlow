<template>
  <div class="flex min-h-screen bg-slate-50 dark:bg-[#0f1a19]">
    <AppSidebar />
    <div class="flex-1 flex flex-col min-w-0">
      <AppHeader title="Upload Statement" />
      <main class="flex-1 flex items-start justify-center px-6 py-10">
        <div class="w-full max-w-xl" style="animation: fade-up 280ms var(--ease-out) both">
          <div class="mb-8">
            <h1 class="text-xl font-semibold text-slate-900 dark:text-white mb-2">Import your bank statement</h1>
            <p class="text-slate-500 dark:text-slate-400 text-sm leading-relaxed">
              Upload a PDF or CSV export from DBS, OCBC, or UOB.
              Claude AI will read and categorise every transaction —
              <span class="text-[#7C9E8C]">the raw file is deleted immediately after parsing.</span>
            </p>
          </div>
          <UploadStatement @uploaded="router.push('/transactions')" />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'
import UploadStatement from '@/views/UploadStatement.vue'

const router = useRouter()

</script>
