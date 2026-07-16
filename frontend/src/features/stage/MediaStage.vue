<template>
  <EditorPanel>
    <div class="media-stage">
      <input ref="fileInput" class="media-stage__file" type="file" accept="video/*,image/*" @change="onFileChange" />

      <div
        ref="viewportRef"
        class="media-stage__viewport"
        :class="{ 'media-stage__viewport--draw': canUseCanvas, 'media-stage__viewport--split': stageView === 'split', 'media-stage__viewport--pan': activeZoom > 1 && (isSpacePressed || panDrag), 'media-stage__viewport--panning': !!panDrag }"
        @pointerdown="onCanvasPointerDown"
        @pointermove="onCanvasPointerMove"
        @pointerup="onCanvasPointerUp"
        @pointerleave="onCanvasPointerUp"
        @wheel.prevent="onCanvasWheel"
        @contextmenu.prevent
      >
        <div
          v-if="stageView !== 'court'"
          ref="mediaPaneRef"
          class="media-stage__media-pane"
          :class="{ 'media-stage__pane--active': services.stageService.activePanel === 'canvas' }"
          @pointerdown="services.stageService.activePanel = 'canvas'"
        >
        <div ref="mediaContentRef" class="media-stage__content" :style="mediaContentStyle">
        <video
          v-if="timeline.state.mediaType !== 'image'"
          ref="videoRef"
          class="media-stage__video"
          :src="timeline.state.videoUrl"
          @loadedmetadata="onVideoMetadata"
        ></video>
        <img
          v-else
          class="media-stage__video"
          :src="timeline.state.videoUrl"
          alt=""
          @load="onImageLoad"
        />

        <svg class="media-stage__overlay" viewBox="0 0 100 100" preserveAspectRatio="none">
          <path
            v-for="item in squareCircleGuideItems"
            :key="`${item.id}-guide`"
            :d="linearClosedPath(item.points || [])"
            :stroke="item.color"
            :stroke-width="item.width / 4"
            :stroke-opacity="item.opacity * 0.7"
            fill="none"
            class="media-stage__shape media-stage__shape--guide"
          />
          <path
            v-for="item in shapeItems"
            :key="item.id"
            :d="pathFor(item)"
            :stroke="item.color"
            :stroke-width="strokeWidthFor(item)"
            :stroke-opacity="strokeOpacityFor(item)"
            :fill="fillFor(item)"
            :fill-opacity="fillOpacityFor(item)"
            :style="{ mixBlendMode: blendModeFor(item) }"
            :class="{ 'media-stage__shape--selected': isSelectedCanvasItem(item) }"
            class="media-stage__shape"
            @pointerdown.stop="selectCanvasItem(item, $event)"
          />
          <template v-for="item in projectionItems" :key="`${item.id}-projection`">
            <path
              :d="goalProjectionFillPath(item)"
              :fill="item.color"
              :fill-opacity="item.fillOpacity ?? 0.18"
              class="media-stage__projection-fill"
              @pointerdown.stop="selectCanvasItem(item, $event)"
            />
            <path
              :d="goalProjectionLinePath(item)"
              :stroke="item.color"
              :stroke-width="strokeWidthFor(item)"
              :stroke-opacity="strokeOpacityFor(item)"
              class="media-stage__projection-line"
              @pointerdown.stop="selectCanvasItem(item, $event)"
            />
            <template v-if="isSelectedCanvasItem(item)">
              <template v-for="(point, index) in item.points" :key="`${item.id}-point-${index}`">
                <path
                  class="media-stage__handle media-stage__handle--plus"
                  :class="{ 'media-stage__handle--active': measure.isActiveMeasurePoint(item.id, index) }"
                  :d="plusHandlePath(point)"
                  @pointerdown.stop="startMeasurePointDrag(item.id, index, $event)"
                />
                <text class="media-stage__handle-label" :x="point.x + 1.4" :y="point.y - 1.4">{{ projectionPointLabel(index) }}</text>
              </template>
            </template>
          </template>
          <path
            v-if="fieldPath"
            :d="fieldPath"
            :stroke="visibleGrid.color || 'var(--accent-primary)'"
            :stroke-opacity="visibleGrid.opacity ?? 0.85"
            :style="{ strokeWidth: `${gridLineWidth}px` }"
            class="media-stage__field"
          />
          <path
            v-for="line in projectionLines"
            :key="line.key"
            :d="line.path"
            :stroke="visibleGrid.color || 'var(--accent-primary)'"
            :stroke-opacity="gridProjectionOpacity"
            :style="{ strokeWidth: `${gridLineWidth}px` }"
            class="media-stage__projection-line"
          />
          <path
            v-for="path in chessboardPaths"
            :key="path"
            :d="path"
            :fill="visibleGrid.color || 'var(--accent-primary)'"
            class="media-stage__field-square"
          />
          <template v-for="(point, index) in activeGridPoints" :key="`field-${index}`">
            <path
              v-if="showGridHandles"
              class="media-stage__handle media-stage__handle--plus"
              :class="{ 'media-stage__handle--active': measure.isActiveFieldPoint(index) }"
              :d="plusHandlePath(point)"
              @pointerdown.stop="startFieldPointDrag(index, $event)"
            />
            <text v-if="showGridHandles" class="media-stage__handle-label" :x="point.x + 1.4" :y="point.y - 1.4">{{ fieldLabels[index] }}</text>
          </template>
          <template v-if="showGridHandles && activeChessCenter">
            <path
              class="media-stage__handle media-stage__handle--plus"
              :class="{ 'media-stage__handle--active': measure.isActiveChessCenter() }"
              :d="plusHandlePath(activeChessCenter)"
              @pointerdown.stop="startChessCenterDrag($event)"
            />
          </template>
          <template v-for="item in measureLineItems" :key="`${item.id}-measure-label`">
            <text
              v-if="measureLineLabel(item)"
              class="media-stage__measure-label"
              :x="measureLineCenter(item).x"
              :y="measureLineCenter(item).y"
            >
              {{ measureLineLabel(item) }}
            </text>
            <template v-if="isSelectedCanvasItem(item)">
              <template v-for="(point, index) in item.points" :key="`${item.id}-point-${index}`">
                <path
                  class="media-stage__handle media-stage__handle--plus"
                  :class="{ 'media-stage__handle--active': measure.isActiveMeasurePoint(item.id, index) }"
                  :d="plusHandlePath(point)"
                  @pointerdown.stop="startMeasurePointDrag(item.id, index, $event)"
                />
              </template>
            </template>
          </template>
          <template v-for="item in playerItems" :key="`${item.id}-marker`">
            <path
              class="media-stage__player"
              :class="{ 'media-stage__player--selected': isSelectedCanvasItem(item) }"
              :d="playerPath(item)"
              :stroke="markerColor(item)"
              :stroke-opacity="item.opacity ?? 1"
              @pointerdown.stop="startPlayerDrag(item, $event)"
            />
            <text
              class="media-stage__player-label"
              :x="item.point.x + 1.6"
              :y="item.point.y - 1.6"
            >
              {{ item.label }}
            </text>
          </template>
          <template v-if="selectedItem">
            <template v-for="handle in selectedHandles" :key="handle.key">
            <path
              v-if="handle.shape === 'plus'"
              class="media-stage__handle media-stage__handle--plus"
              :d="plusHandlePath(handle)"
              @pointerdown.stop="startHandleDrag(handle, $event)"
            />
            <text
              v-if="handle.label"
              class="media-stage__handle-label"
              :x="handle.x + 1.4"
              :y="handle.y - 1.4"
            >
              {{ handle.label }}
            </text>
            <circle
              v-else
              class="media-stage__handle"
              :cx="handle.x"
              :cy="handle.y"
              r="1.2"
              @pointerdown.stop="startHandleDrag(handle, $event)"
            />
            </template>
          </template>
        </svg>

        <div v-if="!timeline.state.videoUrl" class="media-stage__empty">
          <span>Select a video or image file</span>
          <IconButton icon="upload" title="Select video" @click.stop="selectVideo" />
        </div>
        <div v-if="activeChrono" class="media-stage__chrono">
          {{ chronoLabel(activeChrono) }}
        </div>
        <div v-if="activeDelay" class="media-stage__delay-indicator" aria-hidden="true">
          <span></span>
          <span></span>
        </div>
        </div>
        </div>
        <Court2DView
          v-if="stageView !== 'video'"
          class="media-stage__court-pane"
          :class="{ 'media-stage__pane--active': services.stageService.activePanel === 'court' }"
          :content-style="courtContentStyle"
          @pointerdown.stop="services.stageService.activePanel = 'court'"
        />
      </div>

      <div class="media-stage__toolbar">
        <label class="media-stage__speed">
          <span>◉</span>
          <input type="range" min="0.25" max="4" step="0.25" :value="timeline.state.speed" @input="timeline.setSpeed($event.target.value)" />
          <span>{{ timeline.state.speed.toFixed(2).replace(/0$/, '') }}</span>
        </label>

        <div class="media-stage__controls">
          <IconButton icon="start" title="Go to start of video" @click="timeline.setCurrentTime(0)" />
          <IconButton icon="step-back" title="Frame back (Left)" @click="timeline.frame(-1)" />
          <IconButton icon="back" title="Second back (Shift+Left)" @click="timeline.seek(-1)" />
          <IconButton :icon="timeline.state.isPlaying ? 'pause' : 'play'" title="Play/Pause (Space)" @click="timeline.togglePlay()" />
          <IconButton icon="forward" title="Second forward (Shift+Right)" @click="timeline.seek(1)" />
          <IconButton icon="step-forward" title="Frame forward (Right)" @click="timeline.frame(1)" />
        </div>

        <input
          v-if="isEditingTime"
          ref="timeInputRef"
          v-model="timeInput"
          class="media-stage__time media-stage__time-input"
          @keydown.enter="applyTimeInput"
          @keydown.esc="cancelTimeInput"
          @blur="applyTimeInput"
        />
        <button v-else class="media-stage__time media-stage__time-button" type="button" @click="startTimeEdit">
          {{ formatTime(timeline.state.currentTime) }}
        </button>
        <div class="media-stage__actions">
          <IconButton icon="upload" title="Load video or image" @click.stop="selectVideo" />
          <button class="media-stage__zoom-reset" type="button" @click="resetZoom">100%</button>
          <div class="media-stage__view-switch" role="group" aria-label="Stage view">
            <button type="button" :class="{ 'media-stage__view-button--active': stageView === 'video' }" @click="setStageView('video')">Canvas</button>
            <button type="button" :class="{ 'media-stage__view-button--active': stageView === 'split' }" @click="setStageView('split')">Split</button>
            <button type="button" :class="{ 'media-stage__view-button--active': stageView === 'court' }" @click="setStageView('court')">2D</button>
          </div>
          <IconButton icon="event" title="Add event (P)" @click="events.add()" />
        </div>
      </div>
    </div>
  </EditorPanel>
