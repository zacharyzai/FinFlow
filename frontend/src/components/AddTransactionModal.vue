<template>
    <div>
        <form @submit.prevent="handleSubmit">
            <input type="text" v-model="description">
            <input type="number" v-model="amount">
            <select v-model="category">
                <option value="Food & Dining">Food & Dining</option>
                <option value="Transport">Transport</option>
                <option value="Shopping">Shopping</option>
                <option value="Bills & Utilities">Bills & Utilities</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Entertainment">Entertainment</option>
                <option value="Travel">Travel</option>
                <option value="Education">Education</option>
                <option value="Income">Income</option>
                <option value="Transfer">Transfer</option>
                <option value="Other">Other</option>
            </select>
            <select v-model="type">
                <option value="withdrawal">Withdrawal</option>
                <option value="credit">Income (Credit)</option>
            </select>            
            <input type="date" v-model="date">
            
            <button type="submit">Save</button>
        </form>
    </div>
</template>

<script setup>
import { ref } from 'vue';

const date = ref('')
const amount = ref('')
const description = ref('')
const category = ref('')
const type = ref('withdrawal')
</script>

<style scoped>
</style>