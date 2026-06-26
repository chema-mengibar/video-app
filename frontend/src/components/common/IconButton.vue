<template>
  <button class="icon-button" :class="{ 'icon-button--active': active }" :title="title" type="button">
    <AppIcon :name="icon" />
  </button>
</template>

<script setup>
import AppIcon from "@/components/common/AppIcon.vue";

defineProps({
  icon: {
    type: String,
    required: true
  },
  title: {
    type: String,
    default: ""
  },
  active: {
    type: Boolean,
    default: false
  }
});
</script>

<style scoped>
.icon-button {
  width: 36px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--surface-border);
  background: var(--surface-button);
  color: var(--text-color);
  cursor: pointer;
}

.icon-button:hover,
.icon-button--active {
  color: var(--accent-primary);
  border-color: var(--accent-primary);
}

.icon-button--active {
  background: var(--accent-primary);
  color: var(--surface-black);
}

.icon-button:disabled {
  cursor: default;
  opacity: 0.4;
}
</style>
