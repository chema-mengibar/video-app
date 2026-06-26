<template>
  <div class="bookmark-editor">
    <div class="bookmark-editor__header">
      <span class="bookmark-editor__title">Marcadores</span>
      <button
          class="bookmark-editor__add-btn"
          @click="handleCreate"
          :disabled="!videoService?.state.isLoaded"
      >
        + Nueva Marca
      </button>
    </div>

    <div class="bookmark-editor__list">
      <div
          v-for="(item, index) in bookmarkService?.state.items"
          :key="index"
          class="bookmark-item"
          @click="bookmarkService?.seek(item.time_msec)"
      >
        <div class="bookmark-item__time">{{ formatMsec(item.time_msec) }}</div>
        <input
            class="bookmark-item__input"
            v-model="item.label"
            @change="handleSync"
            @click.stop
        />
        <button
            class="bookmark-item__del-btn"
            @click.stop="handleDelete(index)"
        >
          &times;
        </button>
      </div>

      <div v-if="bookmarkService?.state.items.length === 0" class="bookmark-editor__empty">
        No hay marcas en este video
      </div>
    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue';
import { SERVICES_KEY } from "@/services/ServiceRegistry.js";

const services = inject(SERVICES_KEY);
const videoService = services?.videoService;
const bookmarkService = services?.bookmarkService;

const handleCreate = () => {
  const timeMsec = Math.floor((videoService?.state.currentTime || 0) * 1000);
  const path = videoService?.state.videoPath;
  if (path) bookmarkService?.add(path, timeMsec, "Nueva Marca");
};

const handleDelete = (index) => {
  const path = videoService?.state.videoPath;
  if (path) {
    bookmarkService?.remove(path, index);
  }
};

const handleSync = () => {
  const path = videoService?.state.videoPath;
  if (path) bookmarkService?.sync(path);
};

const formatMsec = (msec) => {
  const seconds = Math.floor(msec / 1000);
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
};
</script>

<style scoped lang="scss">
.bookmark-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--base-dark-2);
  border-left: 1px solid var(--base-dark-1);

  &__header {
    padding: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--base-dark-1);
  }

  &__title {
    font-size: var(--fs-ui-small);
    text-transform: uppercase;
    color: var(--text-muted);
  }

  &__add-btn {
    background: var(--accent-primary);
    border: none;
    color: var(--text-color);
    padding: 4px 8px;
    cursor: pointer;
    font-size: 11px;
    border-radius: 2px;
    &:disabled { opacity: 0.3; }
  }

  &__list {
    flex: 1;
    overflow-y: auto;
    padding: 5px;
  }

  &__empty {
    padding: 20px;
    text-align: center;
    color: var(--base-dark-3);
    font-style: italic;
  }
}

.bookmark-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-bottom: 1px solid var(--base-dark-1);
  cursor: pointer;

  &:hover { background: var(--base-dark-1); }

  &__time {
    font-family: monospace;
    color: var(--accent-primary);
    min-width: 40px;
  }

  &__input {
    flex: 1;
    background: transparent;
    border: 1px solid transparent;
    color: var(--text-color);
    padding: 2px 4px;
    &:focus {
      background: var(--base-dark-3);
      border-color: var(--base-dark-1);
    }
  }

  &__del-btn {
    background: transparent;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    font-size: 16px;
    &:hover { color: var(--danger); }
  }
}
</style>
