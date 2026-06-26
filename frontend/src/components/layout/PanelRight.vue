<template>
  <div class="panel-right">
    <slot name="content"></slot>
  </div>
</template>

<script setup>
// No necesitas ninguna lógica adicional aquí
</script>

<style scoped>
.panel-right {
  background-color: var(--base);
}
</style>