<template>
  <div class="category-chart">
    <h3>Spending by Category</h3>
    <ul>
      <li v-for="(amount, category) in data" :key="category">
        <span class="cat-name">{{ category }}</span>
        <div class="bar-track">
          <div class="bar-fill" :style="{ width: pct(amount) + '%' }" />
        </div>
        <span class="cat-amount">SGD {{ amount.toFixed(2) }}</span>
      </li>
      <li v-if="!Object.keys(data).length">No data yet.</li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({}),
  },
})

const max = computed(() => Math.max(...Object.values(props.data), 1))
const pct = (amount) => Math.round((amount / max.value) * 100)
</script>
