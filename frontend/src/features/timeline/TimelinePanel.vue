<template>
  <section class="timeline">
    <header class="timeline__header">
      <div class="timeline__header-left">Timeline</div>
      <div class="timeline__header-main">
        <span>{{ displayMode === "time" ? "Time" : "Frames" }}</span>
        <div class="timeline__header-tools">
          <label class="timeline__scale">
            <span>Scale</span>
            <input v-model.number="timelineScale" type="range" min="1" max="8" step="0.25" />
          </label>
          <button class="timeline__toggle" type="button" @click="toggleDisplayMode">
            {{ displayMode === "time" ? "Show frames" : "Show time" }}
          </button>
        </div>
      </div>
    </header>

    <div class="timeline__body">
      <div class="timeline__label-spacer"></div>
      <div ref="viewportRef" class="timeline__viewport" @scroll="onTimelineScroll">
        <div class="timeline__content" :style="{ width: `${timelineScale * 100}%` }">
          <div class="timeline__ticks">
            <span v-for="tick in ticks" :key="tick.value">{{ tick.label }}</span>
            <button
              v-for="event in events"
              :key="event.id"
              class="timeline__event-marker"
              type="button"
              :title="event.label || 'Event'"
              :style="{ left: percentLeft(event.time_from) }"
              @click.stop="jumpToEvent(event)"
            ></button>
          </div>
          <div class="timeline__playhead-layer" @pointerdown="startPlayheadDrag">
            <button
              class="timeline__cursor"
              type="button"
              :style="{ left: playheadLeft }"
              @pointerdown.stop="startPlayheadDrag"
            >
              <span>{{ formatValue(timeline.state.currentTime) }}</span>
            </button>
          </div>
        </div>
      </div>

      <div class="timeline__rows">
        <div v-for="item in items" :key="item.id" class="timeline__row">
          <button class="timeline__label" type="button" @click="openItem(item.id)" @contextmenu.prevent="openKeyframeMenu($event, item)">
            <span class="timeline__dot" :style="{ background: item.color || 'var(--accent-primary)' }"></span>
            <span>{{ item.label }}</span>
            <span>{{ formatValue(item.time_from) }} - {{ formatValue(item.time_to || item.time_from) }}</span>
          </button>
          <div class="timeline__row-viewport">
            <div
              class="timeline__row-grid"
              :style="rowGridStyle"
            >
              <span class="timeline__playhead-guide" :style="{ left: playheadLeft }"></span>
              <div
                class="timeline__bar"
                :style="barStyle(item)"
                @pointerdown.stop="startItemDrag($event, item, 'move')"
                @click.stop="openItem(item.id)"
                @contextmenu.prevent.stop="openKeyframeMenu($event, item)"
              >
                <span class="timeline__bar-handle timeline__bar-handle--left" @pointerdown.stop="startItemDrag($event, item, 'start')"></span>
                <span class="timeline__bar-handle timeline__bar-handle--right" @pointerdown.stop="startItemDrag($event, item, 'end')"></span>
              </div>
              <button
                v-for="keyframe in keyframesForItem(item)"
                :key="keyframe.id"
                class="timeline__keyframe"
                :class="{ 'timeline__keyframe--active': isActiveKeyframe(keyframe) }"
                type="button"
                :title="`Keyframe ${formatValue(keyframe.time)}`"
                :style="{ left: percentLeft(keyframe.time) }"
                @click.stop="timeline.setCurrentTime(keyframe.time)"
                @contextmenu.prevent.stop="openKeyframeMenu($event, item, keyframe)"
              ></button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="keyframeMenu"
      class="timeline__menu"
      :style="{ left: `${keyframeMenu.x}px`, top: `${keyframeMenu.y}px` }"
      @click.stop
    >
      <button type="button" @click="createKeyframeFromMenu">Create keyframe in current time</button>
      <button type="button" :disabled="!canRemoveMenuKeyframe" @click="removeKeyframeFromMenu">Remove keyframe</button>
    </div>
  </section>
</template>

<script setup>
import { computed, inject, onBeforeUnmount, onMounted, ref } from "vue";
import { SERVICES_KEY } from "@/services/ServiceRegistry.js";

const services = inject(SERVICES_KEY);
const timeline = services.timelineService;
const project = services.projectService;
const draw = services.drawService;
const measure = services.measureService;
const eventService = services.eventsService;
const keyframeService = services.keyframeService;
const viewportRef = ref(null);
const displayMode = ref("time");
const isDragging = ref(false);
const playheadDrag = ref(null);
const itemDrag = ref(null);
const timelineScale = ref(1);
const scrollLeft = ref(0);
const keyframeMenu = ref(null);
const items = computed(() => project.state.data.items || []);
const events = computed(() => project.state.data.events || []);
const scaleMax = computed(() => Math.max(timeline.getDisplayDuration?.() || timeline.state.duration || 200, 1));
const playheadLeft = computed(() => `${Math.min(100, (timeline.state.currentTime / scaleMax.value) * 100)}%`);
const frameRate = 30;

