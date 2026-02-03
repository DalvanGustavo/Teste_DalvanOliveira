<template>
  <div style="padding: 12px; border: 1px solid #f99; background: #fff5f5;">
    <strong>Erro:</strong> {{ message }}
  </div>
</template>

<script setup>
defineProps({ message: { type: String, required: true } });
</script>
