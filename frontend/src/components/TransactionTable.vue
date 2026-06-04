<template>
  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Description</th>
          <th>Category</th>
          <th>Withdrawal (SGD)</th>
          <th>Credit (SGD)</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="tx in transactions" :key="tx.id">
          <td>{{ tx.date }}</td>
          <td>{{ tx.description }}</td>
          <td>
            <span class="badge">{{ tx.category }}</span>
          </td>
          <td>{{ tx.withdrawal ? tx.withdrawal.toFixed(2) : '—' }}</td>
          <td>{{ tx.credit ? tx.credit.toFixed(2) : '—' }}</td>
        </tr>
        <tr v-if="!transactions.length">
          <td colspan="5">No transactions found. Upload a statement to get started.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  transactions: {
    type: Array,
    default: () => [],
  },
})
</script>