</template>

<script setup>
import { computed, inject, nextTick, onBeforeUnmount, onMounted, ref, watch, watchEffect } from "vue";
import EditorPanel from "@/components/common/EditorPanel.vue";
import IconButton from "@/components/common/IconButton.vue";
import Court2DView from "@/features/stage/Court2DView.vue";
import { SERVICES_KEY } from "@/services/ServiceRegistry.js";

const services = inject(SERVICES_KEY);
const timeline = services.timelineService;
const events = services.eventsService;
const draw = services.drawService;
const measure = services.measureService;
const keyframes = services.keyframeService;
const videoRef = ref(null);
const viewportRef = ref(null);
const mediaPaneRef = ref(null);
const mediaContentRef = ref(null);
const fileInput = ref(null);
const timeInputRef = ref(null);
const isEditingTime = ref(false);
const timeInput = ref("");
const isDrawing = ref(false);
const viewportAspect = ref(1);
const mediaAspect = ref(16 / 9);
const mediaPaneSize = ref({ width: 0, height: 0 });
const zoom = ref(1);
const zoomOrigin = ref({ x: 50, y: 50 });
const pan = ref({ x: 0, y: 0 });
const courtZoom = ref(1);
const courtZoomOrigin = ref({ x: 50, y: 50 });
const courtPan = ref({ x: 0, y: 0 });
const panDrag = ref(null);
const isSpacePressed = ref(false);
const stageView = ref("video");
const fieldLabels = ["A", "B", "C", "D"];
const canUseCanvas = computed(() => stageView.value !== "court" && (draw.state.mode === "move" || !!draw.state.selectedTool || !!measure.state.selectedTool || !!measure.state.editMode));
const activeZoom = computed(() => services.stageService.activePanel === "court" ? courtZoom.value : zoom.value);
const mediaContentStyle = computed(() => {
  const paneWidth = mediaPaneSize.value.width;
  const paneHeight = mediaPaneSize.value.height;
  const aspect = mediaAspect.value || 16 / 9;
  if (!paneWidth || !paneHeight) return {};

  const paneAspect = paneWidth / paneHeight;
  if (paneAspect > aspect) {
    return {
      width: `${paneHeight * aspect}px`,
      height: `${paneHeight}px`,
      transform: `translate(${pan.value.x}px, ${pan.value.y}px) scale(${zoom.value})`,
      transformOrigin: `${zoomOrigin.value.x}% ${zoomOrigin.value.y}%`
    };
  }

  return {
    width: `${paneWidth}px`,
    height: `${paneWidth / aspect}px`,
    transform: `translate(${pan.value.x}px, ${pan.value.y}px) scale(${zoom.value})`,
    transformOrigin: `${zoomOrigin.value.x}% ${zoomOrigin.value.y}%`
  };
});
const courtContentStyle = computed(() => ({
  transform: `translate(${courtPan.value.x}px, ${courtPan.value.y}px) scale(${courtZoom.value})`,
  transformOrigin: `${courtZoomOrigin.value.x}% ${courtZoomOrigin.value.y}%`
}));
const isMoveLocked = computed(() => draw.state.mode === "move" || !!measure.state.editMode);

