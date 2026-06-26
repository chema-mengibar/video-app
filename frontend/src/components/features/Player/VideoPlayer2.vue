<template>
  <div class="video-player">
    <div class="video-player__top-row">
      <input type="file" ref="fileInput" hidden accept="video/*" />
      <button @click="handleFileClick">Cargar Video</button>
    </div>
    <div class="video-player__screen-row">
      <video ref="videoElement" :src="videoService.state.videoPath" @loadedmetadata="updateDuration" @timeupdate="updateCurrentTime"></video>
    </div>
    <div class="video-player__controls-row">
      <button @click="togglePlay">{{ videoService.state.isPlaying ? 'Pause' : 'Play' }}</button>
      <button @click="stopVideo">Stop</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { inject } from 'vue';
import { SERVICES_KEY } from '@/services/ServiceRegistry.js';

const services = inject(SERVICES_KEY);
const videoService = services?.videoService;
const fileInput = ref(null);
const videoElement = ref(null);

watch(() => videoService?.state.isPlaying, (isPlaying) => {
  if (videoElement.value && isPlaying) {
    videoElement.value.play();
  } else if (videoElement.value) {
    videoElement.value.pause();
  }
});

watch(() => videoService?.state.currentTime, (currentTime) => {
  if (videoElement.value && Math.abs(videoElement.value.currentTime - currentTime) > 0.1) {
    videoElement.value.currentTime = currentTime;
  }
});

const handleFileClick = () => {
  fileInput.value.click();
};

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    videoService.loadVideo(URL.createObjectURL(file), videoElement.value);
  }
};

const togglePlay = () => {
  videoService.togglePlay(videoElement.value);
};

const stopVideo = () => {
  videoService.stop(videoElement.value);
};

const updateDuration = () => {
  if (videoElement.value) {
    videoService.updateDuration(videoElement.value.duration, videoElement.value);
  }
};

const updateCurrentTime = () => {
  if (videoElement.value) {
    videoService.updateCurrentTime(videoElement.value.currentTime, videoElement.value);
  }
};
</script>

<style scoped lang="scss">
.video-player {
  display: grid;
  grid-template-rows: 40px 1fr 50px;
  height: 100%;
}

.video-player__top-row {
  display: flex;
  justify-content: space-between;
}

.video-player__screen-row {
  background-color: var(--base-dark-3);
}

.video-player__video {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.video-player__controls-row button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background-color: var(--accent-primary);
  color: white;
  cursor: pointer;
  transition: opacity 0.3s;

  &:hover {
    opacity: 0.9;
  }

  &:disabled {
    opacity: 0.3;
  }
}
</style>