const ticks = computed(() => {
  const count = 20;
  return Array.from({ length: count + 1 }, (_, index) => {
    const value = (scaleMax.value / count) * index;
    return {
      value,
      label: formatValue(value)
    };
  });
});

const toggleDisplayMode = () => {
  displayMode.value = displayMode.value === "time" ? "frame" : "time";
};

const openItem = (id) => {
  const item = items.value.find((candidate) => candidate.id === id);
  if (["measure-line", "measure-grid", "chrono", "player", "ball", "delay"].includes(item?.type)) {
    measure.state.selectedItemId = id;
    draw.selectItem(null);
  }
  draw.focusItem(id);
};

const keyframesForItem = (item) => keyframeService.keyframesFor(item);

const isActiveKeyframe = (keyframe) => {
  return Math.abs((Number(keyframe?.time) || 0) - timeline.state.currentTime) <= keyframeService.epsilon;
};

const canRemoveMenuKeyframe = computed(() => {
  if (!keyframeMenu.value?.item) return false;
  const time = keyframeMenu.value.keyframe?.time ?? timeline.state.currentTime;
  return keyframeService.hasKeyframeAt(keyframeMenu.value.item, time);
});

const openKeyframeMenu = (event, item, keyframe = null) => {
  openItem(item.id);
  keyframeMenu.value = {
    x: event.clientX,
    y: event.clientY,
    item,
    keyframe
  };
};

const closeKeyframeMenu = () => {
  keyframeMenu.value = null;
};

const createKeyframeFromMenu = () => {
  keyframeService.addKeyframe(keyframeMenu.value?.item, timeline.state.currentTime);
  closeKeyframeMenu();
};

const removeKeyframeFromMenu = () => {
  if (!keyframeMenu.value?.item) return;
  const time = keyframeMenu.value.keyframe?.time ?? timeline.state.currentTime;
  keyframeService.removeKeyframeAt(keyframeMenu.value.item, time);
  closeKeyframeMenu();
};

const jumpToEvent = (event) => {
  eventService.jump(event);
};

const rowGridStyle = computed(() => ({
  width: `${timelineScale.value * 100}%`,
  transform: `translateX(${-scrollLeft.value}px)`
}));

const onTimelineScroll = () => {
  scrollLeft.value = viewportRef.value?.scrollLeft || 0;
};

const timeFromPointer = (event, bounds = playheadDrag.value?.bounds) => {
  if (!bounds) return timeline.state.currentTime;
  const ratio = Math.min(1, Math.max(0, (event.clientX - bounds.left) / bounds.width));
  return ratio * scaleMax.value;
};

const updateTimeFromPointer = (event) => {
  timeline.pause();
  timeline.setCurrentTime(timeFromPointer(event));
};

const startPlayheadDrag = (event) => {
  const layer = event.currentTarget.classList?.contains("timeline__playhead-layer")
    ? event.currentTarget
    : event.currentTarget.closest(".timeline__playhead-layer");
  if (!layer) return;

  isDragging.value = true;
  playheadDrag.value = {
    bounds: layer.getBoundingClientRect()
  };
  event.preventDefault();
  layer.setPointerCapture?.(event.pointerId);
  updateTimeFromPointer(event);
  window.addEventListener("pointermove", onPointerMove);
  window.addEventListener("pointerup", stopPlayheadDrag);
};

const startItemDrag = (event, item, mode) => {
  openItem(item.id);
  const grid = event.currentTarget.closest(".timeline__row-grid");
  const bounds = grid.getBoundingClientRect();
  itemDrag.value = {
    item,
    mode,
    startX: event.clientX,
    startFrom: Number(item.time_from) || 0,
    startTo: Number(item.time_to) || Number(item.time_from) || 0,
    secondsPerPixel: scaleMax.value / bounds.width
  };
  event.currentTarget.setPointerCapture?.(event.pointerId);
  window.addEventListener("pointermove", onItemPointerMove);
  window.addEventListener("pointerup", stopItemDrag);
};