const visibleItems = computed(() => {
  const currentTime = timeline.state.currentTime;
  return (services.projectService.state.data.items || []).filter((item) => {
    if (item.visible === false) return false;
    const from = Number.isFinite(item.time_from) ? item.time_from : 0;
    const to = Number.isFinite(item.time_to) ? item.time_to : from;
    return currentTime >= from && currentTime <= to;
  }).map((item) => {
    const isActiveDrawEdit = item.id === draw.state.selectedItemId && draw.state.mode === "move";
    const isActiveMeasureEdit = item.id === measure.state.selectedItemId && !!measure.state.editMode;
    return isActiveDrawEdit || isActiveMeasureEdit ? item : keyframes.itemAtTime(item, currentTime);
  });
});
const selectedItem = computed(() => {
  if (draw.state.draftItem) return draw.state.draftItem;
  return visibleItems.value.find((item) => item.id === draw.state.selectedItemId) || null;
});
const drawableItems = computed(() => {
  const items = [...visibleItems.value];
  if (draw.state.draftItem) {
    items.push(draw.state.draftItem);
  }
  if (measure.state.draftItem) {
    items.push(measure.state.draftItem);
  }
  return items;
});
const squareCircleGuideItems = computed(() => drawableItems.value.filter((item) => item.type === "square" && item.asCircle && item.points?.length >= 4));
const shapeItems = computed(() => drawableItems.value.filter((item) => !["measure-grid", "chrono", "player", "ball", "delay", "vertical-projection"].includes(item.type)));
const measureLineItems = computed(() => drawableItems.value.filter((item) => item.type === "measure-line"));
const projectionItems = computed(() => drawableItems.value.filter((item) => item.type === "vertical-projection" && item.points?.length >= 5));
const playerItems = computed(() => drawableItems.value.filter((item) => ["player", "ball"].includes(item.type) && item.point));
const visibleGrid = computed(() => visibleItems.value.find((item) => item.type === "measure-grid") || null);
watchEffect(() => {
  measure.state.displayGrid = visibleGrid.value;
});
const showGridHandles = computed(() => !!visibleGrid.value && visibleGrid.value.visible !== false);
const activeGridPoints = computed(() => visibleGrid.value?.points || []);
const activeChessCenter = computed(() => {
  const grid = visibleGrid.value;
  if (!grid?.chessboard) return null;
  const width = Number(grid.abMeters) || 0;
  const height = Number(grid.acMeters) || 0;
  return measure.worldToImage({
    x: Number.isFinite(Number(grid.chessCenterX)) ? Number(grid.chessCenterX) : width / 2,
    y: Number.isFinite(Number(grid.chessCenterY)) ? Number(grid.chessCenterY) : height / 2
  });
});
const gridLineWidth = computed(() => Math.max(1, Number(visibleGrid.value?.width) || 2));
const gridProjectionOpacity = computed(() => Math.max(0, Math.min(1, (Number(visibleGrid.value?.opacity) || 0.85) / 2)));
const fieldPath = computed(() => {
  if (!visibleGrid.value) return "";
  const [a, b, c, d] = activeGridPoints.value;
  if (!a || !b || !c || !d) return "";
  return `M ${a.x} ${a.y} L ${b.x} ${b.y} L ${d.x} ${d.y} L ${c.x} ${c.y} Z`;
});
const chessboardPaths = computed(() => {
  const grid = visibleGrid.value;
  if (!grid?.chessboard) return [];
  const width = Number(grid.abMeters) || 0;
  const height = Number(grid.acMeters) || 0;
  const squareSize = Math.max(0.01, Number(grid.chessSquareMeters) || 1);
  if (width <= 0 || height <= 0) return [];
  const projectionDistance = Math.max(0.01, Number(grid.projectionDistance) || 1);
  const projectionX = grid.projection ? Math.max(0, Math.round(Number(grid.projectionLoopsX) || 0)) * projectionDistance : 0;
  const projectionY = grid.projection ? Math.max(0, Math.round(Number(grid.projectionLoopsY) || 0)) * projectionDistance : 0;
  const xMin = -projectionX;
  const xMax = width + projectionX;
  const yMin = -projectionY;
  const yMax = height + projectionY;
  const originX = Number.isFinite(Number(grid.chessCenterX)) ? Number(grid.chessCenterX) : width / 2;
  const originY = Number.isFinite(Number(grid.chessCenterY)) ? Number(grid.chessCenterY) : height / 2;
  const startCol = Math.floor((xMin - originX) / squareSize);
  const endCol = Math.ceil((xMax - originX) / squareSize);
  const startRow = Math.floor((yMin - originY) / squareSize);
  const endRow = Math.ceil((yMax - originY) / squareSize);
  const paths = [];
  const pointAt = (x, y) => measure.worldToImage({ x, y });
  for (let row = startRow; row < endRow; row += 1) {
    for (let col = startCol; col < endCol; col += 1) {
      if ((col + row) % 2 !== 0) continue;
      const left = Math.max(xMin, originX + col * squareSize);
      const right = Math.min(xMax, originX + (col + 1) * squareSize);
      const top = Math.max(yMin, originY + row * squareSize);
      const bottom = Math.min(yMax, originY + (row + 1) * squareSize);
      if (right <= left || bottom <= top) continue;
      const p1 = pointAt(left, top);
      const p2 = pointAt(right, top);
      const p3 = pointAt(right, bottom);
      const p4 = pointAt(left, bottom);
      if (!p1 || !p2 || !p3 || !p4) continue;
      paths.push(`M ${p1.x} ${p1.y} L ${p2.x} ${p2.y} L ${p3.x} ${p3.y} L ${p4.x} ${p4.y} Z`);
    }
  }
  return paths;
});
const projectionLines = computed(() => {
  const grid = visibleGrid.value;
  if (!grid?.projection) return [];

  const width = Number(grid.abMeters) || 0;
  const height = Number(grid.acMeters) || 0;
  const distance = Math.max(0.01, Number(grid.projectionDistance) || 1);
  const loopsX = Math.max(0, Math.round(Number(grid.projectionLoopsX) || 0));
  const loopsY = Math.max(0, Math.round(Number(grid.projectionLoopsY) || 0));
  if (width <= 0 || height <= 0 || (!loopsX && !loopsY)) return [];

  const lines = [];
  const xMin = -loopsX * distance;
  const xMax = width + loopsX * distance;
  const yMin = -loopsY * distance;
  const yMax = height + loopsY * distance;
  const addLine = (key, start, end) => {
    const imageStart = measure.worldToImage(start);
    const imageEnd = measure.worldToImage(end);
    if (!imageStart || !imageEnd) return;
    lines.push({
      key,
      path: `M ${imageStart.x} ${imageStart.y} L ${imageEnd.x} ${imageEnd.y}`
    });
  };

  for (let index = 1; index <= loopsX; index += 1) {
    const offset = index * distance;
    addLine(`left-${index}`, { x: -offset, y: yMin }, { x: -offset, y: yMax });
    addLine(`right-${index}`, { x: width + offset, y: yMin }, { x: width + offset, y: yMax });
  }

  for (let index = 1; index <= loopsY; index += 1) {
    const offset = index * distance;
    addLine(`top-${index}`, { x: xMin, y: -offset }, { x: xMax, y: -offset });
    addLine(`bottom-${index}`, { x: xMin, y: height + offset }, { x: xMax, y: height + offset });
  }

  return lines;
});

