<template>
  <div class="top-bar">
    <slot name="content"></slot>
  </div>
</template>

<script setup>
// No necesitas ninguna lógica adicional aquí
</script>

<style scoped>
.top-bar {
  background-color: var(--base);
  height:40px;
  width:100%;
}
</style>