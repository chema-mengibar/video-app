<template>
  <div
      :class="['resize-handler', `resize-handler--${direction}`]"
      @mousedown="emit('resize-start', $event)"
  ></div>
</template>

<script setup>
defineProps({
  direction: {
    type: String,
    default: 'horizontal'
  }
});

const emit = defineEmits(['resize-start']);
</script>

<style scoped lang="scss">
.resize-handler {
  background-color: var(--surface-outer);
  transition: background 0.2s;
  flex-shrink: 0;
  z-index: 10;

  &:hover {
    background-color: var(--accent-primary);
  }

  &--horizontal {
    width: 6px;
    height: 100%;
    cursor: col-resize;
  }

  &--vertical {
    height: 6px;
    width: 100%;
    cursor: row-resize;
  }
}
</style>
