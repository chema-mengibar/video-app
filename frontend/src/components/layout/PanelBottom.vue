<template>
  <div class="panel-bottom">
    <slot name="content"></slot>
  </div>
</template>

<script setup>
// No necesitas ninguna lógica adicional aquí
</script>

<style scoped>
.panel-bottom {
  background-color: var(--base);
}
</style>