<template>
  <svg class="app-icon" viewBox="0 0 24 24" aria-hidden="true">
    <path v-if="name === 'upload'" d="M12 3l5 5h-3v7h-4V8H7l5-5zM5 19h14v2H5z" />
    <path v-else-if="name === 'play'" d="M8 5v14l11-7z" />
    <path v-else-if="name === 'pause'" d="M7 5h4v14H7zM13 5h4v14h-4z" />
    <path v-else-if="name === 'back'" d="M11 6v12l-8-6zM20 6v12l-8-6z" />
    <path v-else-if="name === 'forward'" d="M13 6v12l8-6zM4 6v12l8-6z" />
    <path v-else-if="name === 'step-back'" d="M7 5h2v14H7zM18 6v12l-8-6z" />
    <path v-else-if="name === 'step-forward'" d="M15 5h2v14h-2zM6 6v12l8-6z" />
    <path v-else-if="name === 'start'" d="M5 5h2v14H5zM9 5h2v14H9zM20 6v12l-8-6z" />
    <path v-else-if="name === 'draw'" d="M4 17.5V21h3.5L18.1 10.4l-3.5-3.5L4 17.5zM19.2 9.3l1.1-1.1a1.5 1.5 0 000-2.1l-2.4-2.4a1.5 1.5 0 00-2.1 0l-1.1 1.1 4.5 4.5z" />
    <path v-else-if="name === 'event'" d="M5 4h14v16H5zM8 8h8v2H8zM8 12h5v2H8z" />
    <path v-else-if="name === 'cut'" d="M9 4a3 3 0 11-2.1 5.1L4 12l2.9 2.9A3 3 0 119 17l3-3 3 3a3 3 0 10.1-2.1L12 12l3.1-2.9A3 3 0 109 7L6 10 4 8l2-2 3 3z" />
    <path v-else-if="name === 'trash'" d="M8 7h8l-.6 13H8.6L8 7zM6 4h12v2H6zM10 2h4v2h-4z" />
    <path v-else-if="name === 'move'" d="M12 2l3 3h-2v6h6V9l3 3-3 3v-2h-6v6h2l-3 3-3-3h2v-6H5v2l-3-3 3-3v2h6V5H9z" />
    <path v-else-if="name === 'cursor'" d="M5 3l12 8-5 1.2 3.2 5.5-2.2 1.3-3.2-5.6L6 17z" />
    <path v-else-if="name === 'eye'" d="M2 12s4-6 10-6 10 6 10 6-4 6-10 6S2 12 2 12zm10 3a3 3 0 100-6 3 3 0 000 6z" />
    <path v-else-if="name === 'eye-off'" d="M4 3l17 17-1.4 1.4-3-3A11.7 11.7 0 0112 19C6 19 2 12 2 12a18.2 18.2 0 014.1-4.8L2.6 4.4 4 3zm5.1 7.4a3 3 0 004.1 4.1zM12 5c6 0 10 7 10 7a17 17 0 01-3.2 4.1L16.6 14A3 3 0 0012 9.4L9.8 7.2A10.7 10.7 0 0112 5z" />
    <path v-else-if="name === 'line'" d="M4 18c6-1 7-11 16-12" fill="none" stroke="currentColor" stroke-width="2" />
    <path v-else-if="name === 'straight'" d="M5 19L19 5" fill="none" stroke="currentColor" stroke-width="2" />
    <path v-else-if="name === 'measure'" d="M4 17L17 4l3 3L7 20H4zm3-1.8L15.2 7 17 8.8 8.8 17H7zM6 5h7v2H8v5H6z" />
    <path v-else-if="name === 'triangle'" d="M12 5l8 14H4z" />
    <path v-else-if="name === 'square'" d="M6 6h12v12H6z" />
    <path v-else-if="name === 'polygon'" d="M12 3l8 6-3 10H7L4 9z" />
    <path v-else-if="name === 'circle'" d="M12 5a7 7 0 100 14 7 7 0 000-14z" />
    <path v-else-if="name === 'chrono'" d="M9 2h6v2H9zM11 5h2v7l5 3-1 1.7-6-3.6V5zM12 4a9 9 0 100 18 9 9 0 000-18zm0 2a7 7 0 110 14 7 7 0 010-14z" />
    <path v-else-if="name === 'player'" d="M11 4h2v7h7v2h-7v7h-2v-7H4v-2h7z" />
    <path v-else-if="name === 'ball'" d="M12 4a8 8 0 100 16 8 8 0 000-16zm0 2a6 6 0 014.7 2.3L12 11 7.3 8.3A6 6 0 0112 6zm-6 6c0-.7.1-1.4.4-2l4.6 2.7v5.1A6 6 0 016 12zm7 5.8v-5.1l4.6-2.7A6 6 0 0113 17.8z" />
    <path v-else-if="name === 'jump'" d="M5 6h2v12H5zM9 5l10 7-10 7z" />
    <path v-else d="M5 5h14v14H5z" />
  </svg>
</template>

<script setup>
defineProps({
  name: {
    type: String,
    default: "square"
  }
});
</script>

<style scoped>
.app-icon {
  width: 16px;
  height: 16px;
  display: block;
  fill: currentColor;
}
</style>