const onItemPointerMove = (event) => {
  const drag = itemDrag.value;
  if (!drag) return;

  const delta = (event.clientX - drag.startX) * drag.secondsPerPixel;
  const minDuration = 0.1;
  const duration = Math.max(minDuration, drag.startTo - drag.startFrom);

  if (drag.mode === "move") {
    const nextFrom = Math.max(0, Math.min(scaleMax.value - duration, drag.startFrom + delta));
    drag.item.time_from = nextFrom;
    drag.item.time_to = nextFrom + duration;
    return;
  }

  if (drag.mode === "start") {
    drag.item.time_from = Math.max(0, Math.min(drag.startTo - minDuration, drag.startFrom + delta));
    return;
  }

  drag.item.time_to = Math.max(drag.startFrom + minDuration, Math.min(scaleMax.value, drag.startTo + delta));
};

const stopItemDrag = () => {
  if (itemDrag.value) {
    if (itemDrag.value.item?.type === "delay") {
      itemDrag.value.item.duration = Math.max(0.1, (Number(itemDrag.value.item.time_to) || 0) - (Number(itemDrag.value.item.time_from) || 0));
    }
    project.save();
  }
  itemDrag.value = null;
  window.removeEventListener("pointermove", onItemPointerMove);
  window.removeEventListener("pointerup", stopItemDrag);
};

const onPointerMove = (event) => {
  if (isDragging.value) {
    updateTimeFromPointer(event);
  }
};

const stopPlayheadDrag = () => {
  isDragging.value = false;
  playheadDrag.value = null;
  window.removeEventListener("pointermove", onPointerMove);
  window.removeEventListener("pointerup", stopPlayheadDrag);
};

const barStyle = (item) => {
  const start = Math.min(100, ((item.time_from || 0) / scaleMax.value) * 100);
  const end = Math.min(100, ((item.time_to || item.time_from || 0) / scaleMax.value) * 100);
  return {
    left: `${start}%`,
    width: `${Math.max(1, end - start)}%`,
    background: item.color || "var(--accent-primary)"
  };
};

const percentLeft = (time) => `${Math.min(100, ((time || 0) / scaleMax.value) * 100)}%`;

const formatValue = (time) => {
  const value = Math.max(0, Number.isFinite(time) ? time : 0);
  if (displayMode.value === "frame") {
    return `${Math.round(value * frameRate)}f`;
  }

  const minutes = Math.floor(value / 60);
  const seconds = Math.floor(value % 60);
  const millis = Math.floor((value % 1) * 1000);
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")},${String(millis).padStart(3, "0")}`;
};

onBeforeUnmount(() => {
  stopPlayheadDrag();
  stopItemDrag();
  window.removeEventListener("click", closeKeyframeMenu);
});

onMounted(() => {
  window.addEventListener("click", closeKeyframeMenu);
});
</script>

<style scoped>
.timeline {
  height: 240px;
  display: grid;
  grid-template-columns: 280px 1fr;
  grid-template-rows: 30px minmax(0, 1fr);
  background: var(--surface-timeline);
  border-top: 4px solid var(--surface-outer);
}

.timeline__header {
  grid-column: 1 / span 2;
  display: grid;
  grid-template-columns: 280px 1fr;
  background: var(--surface-black);
  border-bottom: 1px solid var(--surface-border);
}

.timeline__header-left,
.timeline__header-main {
  min-width: 0;
  display: flex;
  align-items: center;
  padding: 0 12px;
}

.timeline__header-left {
  border-right: 1px solid var(--surface-border);
  color: var(--text-muted);
}

.timeline__header-main {
  justify-content: space-between;
  color: var(--text-muted);
}

.timeline__header-tools {
  display: flex;
  align-items: center;
  gap: 12px;
}

.timeline__scale {
  display: flex;
  align-items: center;
  gap: 8px;
}

.timeline__scale input {
  width: 150px;
  accent-color: var(--accent-primary);
}

.timeline__toggle {
  height: 24px;
  border: 1px solid var(--surface-border);
  background: var(--surface-button);
  color: var(--text-color);
  cursor: pointer;
}

.timeline__body {
  grid-column: 1 / span 2;
  grid-row: 2;
  min-height: 0;
  display: grid;
  grid-template-columns: 280px 1fr;
  grid-template-rows: 30px minmax(0, 1fr);
  overflow: hidden;
}

.timeline__label-spacer {
  background: var(--surface-track-label);
  border-right: 1px solid var(--surface-border);
}

.timeline__dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
}

.timeline__dot--event {
  background: var(--accent-primary);
}

.timeline__viewport {
  grid-column: 2;
  grid-row: 1;
  width: 100%;
  height: 100%;
  overflow-x: auto;
  overflow-y: hidden;
}

.timeline__content {
  min-width: 100%;
  height: 100%;
  display: grid;
  grid-template-rows: 30px 1fr;
  position: relative;
}

