<template>
  <div class="workspace" :style="{ gridTemplateColumns: `auto ${props.width}px auto` }">
    <slot></slot>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  width: {
    type: Number,
    required: true
  }
});
</script>

<style lang="scss">
.workspace {
  display: grid;
  grid-template-rows: auto 1fr auto;
  background-color: var(--base);
}
</style>