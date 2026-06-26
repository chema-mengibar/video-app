<template>
  <div class="main-panel">
    <slot></slot>
  </div>
</template>

<script setup>
// No necesitas ninguna lógica adicional aquí
</script>

<style scoped>
.main-panel {
  background-color: var(--base);
  flex:1;
}
</style>