const activeChrono = computed(() => visibleItems.value.find((item) => item.type === "chrono") || null);
const activeDelay = computed(() => timeline.activeDelayAt?.(timeline.state.currentTime) || null);
const selectedHandles = computed(() => {
  const item = selectedItem.value;
  if (!item || item.type === "free-line") return [];

  if (item.type === "circle") {
    const circle = circleFor(item);
    if (!circle) return [];
    const handles = [
      { key: "center", mode: "move", x: circle.center.x, y: circle.center.y },
      { key: "radius", mode: "radius", x: circleHandlePoint(circle, "radius").x, y: circleHandlePoint(circle, "radius").y }
    ];
    if (item.oval) {
      handles.push({ key: "height", mode: "height", x: circleHandlePoint(circle, "height").x, y: circleHandlePoint(circle, "height").y });
    }
    return handles;
  }

  return (item.points || []).map((point, index) => ({
    key: `point-${index}`,
    mode: "point",
    shape: "plus",
    label: item.type === "measure-grid" ? fieldLabels[index] : `Point ${index + 1}`,
    index,
    x: point.x,
    y: point.y
  }));
});

const selectVideo = async () => {
  if (!window.pywebview?.api?.choose_video_file) {
    fileInput.value?.click();
    return;
  }

  const loadedFromPicker = await timeline.loadFromPicker();
  if (!loadedFromPicker) {
    fileInput.value?.click();
  }
};

const setStageView = (view) => {
  stageView.value = view;
  if (view === "video") {
    services.stageService.activePanel = "canvas";
  } else if (view === "split") {
    services.stageService.activePanel = services.stageService.activePanel === "court" ? "court" : "canvas";
  } else if (view === "court") {
    services.stageService.activePanel = "court";
  }
};

const onFileChange = async (event) => {
  await timeline.loadFile(event?.target?.files?.[0]);
};

const pointFromEvent = (event) => {
  const bounds = mediaContentRef.value?.getBoundingClientRect() || mediaPaneRef.value?.getBoundingClientRect() || viewportRef.value?.getBoundingClientRect() || event.currentTarget.getBoundingClientRect();
  return {
    x: ((event.clientX - bounds.left) / bounds.width) * 100,
    y: ((event.clientY - bounds.top) / bounds.height) * 100
  };
};

const updateViewportAspect = () => {
  const paneBounds = mediaPaneRef.value?.getBoundingClientRect();
  mediaPaneSize.value = {
    width: paneBounds?.width || 0,
    height: paneBounds?.height || 0
  };
  const bounds = mediaContentRef.value?.getBoundingClientRect() || viewportRef.value?.getBoundingClientRect();
  viewportAspect.value = bounds?.width && bounds?.height ? bounds.width / bounds.height : 1;
};

const onVideoMetadata = () => {
  timeline.setDuration(videoRef.value?.duration);
  if (videoRef.value?.videoWidth && videoRef.value?.videoHeight) {
    mediaAspect.value = videoRef.value.videoWidth / videoRef.value.videoHeight;
  }
  syncVideoToTimeline(true);
  updateViewportAspect();
};

const onImageLoad = (event) => {
  timeline.setDuration(timeline.state.duration || 10);
  const image = event.target;
  if (image?.naturalWidth && image?.naturalHeight) {
    mediaAspect.value = image.naturalWidth / image.naturalHeight;
  }
  updateViewportAspect();
};

const onCanvasPointerDown = (event) => {
  if (beginPan(event)) return;
  if (stageView.value === "court") return;
  if (!timeline.state.videoUrl) return;
  if (measure.state.selectedTool || measure.state.editMode) {
    isDrawing.value = true;
    viewportRef.value?.setPointerCapture?.(event.pointerId);
    measure.begin(pointFromEvent(event));
    return;
  }
  if (draw.state.mode === "move" && !draw.selectedItem) return;
  if (draw.state.mode !== "move" && !draw.state.selectedTool) return;
  if (draw.state.mode !== "move" && draw.state.selectedTool === "polyline") {
    draw.addPolylinePoint(pointFromEvent(event));
    return;
  }
  isDrawing.value = true;
  viewportRef.value?.setPointerCapture?.(event.pointerId);
  draw.begin(pointFromEvent(event));
};

