<template>
  <RouterView v-slot="{ Component }">
    <Transition name="page" mode="out-in">
      <component :is="Component" :key="$route.path" />
    </Transition>
  </RouterView>
  <CommandPalette :open="paletteOpen" @close="paletteOpen = false" />
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import CommandPalette from '@/components/CommandPalette.vue'
import { usePalette } from '@/composables/usePalette'

const { open: paletteOpen } = usePalette()

function onKeydown(e) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    paletteOpen.value = !paletteOpen.value
  }
}

onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))
</script>
