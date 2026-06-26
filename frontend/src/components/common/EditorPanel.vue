<template>
  <section class="editor-panel">
    <div class="editor-panel__body">
      <slot />
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: ""
  },
  accent: {
    type: Boolean,
    default: false
  }
});
</script>

<style scoped>
.editor-panel {
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: var(--surface-panel);
  border-right: 1px solid var(--surface-outer);
}

.editor-panel__body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
</style>
