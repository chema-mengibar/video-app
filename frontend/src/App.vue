<template>
  <main class="app">
    <div class="app__top" :style="{ gridTemplateColumns: `${leftWidth}px 6px minmax(0, 1fr) 6px ${rightWidth}px` }">
      <ToolsPanel />
      <ResizeHandler direction="horizontal" @resize-start="startResize('left')" />
      <MediaStage />
      <ResizeHandler direction="horizontal" @resize-start="startResize('right')" />
      <InspectorPanel />
    </div>
    <ResizeHandler direction="vertical" @resize-start="startResize('timeline')" />
    <TimelinePanel :style="{ height: `${timelineHeight}px` }" />
  </main>
</template>

<script setup>
import { onUnmounted, ref } from "vue";
import ResizeHandler from "@/components/layout/ResizeHandler.vue";
import ToolsPanel from "@/features/tools/ToolsPanel.vue";
import MediaStage from "@/features/stage/MediaStage.vue";
import InspectorPanel from "@/features/sidepanel/InspectorPanel.vue";
import TimelinePanel from "@/features/timeline/TimelinePanel.vue";

const leftWidth = ref(405);
const rightWidth = ref(400);
const timelineHeight = ref(240);
const activeResize = ref(null);

const startResize = (panel) => {
  activeResize.value = panel;
};

const onMouseMove = (event) => {
  if (!activeResize.value) return;

  if (activeResize.value === "left") {
    leftWidth.value = Math.min(520, Math.max(260, event.clientX));
  }

  if (activeResize.value === "right") {
    rightWidth.value = Math.min(520, Math.max(300, window.innerWidth - event.clientX));
  }

  if (activeResize.value === "timeline") {
    timelineHeight.value = Math.min(360, Math.max(160, window.innerHeight - event.clientY));
  }
};

const stopResize = () => {
  activeResize.value = null;
};

window.addEventListener("mousemove", onMouseMove);
window.addEventListener("mouseup", stopResize);

onUnmounted(() => {
  window.removeEventListener("mousemove", onMouseMove);
  window.removeEventListener("mouseup", stopResize);
});
</script>

<style scoped>
.app {
  width: 100vw;
  height: 100vh;
  display: grid;
  grid-template-rows: minmax(0, 1fr) 6px auto;
  overflow: hidden;
  background: var(--surface-outer);
  color: var(--text-color);
}

.app__top {
  min-height: 0;
  display: grid;
  overflow: hidden;
}
</style>