const onCanvasWheel = (event) => {
  if (services.stageService.activePanel === "canvas" && !timeline.state.videoUrl) return;
  const direction = event.deltaY > 0 ? -1 : 1;
  const factor = direction > 0 ? 1.12 : 1 / 1.12;
  if (services.stageService.activePanel === "court") {
    courtZoomOrigin.value = { x: 50, y: 50 };
    courtZoom.value = Math.min(6, Math.max(0.25, courtZoom.value * factor));
    return;
  }
  zoomOrigin.value = { x: 50, y: 50 };
  zoom.value = Math.min(6, Math.max(0.25, zoom.value * factor));
  nextTick(updateViewportAspect);
};

const resetZoom = () => {
  if (services.stageService.activePanel === "court") {
    courtZoom.value = 1;
    courtZoomOrigin.value = { x: 50, y: 50 };
    courtPan.value = { x: 0, y: 0 };
    return;
  }
  zoom.value = 1;
  zoomOrigin.value = { x: 50, y: 50 };
  pan.value = { x: 0, y: 0 };
  nextTick(updateViewportAspect);
};

const onCanvasPointerMove = (event) => {
  if (panDrag.value) {
    const nextPan = {
      x: panDrag.value.startPan.x + event.clientX - panDrag.value.startX,
      y: panDrag.value.startPan.y + event.clientY - panDrag.value.startY
    };
    if (panDrag.value.panel === "court") {
      courtPan.value = nextPan;
    } else {
      pan.value = nextPan;
    }
    return;
  }
  if (!isDrawing.value) return;
  if (measure.state.selectedTool || measure.state.editMode || measure.state.draftItem) {
    measure.update(pointFromEvent(event));
    return;
  }
  draw.update(pointFromEvent(event));
};

const onCanvasPointerUp = (event) => {
  if (panDrag.value) {
    panDrag.value = null;
    viewportRef.value?.releasePointerCapture?.(event.pointerId);
    return;
  }
  if (!isDrawing.value) return;
  isDrawing.value = false;
  if (measure.state.selectedTool || measure.state.editMode || measure.state.draftItem) {
    measure.finish(pointFromEvent(event));
    return;
  }
  draw.finish(pointFromEvent(event));
};

const beginPan = (event) => {
  if (activeZoom.value === 1) return false;
  if (!isSpacePressed.value && event.button !== 2) return false;

  panDrag.value = {
    panel: services.stageService.activePanel,
    startX: event.clientX,
    startY: event.clientY,
    startPan: services.stageService.activePanel === "court" ? { ...courtPan.value } : { ...pan.value }
  };
  viewportRef.value?.setPointerCapture?.(event.pointerId);
  event.preventDefault();
  return true;
};

const selectCanvasItem = (item, event = null) => {
  if (isMoveLocked.value && !isSelectedCanvasItem(item)) return;
  if (item.type === "measure-line" || item.type === "measure-grid" || item.type === "chrono" || item.type === "player" || item.type === "ball" || item.type === "vertical-projection") {
    measure.state.selectedItemId = item.id;
    draw.selectItem(null);
    if (event && measure.isActiveImageMove?.(item.id)) {
      isDrawing.value = true;
      viewportRef.value?.setPointerCapture?.(event.pointerId);
      measure.begin(pointFromEvent(event));
    }
    return;
  }
  draw.selectItem(item.id);
  measure.state.selectedItemId = null;
};

const isSelectedCanvasItem = (item) => {
  if (item.type === "measure-line" || item.type === "measure-grid" || item.type === "chrono" || item.type === "player" || item.type === "ball" || item.type === "vertical-projection") return item.id === measure.state.selectedItemId;
  return item.id === draw.state.selectedItemId;
};

const startHandleDrag = (handle, event) => {
  if (!selectedItem.value) return;
  if (handle.mode === "point") {
    draw.startMovePoint(selectedItem.value.id, handle.index);
  } else if (handle.mode === "radius") {
    draw.startResizeCircle(selectedItem.value.id);
  } else if (handle.mode === "height") {
    draw.startResizeCircleHeight(selectedItem.value.id);
  } else {
    draw.startMoveSelected(selectedItem.value.id);
  }

  isDrawing.value = true;
  viewportRef.value?.setPointerCapture?.(event.pointerId);
  draw.begin(pointFromEvent(event));
};

const startFieldPointDrag = (index, event) => {
  if (isMoveLocked.value && !measure.isActiveFieldPoint(index)) return;
  measure.startMoveFieldPoint(index);
  isDrawing.value = true;
  viewportRef.value?.setPointerCapture?.(event.pointerId);
  measure.begin(pointFromEvent(event));
};

const startChessCenterDrag = (event) => {
  if (isMoveLocked.value && !measure.isActiveChessCenter()) return;
  measure.startMoveChessCenter();
  isDrawing.value = true;
  viewportRef.value?.setPointerCapture?.(event.pointerId);
  measure.begin(pointFromEvent(event));
};

const startMeasurePointDrag = (id, index, event) => {
  if (isMoveLocked.value && !measure.isActiveMeasurePoint(id, index)) return;
  measure.startMoveMeasurePoint(id, index);
  isDrawing.value = true;
  viewportRef.value?.setPointerCapture?.(event.pointerId);
  measure.begin(pointFromEvent(event));
};

const startPlayerDrag = (item, event) => {
  if (isMoveLocked.value && !measure.isActivePlayer(item.id) && !measure.isActiveImageMove?.(item.id)) return;
  if (!measure.isActiveImageMove?.(item.id)) {
    measure.startMovePlayer(item.id);
  }
  isDrawing.value = true;
  viewportRef.value?.setPointerCapture?.(event.pointerId);
  measure.begin(pointFromEvent(event));
};

const pathFor = (item) => {
  if (item.type === "free-line" && item.path) {
    return item.path;
  }

  const points = item.points || [];
  if (item.type === "measure-line") {
    return points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ");
  }

  if (item.type === "circle") {
    const circle = circleFor(item);
    if (!circle) return "";
    if (!item.oval) {
      const radiusX = circle.radius / viewportAspect.value;
      return `M ${circle.center.x - radiusX} ${circle.center.y} a ${radiusX} ${circle.radius} 0 1 0 ${radiusX * 2} 0 a ${radiusX} ${circle.radius} 0 1 0 ${radiusX * -2} 0`;
    }
    return ellipsePath(circle, item.oval);
  }

  if (item.type === "square" && item.asCircle && points.length >= 4) {
    return bezierClosedPath(points);
  }

  if (["triangle", "square", "polygon"].includes(item.type) || (item.type === "polyline" && item.closed)) {
    return points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ") + " Z";
  }

  return points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ");
};

