<template>
  <div class="layout">
    <AppSidebar />
    <main>
      <AppHeader title="Upload Statement" />
      <UploadForm @uploaded="handleUploaded" />
      <p v-if="successMsg" class="success">{{ successMsg }}</p>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'
import UploadForm from '@/components/UploadForm.vue'

const router = useRouter()
const successMsg = ref('')

function handleUploaded(result) {
  successMsg.value = `Imported ${result.transactions_imported} transactions successfully.`
  setTimeout(() => router.push('/transactions'), 2000)
}
</script>