.timeline__rows {
  grid-column: 1 / span 2;
  grid-row: 2;
  min-height: 0;
  overflow-y: auto;
}

.timeline__row {
  height: 30px;
  display: grid;
  grid-template-columns: 280px 1fr;
}

.timeline__label {
  width: 100%;
  display: grid;
  grid-template-columns: 14px 70px 1fr;
  align-items: center;
  gap: 10px;
  padding: 0 22px;
  border: 0;
  border-right: 1px solid var(--surface-border);
  background: var(--surface-track-label);
  color: var(--text-color);
  text-align: left;
  cursor: pointer;
}

.timeline__label:hover {
  background: var(--surface-header);
}

.timeline__row-viewport {
  min-width: 0;
  overflow: hidden;
}

.timeline__row-grid {
  position: relative;
  min-width: 100%;
  height: 30px;
  display: flex;
  align-items: center;
  background-image: linear-gradient(to right, var(--surface-grid) 1px, transparent 1px);
  background-size: 65px 100%;
}

.timeline__playhead-guide {
  position: absolute;
  top: 0;
  bottom: 0;
  z-index: 1;
  width: 2px;
  background: var(--playhead);
  pointer-events: none;
  transform: translateX(-1px);
}

.timeline__ticks {
  position: relative;
  display: grid;
  grid-template-columns: repeat(21, minmax(72px, 1fr));
  align-items: center;
  color: var(--text-muted);
  font-size: var(--fs-ui-small);
  overflow: hidden;
}

.timeline__ticks span {
  min-width: 0;
  overflow: hidden;
  text-overflow: clip;
  white-space: nowrap;
}

.timeline__event-marker {
  position: absolute;
  top: 6px;
  bottom: 6px;
  width: 3px;
  padding: 0;
  border: 0;
  background: var(--accent-primary);
  border-radius: 2px;
  cursor: pointer;
  transform: translateX(-1px);
}

.timeline__event-marker:hover {
  width: 7px;
  transform: translateX(-3px);
}

.timeline__playhead-layer {
  position: absolute;
  inset: 30px 0 0;
  cursor: col-resize;
}

.timeline__cursor {
  position: absolute;
  top: 0;
  bottom: 0;
  z-index: 3;
  width: 18px;
  padding: 0;
  border: 0;
  border-left: 2px solid var(--playhead);
  background: transparent;
  color: var(--text-color);
  cursor: ew-resize;
  transform: translateX(-1px);
}

.timeline__cursor::before {
  content: "";
  position: absolute;
  top: 0;
  left: -7px;
  width: 14px;
  height: 14px;
  background: var(--playhead);
  clip-path: polygon(50% 100%, 0 0, 100% 0);
}

.timeline__cursor span {
  position: absolute;
  top: -28px;
  left: -28px;
  min-width: 56px;
  padding: 3px 6px;
  text-align: center;
  background: var(--playhead);
  color: var(--text-color);
  border-radius: 3px;
  font-variant-numeric: tabular-nums;
}

.timeline__bar {
  position: absolute;
  top: 10px;
  z-index: 2;
  height: 10px;
  cursor: grab;
}

.timeline__keyframe {
  position: absolute;
  top: 9px;
  z-index: 4;
  width: 12px;
  height: 12px;
  padding: 0;
  border: 1px solid var(--surface-black);
  background: var(--text-color);
  cursor: pointer;
  transform: translateX(-50%) rotate(45deg);
}

.timeline__keyframe--active {
  background: var(--accent-primary);
}

.timeline__keyframe:hover {
  border-color: var(--text-color);
}

.timeline__bar-handle {
  position: absolute;
  top: -3px;
  width: 6px;
  height: 18px;
  background: var(--text-color);
  cursor: ew-resize;
}

.timeline__bar-handle--left {
  left: -3px;
}

.timeline__bar-handle--right {
  right: -3px;
}

.timeline__menu {
  position: fixed;
  z-index: 20;
  min-width: 210px;
  display: grid;
  padding: 4px;
  background: var(--surface-control);
  border: 1px solid var(--surface-border);
  box-shadow: 0 8px 22px rgb(0 0 0 / 0.35);
}

.timeline__menu button {
  min-height: 28px;
  border: 0;
  padding: 0 10px;
  background: transparent;
  color: var(--text-color);
  text-align: left;
  cursor: pointer;
}

.timeline__menu button:hover:not(:disabled) {
  background: var(--surface-button);
}

.timeline__menu button:disabled {
  color: var(--text-muted);
  cursor: not-allowed;
}
</style>