const goalProjectionFillPath = (item) => {
  const [a, b, projectionB, projectionA, c] = item.points || [];
  if (!a || !b || !projectionB || !projectionA || !c) return "";
  return `M ${a.x} ${a.y} L ${b.x} ${b.y} L ${c.x} ${c.y} Z M ${projectionA.x} ${projectionA.y} L ${projectionB.x} ${projectionB.y} L ${c.x} ${c.y} Z`;
};

const goalProjectionLinePath = (item) => {
  const [a, b, projectionB, projectionA, c] = item.points || [];
  if (!a || !b || !projectionB || !projectionA || !c) return "";
  return [
    `M ${a.x} ${a.y} L ${b.x} ${b.y}`,
    `M ${projectionA.x} ${projectionA.y} L ${projectionB.x} ${projectionB.y}`,
    `M ${a.x} ${a.y} L ${c.x} ${c.y} L ${b.x} ${b.y}`,
    `M ${projectionA.x} ${projectionA.y} L ${c.x} ${c.y} L ${projectionB.x} ${projectionB.y}`
  ].join(" ");
};

const projectionPointLabel = (index) => ["u", "v", "V", "U", "C"][index] || `P${index + 1}`;

const linearClosedPath = (points) => {
  if (!points.length) return "";
  return points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ") + " Z";
};

const bezierClosedPath = (points) => {
  const curvePoints = points.slice(0, 4);
  const tension = 0.42;
  return curvePoints.map((point, index) => {
    const previous = curvePoints[(index - 1 + curvePoints.length) % curvePoints.length];
    const next = curvePoints[(index + 1) % curvePoints.length];
    const nextNext = curvePoints[(index + 2) % curvePoints.length];
    const controlA = {
      x: point.x + (next.x - previous.x) * tension,
      y: point.y + (next.y - previous.y) * tension
    };
    const controlB = {
      x: next.x - (nextNext.x - point.x) * tension,
      y: next.y - (nextNext.y - point.y) * tension
    };
    return `${index === 0 ? `M ${point.x} ${point.y}` : ""} C ${controlA.x} ${controlA.y} ${controlB.x} ${controlB.y} ${next.x} ${next.y}`;
  }).join(" ") + " Z";
};

const circleFor = (item) => {
  if (item.center && Number.isFinite(item.radius)) {
    return {
      center: item.center,
      radius: item.radius,
      height: Number.isFinite(item.height) ? item.height : item.radius,
      rotation: Number.isFinite(item.rotation) ? item.rotation : 0
    };
  }

  const [start, end] = item.points || [];
  if (!start || !end) return null;

  return {
    center: {
      x: (start.x + end.x) / 2,
      y: (start.y + end.y) / 2
    },
    radius: Math.max(Math.abs(end.x - start.x), Math.abs(end.y - start.y)) / 2,
    height: Math.max(Math.abs(end.x - start.x), Math.abs(end.y - start.y)) / 2,
    rotation: 0
  };
};

const ellipsePath = (circle, oval) => {
  const rx = circle.radius / viewportAspect.value;
  const ry = oval ? circle.height : circle.radius;
  const rotation = ((circle.rotation || 0) * Math.PI) / 180;
  const points = Array.from({ length: 64 }, (_, index) => {
    const angle = (index / 64) * Math.PI * 2;
    const localX = Math.cos(angle) * rx;
    const localY = Math.sin(angle) * ry;
    return {
      x: circle.center.x + localX * Math.cos(rotation) - localY * Math.sin(rotation),
      y: circle.center.y + localX * Math.sin(rotation) + localY * Math.cos(rotation)
    };
  });
  return linearClosedPath(points);
};

const circleHandlePoint = (circle, axis) => {
  const rotation = ((circle.rotation || 0) * Math.PI) / 180;
  const distance = axis === "height" ? circle.height : circle.radius;
  const angle = axis === "height" ? rotation + Math.PI / 2 : rotation;
  return {
    x: circle.center.x + Math.cos(angle) * distance,
    y: circle.center.y + Math.sin(angle) * distance
  };
};

const plusHandlePath = (handle) => {
  const size = 1.8;
  return `M ${handle.x - size} ${handle.y} L ${handle.x + size} ${handle.y} M ${handle.x} ${handle.y - size} L ${handle.x} ${handle.y + size}`;
};

const playerPath = (item) => {
  const bounds = viewportRef.value?.getBoundingClientRect();
  const width = bounds?.width || 1;
  const height = bounds?.height || 1;
  const halfWidth = ((Number(item.width) || measure.state.playerConfig.widthPx) / width) * 50;
  const halfLength = ((Number(item.length) || measure.state.playerConfig.lengthPx) / height) * 50;
  const point = item.point;
  return `M ${point.x - halfWidth} ${point.y} L ${point.x + halfWidth} ${point.y} M ${point.x} ${point.y - halfLength} L ${point.x} ${point.y + halfLength}`;
};

const markerColor = (item) => {
  if (item.type === "ball") return item.color || measure.state.playerConfig.ballColor;
  if (item.type === "player") {
    return item.team === "home" ? measure.state.playerConfig.homeColor : measure.state.playerConfig.guestColor;
  }
  return item.color || "#fff";
};

const measureLineCenter = (item) => {
  const [start, end] = item.points || [];
  if (!start || !end) return { x: 0, y: 0 };
  return { x: (start.x + end.x) / 2, y: (start.y + end.y) / 2 };
};

const measureLineLabel = (item) => {
  const meters = measure.measureLineMeters(item);
  if (!Number.isFinite(meters)) return "";
  return `${meters.toFixed(2)} m`;
};

const chronoLabel = (item) => {
  const duration = Math.max(0, (Number(item.time_to) || 0) - (Number(item.time_from) || 0));
  const elapsed = Math.min(duration, Math.max(0, timeline.state.currentTime - (Number(item.time_from) || 0)));
  return formatTime(elapsed);
};

