<template>
  <div class="video-player">
    <div class="video-player__top-row">
      <input type="file" ref="fileInput" @change="handleFileChange" accept="video/*" hidden />
      <button class="video-player__button" @click="fileInput?.click()">Cargar Video</button>
      <span class="video-player__path">{{ videoFileName }}</span>
    </div>

    <div class="video-player__screen-row">
      <video
        ref="videoRef"
        class="video-player__video"
        @loadedmetadata="onMetadata"
        @timeupdate="onTimeUpdate"
      ></video>
      <div v-if="!videoService?.state.isLoaded" class="video-player__placeholder">Sin senal</div>
    </div>

    <div class="video-player__controls-row">
      <button class="video-player__button" @click="videoService?.togglePlay()" :disabled="!videoService?.state.isLoaded">
        {{ videoService?.state.isPlaying ? 'Pausa' : 'Play' }}
      </button>
      <button class="video-player__button" @click="videoService?.stop()" :disabled="!videoService?.state.isLoaded">Stop</button>
      <div class="video-player__time-display">
        {{ formatTime(videoService?.state.currentTime) }} / {{ formatTime(videoService?.state.duration) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, computed, watch, onBeforeUnmount } from 'vue';
import { SERVICES_KEY } from "@/services/ServiceRegistry.js";

const services = inject(SERVICES_KEY);
const videoService = services?.videoService;
const videoRef = ref(null);
const fileInput = ref(null);
let currentObjectUrl = null;

const revokeObjectUrl = () => {
  if (currentObjectUrl) {
    URL.revokeObjectURL(currentObjectUrl);
    currentObjectUrl = null;
  }
};

const videoFileName = computed(() => {
  const path = videoService?.state.videoPath;
  return path ? path.split(/[\\/]/).pop() : '';
});

const handleFileChange = (e) => {
  const file = e?.target?.files?.[0];
  if (!file || !videoService) return;

  const realPath = file.path || file.name;
  revokeObjectUrl();
  currentObjectUrl = URL.createObjectURL(file);

  videoService.loadVideo(realPath, currentObjectUrl);
};

const onMetadata = () => {
  if (videoRef.value && videoService) {
    videoService.updateDuration(videoRef.value.duration);
  }
};

const onTimeUpdate = () => {
  if (videoRef.value && videoService) {
    videoService.state.currentTime = videoRef.value.currentTime;
  }
};

const formatTime = (s) => {
  const safeSeconds = Number.isFinite(s) ? s : 0;
  const mins = Math.floor(safeSeconds / 60);
  const secs = Math.floor(safeSeconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

watch(
  () => videoService?.state.videoUrl,
  (videoUrl) => {
    if (videoRef.value) {
      videoRef.value.src = videoUrl || '';
    }
  }
);

watch(
  () => videoService?.state.isPlaying,
  (isPlaying) => {
    if (!videoRef.value) return;
    if (isPlaying) {
      videoRef.value.play()?.catch(() => videoService?.pause());
    } else {
      videoRef.value.pause();
    }
  }
);

watch(
  () => videoService?.state.currentTime,
  (currentTime) => {
    if (!videoRef.value || !Number.isFinite(currentTime)) return;
    if (Math.abs(videoRef.value.currentTime - currentTime) > 0.25) {
      videoRef.value.currentTime = currentTime;
    }
  }
);

onBeforeUnmount(revokeObjectUrl);
</script>

<style scoped lang="scss">
.video-player {
  display: grid;
  grid-template-rows: 40px 1fr 50px;
  height: 100%;
  background: var(--surface-panel);

  &__top-row,
  &__controls-row {
    display: flex;
    align-items: center;
    padding: 0 10px;
    gap: 10px;
    background: var(--surface-control);
  }

  &__screen-row {
    background: var(--surface-black);
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }

  &__video {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }

  &__path {
    font-size: 10px;
    color: var(--text-muted);
    overflow: hidden;
    text-overflow: ellipsis;
  }

  &__time-display {
    margin-left: auto;
    font-family: monospace;
    color: var(--signal-green);
  }

  &__button {
    background: var(--surface-button);
    color: var(--text-color);
    border: 1px solid var(--surface-border);
    padding: 4px 10px;
    cursor: pointer;
    border-radius: 2px;

    &:hover {
      border-color: var(--signal-green);
    }

    &:disabled {
      opacity: 0.3;
    }
  }
}
</style>
