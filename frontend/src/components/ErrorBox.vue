<template>
  <div class="alert">
    <strong>Erro:</strong> {{ message }}
  </div>
</template>

<script setup>
defineProps({ message: { type: String, required: true } });
</script>