const fillFor = (item) => {
  if (item.type === "measure-line") return "none";
  if (["triangle", "square", "polygon", "circle"].includes(item.type) || (item.type === "polyline" && item.closed)) {
    return item.color;
  }
  return "none";
};

const fillOpacityFor = (item) => {
  if (item.type === "polyline" && item.closed) return Number.isFinite(item.fillOpacity) ? item.fillOpacity : 0.4;
  if (["triangle", "square", "polygon", "circle"].includes(item.type)) {
    return Number.isFinite(item.fillOpacity) ? item.fillOpacity : item.opacity;
  }
  return fillFor(item) === "none" ? 0 : item.opacity;
};

const strokeWidthFor = (item) => {
  const width = Number(item.width) || 2;
  if (item.type === "polyline") return Math.max(1.2, width / 2);
  return width / 4;
};

const strokeOpacityFor = (item) => item.type === "polyline" ? 1 : item.opacity;

const blendModeFor = (item) => {
  return item.fillMode || "normal";
};

const formatTime = (time) => {
  const value = Math.max(0, Number.isFinite(time) ? time : 0);
  const minutes = Math.floor(value / 60);
  const seconds = Math.floor(value % 60);
  const millis = Math.floor((value % 1) * 1000);
  return `00:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")},${String(millis).padStart(3, "0")}`;
};

const parseTime = (value) => {
  const normalizedValue = String(value || "").trim().replace(",", ".");
  const parts = normalizedValue.split(":").map(Number);

  if (parts.length === 1 && Number.isFinite(parts[0])) return parts[0];
  if (parts.length === 2 && parts.every(Number.isFinite)) return parts[0] * 60 + parts[1];
  if (parts.length === 3 && parts.every(Number.isFinite)) return parts[0] * 3600 + parts[1] * 60 + parts[2];

  return null;
};

const startTimeEdit = async () => {
  timeInput.value = formatTime(timeline.state.currentTime);
  isEditingTime.value = true;
  await nextTick();
  timeInputRef.value?.select();
};

const applyTimeInput = () => {
  const parsedTime = parseTime(timeInput.value);
  if (parsedTime !== null) {
    timeline.setCurrentTime(parsedTime);
  }
  isEditingTime.value = false;
};

const cancelTimeInput = () => {
  isEditingTime.value = false;
};

watch(
  () => timeline.state.isPlaying,
  (isPlaying) => {
    if (!videoRef.value) return;
    if (isPlaying) {
      syncVideoToTimeline(true);
      updateVideoPlaybackState();
      startPlaybackClock();
    } else {
      stopPlaybackClock();
      videoRef.value.pause();
    }
  }
);

watch(
  () => timeline.state.currentTime,
  (time) => {
    if (!videoRef.value || !Number.isFinite(time)) return;
    const sourceTime = timeline.displayToSourceTime?.(time) ?? time;
    if (timeline.state.isPlaying && !timeline.activeDelayAt?.(time)) return;
    syncVideoToTimeline(!timeline.state.isPlaying);
  }
);

watch(
  () => timeline.state.speed,
  () => updateVideoPlaybackState()
);

let playbackFrame = null;
let playbackLastTick = null;

const startPlaybackClock = () => {
  stopPlaybackClock();
  playbackLastTick = performance.now();
  const tick = (now) => {
    if (!timeline.state.isPlaying) return;
    const elapsed = ((now - playbackLastTick) / 1000) * timeline.state.speed;
    playbackLastTick = now;
    const nextTime = timeline.state.currentTime + elapsed;
    timeline.setCurrentTime(nextTime);
    updateVideoPlaybackState();
    if (nextTime >= timeline.getDisplayDuration()) {
      timeline.pause();
      return;
    }
    playbackFrame = requestAnimationFrame(tick);
  };
  playbackFrame = requestAnimationFrame(tick);
};

const syncVideoToTimeline = (force = false) => {
  if (!videoRef.value) return;
  const sourceTime = timeline.displayToSourceTime?.(timeline.state.currentTime) ?? timeline.state.currentTime;
  const tolerance = force ? 0.03 : 0.18;
  if (Math.abs(videoRef.value.currentTime - sourceTime) > tolerance) {
    videoRef.value.currentTime = sourceTime;
  }
};

const updateVideoPlaybackState = () => {
  if (!videoRef.value || timeline.state.mediaType === "image") return;
  videoRef.value.playbackRate = Math.max(0.0625, Number(timeline.state.speed) || 1);
  const delay = timeline.activeDelayAt?.(timeline.state.currentTime);
  if (!timeline.state.isPlaying || delay) {
    videoRef.value.pause();
    syncVideoToTimeline(!!delay);
    return;
  }
  syncVideoToTimeline(false);
  if (videoRef.value.paused) {
    videoRef.value.play().catch(() => {
      timeline.pause();
    });
  }
};

const stopPlaybackClock = () => {
  if (playbackFrame) {
    cancelAnimationFrame(playbackFrame);
    playbackFrame = null;
  }
  playbackLastTick = null;
};

watch(stageView, async () => {
  await nextTick();
  if (mediaPaneRef.value) {
    resizeObserver?.observe(mediaPaneRef.value);
  }
  updateViewportAspect();
});

const isTextInputTarget = (target) => {
  const element = target instanceof Element ? target : null;
  if (!element) return false;
  return !!element.closest("input, textarea, select, [contenteditable='true']");
};

const onKeyDown = (event) => {
  if (isTextInputTarget(event.target)) return;

  if (event.code === "Space") {
    event.preventDefault();
    timeline.togglePlay();
    return;
  }

  if (event.key === "p" || event.key === "P") {
    event.preventDefault();
    events.add();
    return;
  }

  if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
    event.preventDefault();
    const direction = event.key === "ArrowRight" ? 1 : -1;
    if (event.shiftKey) {
      timeline.seek(direction);
    } else {
      timeline.frame(direction);
    }
    return;
  }

  if (event.key !== "Enter") return;
  if (measure.state.editMode) {
    event.preventDefault();
    measure.finishMove();
    return;
  }
  if (draw.state.mode === "move") {
    event.preventDefault();
    draw.finishMoveMode();
    return;
  }

  if (draw.state.draftItem?.type === "polyline") {
    event.preventDefault();
    draw.finishPolyline();
  }
};

const onKeyUp = (event) => {
  if (event.code === "Space") {
    isSpacePressed.value = false;
  }
};

const onWindowPointerDown = (event) => {
  if (draw.state.draftItem?.type !== "polyline") return;
  if (viewportRef.value?.contains(event.target)) return;
  draw.finishPolyline();
};

window.addEventListener("keydown", onKeyDown);
window.addEventListener("keyup", onKeyUp);
window.addEventListener("pointerdown", onWindowPointerDown);

let resizeObserver = null;
onMounted(() => {
  updateViewportAspect();
  resizeObserver = new ResizeObserver(updateViewportAspect);
  if (viewportRef.value) {
    resizeObserver.observe(viewportRef.value);
  }
  if (mediaPaneRef.value) {
    resizeObserver.observe(mediaPaneRef.value);
  }
});

onBeforeUnmount(() => {
  stopPlaybackClock();
  window.removeEventListener("keydown", onKeyDown);
  window.removeEventListener("keyup", onKeyUp);
  window.removeEventListener("pointerdown", onWindowPointerDown);
  resizeObserver?.disconnect();
});
</script>

<style scoped>
.media-stage {
  height: 100%;
  display: grid;
  grid-template-rows: 1fr 68px;
  padding: 30px 22px 16px;
}

.media-stage__file {
  display: none;
}

.media-stage__viewport {
  position: relative;
  min-height: 0;
  display: grid;
  background: var(--surface-black);
}

.media-stage__viewport--split {
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
}

.media-stage__media-pane,
.media-stage__court-pane {
  position: relative;
  min-width: 0;
  min-height: 0;
  border: 1px solid transparent;
}

.media-stage__pane--active {
  border-color: var(--accent-primary);
}

.media-stage__media-pane {
  display: grid;
  place-items: center;
  overflow: hidden;
}

.media-stage__court-pane {
  overflow: hidden;
}

.media-stage__content {
  position: relative;
  max-width: 100%;
  max-height: 100%;
  will-change: transform;
  overflow: visible;
}

.media-stage__viewport--draw {
  cursor: crosshair;
}

.media-stage__viewport--pan {
  cursor: grab;
}

.media-stage__viewport--panning {
  cursor: grabbing;
}

.media-stage__video,
.media-stage__overlay {
  width: 100%;
  height: 100%;
}

.media-stage__video {
  object-fit: contain;
}

.media-stage__overlay {
  position: absolute;
  inset: 0;
  overflow: visible;
  pointer-events: auto;
}

.media-stage__shape {
  cursor: pointer;
}

.media-stage__field {
  fill: none;
  pointer-events: none;
  vector-effect: non-scaling-stroke;
}

.media-stage__projection-line {
  fill: none;
  pointer-events: none;
  vector-effect: non-scaling-stroke;
}

.media-stage__projection-fill {
  cursor: pointer;
}

.media-stage__field-square {
  opacity: 0.16;
  pointer-events: none;
}

.media-stage__shape--guide {
  stroke-dasharray: 2 2;
  pointer-events: none;
}

.media-stage__handle {
  fill: var(--text-color);
  stroke: var(--surface-black);
  stroke-width: 0.5;
  cursor: grab;
}

.media-stage__handle--plus {
  fill: none;
  stroke: var(--text-color);
  stroke-width: 0.7;
  vector-effect: non-scaling-stroke;
}

.media-stage__handle--active {
  stroke: var(--accent-primary);
}

.media-stage__handle-label {
  fill: var(--text-color);
  stroke: var(--surface-black);
  stroke-width: 0.25;
  paint-order: stroke;
  font-size: 3px;
  pointer-events: none;
}

.media-stage__measure-label {
  fill: var(--accent-primary);
  stroke: var(--surface-black);
  stroke-width: 0.45;
  paint-order: stroke;
  font-size: 3.4px;
  text-anchor: middle;
  dominant-baseline: middle;
  pointer-events: none;
}

.media-stage__player {
  fill: none;
  stroke-width: 2;
  vector-effect: non-scaling-stroke;
  cursor: grab;
}

.media-stage__player--selected {
  filter: drop-shadow(0 0 3px var(--accent-primary));
}

.media-stage__player-label {
  fill: var(--text-color);
  stroke: var(--surface-black);
  stroke-width: 0.3;
  paint-order: stroke;
  font-size: 2.6px;
  pointer-events: none;
}

.media-stage__empty {
  position: absolute;
  inset: 0;
  display: grid;
  place-content: center;
  gap: 14px;
  justify-items: center;
}

.media-stage__chrono {
  position: absolute;
  top: 18px;
  right: 18px;
  padding: 7px 10px;
  background: #000;
  color: #fff;
  font-variant-numeric: tabular-nums;
  font-size: 14px;
  line-height: 1;
  pointer-events: none;
}

.media-stage__delay-indicator {
  position: absolute;
  left: 18px;
  bottom: 18px;
  display: flex;
  gap: 5px;
  padding: 8px 9px;
  background: rgb(0 0 0 / 0.35);
  pointer-events: none;
}

.media-stage__delay-indicator span {
  width: 5px;
  height: 24px;
  background: rgb(0 0 0 / 0.72);
}

.media-stage__toolbar {
  display: grid;
  grid-template-columns: 210px auto 132px minmax(220px, auto);
  align-items: center;
  gap: 8px;
  background: var(--surface-control);
  padding: 10px 20px;
}

.media-stage__actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
}

.media-stage__view-switch {
  display: flex;
  border: 1px solid var(--surface-border);
}

.media-stage__view-switch button {
  height: 28px;
  border: 0;
  border-right: 1px solid var(--surface-border);
  padding: 0 8px;
  background: var(--surface-button);
  color: var(--text-muted);
  cursor: pointer;
}

.media-stage__view-switch button:last-child {
  border-right: 0;
}

.media-stage__view-switch .media-stage__view-button--active {
  color: var(--surface-black);
  background: var(--accent-primary);
}

.media-stage__speed,
.media-stage__controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.media-stage__zoom-reset {
  height: 32px;
  min-width: 54px;
  border: 1px solid var(--surface-border);
  background: var(--surface-button);
  color: var(--text-color);
  cursor: pointer;
}

.media-stage__speed input {
  width: 130px;
  accent-color: var(--accent-primary);
}

.media-stage__time {
  font-variant-numeric: tabular-nums;
}

.media-stage__time-button,
.media-stage__time-input {
  width: 132px;
  height: 32px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-color);
  text-align: left;
}

.media-stage__time-button {
  cursor: text;
}

.media-stage__time-input {
  border-color: var(--surface-border);
  background: var(--surface-button);
}
</style>
