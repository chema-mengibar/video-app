<template>
  <div class="court-2d">
    <svg
      ref="svgRef"
      class="court-2d__svg"
      :style="contentStyle"
      :viewBox="`${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`"
      preserveAspectRatio="xMidYMid meet"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointerleave="onPointerUp"
    >
      <rect class="court-2d__area" :x="viewBox.x" :y="viewBox.y" :width="viewBox.width" :height="viewBox.height" />
      <rect class="court-2d__field" x="0" y="0" :width="courtWidth" :height="courtHeight" />
      <rect
        v-for="square in chessboardSquares"
        :key="square.key"
        class="court-2d__chess-square"
        :x="square.x"
        :y="square.y"
        :width="square.width"
        :height="square.height"
        :fill="gridColor"
      />
      <path
        v-for="line in gridLines"
        :key="line.key"
        class="court-2d__grid-line"
        :d="line.path"
        :stroke="gridColor"
        :stroke-opacity="line.opacity"
        :stroke-width="gridStrokeWidth"
      />
      <g v-for="vertex in gridVertices" :key="vertex.label" class="court-2d__vertex">
        <circle :cx="vertex.x" :cy="vertex.y" :r="vertexRadius" />
        <text :x="vertex.labelX" :y="vertex.labelY">{{ vertex.label }}</text>
      </g>

      <path
        v-for="item in drawShapes"
        :key="item.id"
        class="court-2d__shape"
        :class="{ 'court-2d__shape--selected': item.selected }"
        :d="item.path"
        :stroke="item.color"
        :stroke-opacity="item.opacity"
        :stroke-width="shapeStrokeWidth(item)"
        :fill="item.fill"
        :fill-opacity="item.fillOpacity"
        @pointerdown.stop="selectDrawItem(item.source, $event)"
      />

      <line
        v-for="item in measureLines"
        :key="item.id"
        class="court-2d__measure"
        :x1="item.start.x"
        :y1="item.start.y"
        :x2="item.end.x"
        :y2="item.end.y"
        @pointerdown.stop="selectMeasureItem(item.source, $event)"
      />

      <g v-for="item in playerDots" :key="item.id">
        <circle
          class="court-2d__player"
          :cx="item.point.x"
          :cy="item.point.y"
          :r="playerRadius"
          :fill="item.color || '#fff'"
          @pointerdown.stop="selectMeasureItem(item.source, $event)"
        />
        <text class="court-2d__label" :x="item.point.x + playerRadius * 1.5" :y="item.point.y - playerRadius">{{ item.label }}</text>
      </g>
    </svg>
    <div v-if="activeChrono" class="court-2d__chrono">{{ chronoLabel(activeChrono) }}</div>
  </div>
</template>

<script setup>
import { computed, inject, ref } from "vue";
import { SERVICES_KEY } from "@/services/ServiceRegistry.js";

defineProps({
  contentStyle: {
    type: Object,
    default: () => ({})
  }
});

const services = inject(SERVICES_KEY);
const timeline = services.timelineService;
const measure = services.measureService;
const project = services.projectService;
const draw = services.drawService;
const keyframes = services.keyframeService;
const svgRef = ref(null);
const isDragging = ref(false);
const dragTarget = ref(null);

const visibleItems = computed(() => {
  const currentTime = timeline.state.currentTime;
  return (project.state.data.items || []).filter((item) => {
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

const courtWidth = computed(() => Number(measure.gridItem?.abMeters) || 28.65);
const courtHeight = computed(() => Number(measure.gridItem?.acMeters) || 15.24);
const paddingX = computed(() => Math.max(0, Number(measure.gridItem?.paddingX) || 0));
const paddingY = computed(() => Math.max(0, Number(measure.gridItem?.paddingY) || 0));
const projectionDistance = computed(() => Math.max(0.01, Number(measure.gridItem?.projectionDistance) || 1));
const projectionLoopsX = computed(() => measure.gridItem?.projection ? Math.max(0, Math.round(Number(measure.gridItem?.projectionLoopsX) || 0)) : 0);
const projectionLoopsY = computed(() => measure.gridItem?.projection ? Math.max(0, Math.round(Number(measure.gridItem?.projectionLoopsY) || 0)) : 0);
const projectionPaddingX = computed(() => projectionLoopsX.value * projectionDistance.value);
const projectionPaddingY = computed(() => projectionLoopsY.value * projectionDistance.value);
const viewPaddingX = computed(() => Math.max(paddingX.value, projectionPaddingX.value));
const viewPaddingY = computed(() => Math.max(paddingY.value, projectionPaddingY.value));
const viewBox = computed(() => ({
  x: -viewPaddingX.value,
  y: -viewPaddingY.value,
  width: courtWidth.value + viewPaddingX.value * 2,
  height: courtHeight.value + viewPaddingY.value * 2
}));
const worldSpan = computed(() => Math.min(viewBox.value.width, viewBox.value.height));
const playerRadius = computed(() => worldSpan.value * 0.018);
const vertexRadius = computed(() => worldSpan.value * 0.014);
const gridColor = computed(() => measure.gridItem?.color || "#45FFA2");
const gridOpacity = computed(() => Math.max(0, Math.min(1, Number(measure.gridItem?.opacity) || 0.85)));
const projectionOpacity = computed(() => gridOpacity.value / 2);
const gridStrokeWidth = computed(() => Math.max(0.025, (Number(measure.gridItem?.width) || 2) * 0.025));
const chessSquareMeters = computed(() => Math.max(0.01, Number(measure.gridItem?.chessSquareMeters) || 1));
const chessCenterX = computed(() => Number.isFinite(Number(measure.gridItem?.chessCenterX)) ? Number(measure.gridItem.chessCenterX) : courtWidth.value / 2);
const chessCenterY = computed(() => Number.isFinite(Number(measure.gridItem?.chessCenterY)) ? Number(measure.gridItem.chessCenterY) : courtHeight.value / 2);
const drawableTypes = ["free-line", "straight-line", "polyline", "triangle", "square", "polygon", "circle"];
const gridVertices = computed(() => {
  const offset = Math.min(courtWidth.value, courtHeight.value) * 0.035;
  return [
    { label: "A", x: 0, y: 0, labelX: offset, labelY: offset * 1.6 },
    { label: "B", x: courtWidth.value, y: 0, labelX: courtWidth.value - offset * 2.2, labelY: offset * 1.6 },
    { label: "C", x: 0, y: courtHeight.value, labelX: offset, labelY: courtHeight.value - offset },
    { label: "D", x: courtWidth.value, y: courtHeight.value, labelX: courtWidth.value - offset * 2.2, labelY: courtHeight.value - offset }
  ];
});
const gridLines = computed(() => {
  const lines = [];
  const xMin = -viewPaddingX.value;
  const xMax = courtWidth.value + viewPaddingX.value;
  const yMin = -viewPaddingY.value;
  const yMax = courtHeight.value + viewPaddingY.value;

  if (measure.gridItem?.chessboard) {
    const startCol = Math.floor((xMin - chessCenterX.value) / chessSquareMeters.value);
    const endCol = Math.ceil((xMax - chessCenterX.value) / chessSquareMeters.value);
    const startRow = Math.floor((yMin - chessCenterY.value) / chessSquareMeters.value);
    const endRow = Math.ceil((yMax - chessCenterY.value) / chessSquareMeters.value);
    for (let col = startCol + 1; col < endCol; col += 1) {
      const x = chessCenterX.value + col * chessSquareMeters.value;
      lines.push({ key: `chess-x-${col}`, path: `M ${x} ${yMin} L ${x} ${yMax}`, opacity: gridOpacity.value });
    }
    for (let row = startRow + 1; row < endRow; row += 1) {
      const y = chessCenterY.value + row * chessSquareMeters.value;
      lines.push({ key: `chess-y-${row}`, path: `M ${xMin} ${y} L ${xMax} ${y}`, opacity: gridOpacity.value });
    }
  }

  for (let index = 1; index <= projectionLoopsX.value; index += 1) {
    const offset = index * projectionDistance.value;
    lines.push({ key: `projection-left-${index}`, path: `M ${-offset} ${yMin} L ${-offset} ${yMax}`, opacity: projectionOpacity.value });
    lines.push({ key: `projection-right-${index}`, path: `M ${courtWidth.value + offset} ${yMin} L ${courtWidth.value + offset} ${yMax}`, opacity: projectionOpacity.value });
  }
  for (let index = 1; index <= projectionLoopsY.value; index += 1) {
    const offset = index * projectionDistance.value;
    lines.push({ key: `projection-top-${index}`, path: `M ${xMin} ${-offset} L ${xMax} ${-offset}`, opacity: projectionOpacity.value });
    lines.push({ key: `projection-bottom-${index}`, path: `M ${xMin} ${courtHeight.value + offset} L ${xMax} ${courtHeight.value + offset}`, opacity: projectionOpacity.value });
  }
  return lines;
});
const chessboardSquares = computed(() => {
  if (!measure.gridItem?.chessboard) return [];
  const squares = [];
  const xMin = -viewPaddingX.value;
  const xMax = courtWidth.value + viewPaddingX.value;
  const yMin = -viewPaddingY.value;
  const yMax = courtHeight.value + viewPaddingY.value;
  const startCol = Math.floor((xMin - chessCenterX.value) / chessSquareMeters.value);
  const endCol = Math.ceil((xMax - chessCenterX.value) / chessSquareMeters.value);
  const startRow = Math.floor((yMin - chessCenterY.value) / chessSquareMeters.value);
  const endRow = Math.ceil((yMax - chessCenterY.value) / chessSquareMeters.value);
  for (let row = startRow; row < endRow; row += 1) {
    for (let col = startCol; col < endCol; col += 1) {
      if ((row + col) % 2 !== 0) continue;
      const left = Math.max(xMin, chessCenterX.value + col * chessSquareMeters.value);
      const right = Math.min(xMax, chessCenterX.value + (col + 1) * chessSquareMeters.value);
      const top = Math.max(yMin, chessCenterY.value + row * chessSquareMeters.value);
      const bottom = Math.min(yMax, chessCenterY.value + (row + 1) * chessSquareMeters.value);
      if (right <= left || bottom <= top) continue;
      squares.push({
        key: `chess-${row}-${col}`,
        x: left,
        y: top,
        width: right - left,
        height: bottom - top
      });
    }
  }
  return squares;
});

const playerDots = computed(() => visibleItems.value
  .filter((item) => ["player", "ball"].includes(item.type) && item.point)
  .map((item) => ({
    ...item,
    source: item,
    color: colorFor(item),
    point: measure.imageToWorld(item.point)
  }))
  .filter((item) => item.point));

const measureLines = computed(() => visibleItems.value
  .filter((item) => item.type === "measure-line" && item.points?.length >= 2)
  .map((item) => ({
    id: item.id,
    source: item,
    start: measure.imageToWorld(item.points[0]),
    end: measure.imageToWorld(item.points[1])
  }))
  .filter((item) => item.start && item.end));

const drawShapes = computed(() => visibleItems.value
  .filter((item) => drawableTypes.includes(item.type))
  .map((item) => {
    const path = worldPathFor(item);
    if (!path) return null;
    return {
      id: item.id,
      source: item,
      path,
      color: item.color || "#45FFA2",
      opacity: strokeOpacityFor(item),
      width: Number(item.width) || 2,
      fill: fillFor(item),
      fillOpacity: fillOpacityFor(item),
      selected: item.id === draw.state.selectedItemId
    };
  })
  .filter(Boolean));

const activeChrono = computed(() => visibleItems.value.find((item) => item.type === "chrono") || null);

const imagePointsFor = (item) => {
  if (item.type === "circle") {
    const circle = circleFor(item);
    if (!circle) return [];
    const radius = Number(circle.radius) || 1;
    return Array.from({ length: 48 }, (_, index) => {
      const angle = (index / 48) * Math.PI * 2;
      return {
        x: circle.center.x + Math.cos(angle) * radius,
        y: circle.center.y + Math.sin(angle) * radius
      };
    });
  }

  if (item.type === "free-line" && item.path) {
    return pathPoints(item.path);
  }

  return item.points || [];
};

const worldPathFor = (item) => {
  if (item.type === "circle") {
    return worldCirclePathFor(item);
  }

  const points = imagePointsFor(item)
    .map((point) => measure.imageToWorld(point))
    .filter(Boolean);
  if (points.length < 2) return "";

  const closed = ["triangle", "square", "polygon", "circle"].includes(item.type) || (item.type === "polyline" && item.closed);
  return points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ") + (closed ? " Z" : "");
};

const worldCirclePathFor = (item) => {
  const circle = circleFor(item);
  const center = circle ? measure.imageToWorld(circle.center) : null;
  if (!circle || !center) return "";

  const radiusPoint = measure.imageToWorld({
    x: circle.center.x + (Number(circle.radius) || 1),
    y: circle.center.y
  });
  if (!radiusPoint) return "";

  const radius = Math.max(0.01, Math.hypot(radiusPoint.x - center.x, radiusPoint.y - center.y));
  const points = Array.from({ length: 48 }, (_, index) => {
    const angle = (index / 48) * Math.PI * 2;
    return {
      x: center.x + Math.cos(angle) * radius,
      y: center.y + Math.sin(angle) * radius
    };
  });
  return points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ") + " Z";
};

const pathPoints = (path) => Array.from(String(path || "").matchAll(/[ML]\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)/g))
  .map((match) => ({ x: Number(match[1]), y: Number(match[2]) }));

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

const fillFor = (item) => {
  if (["triangle", "square", "polygon", "circle"].includes(item.type) || (item.type === "polyline" && item.closed)) {
    return item.color || "#45FFA2";
  }
  return "none";
};

const fillOpacityFor = (item) => {
  if (fillFor(item) === "none") return 0;
  return Number.isFinite(item.fillOpacity) ? item.fillOpacity : 0.4;
};

const shapeStrokeWidth = (item) => {
  const width = Number(item.width) || 2;
  if (item.type === "polyline") return Math.max(0.08, width * 0.05);
  return Math.max(0.04, width * 0.025);
};

const strokeOpacityFor = (item) => item.type === "polyline" ? 1 : Number.isFinite(item.opacity) ? item.opacity : 1;

const pointFromEvent = (event) => {
  const svg = svgRef.value;
  if (!svg) return null;
  const point = svg.createSVGPoint();
  point.x = event.clientX;
  point.y = event.clientY;
  const transformed = point.matrixTransform(svg.getScreenCTM().inverse());
  return { x: transformed.x, y: transformed.y };
};

const selectDrawItem = (item, event) => {
  services.stageService.activePanel = "court";
  draw.selectItem(item.id);
  measure.state.selectedItemId = null;
  beginMoveIfActive(event, "draw");
};

const selectMeasureItem = (item, event) => {
  services.stageService.activePanel = "court";
  measure.state.selectedItemId = item.id;
  draw.selectItem(null);
  beginMoveIfActive(event, "measure");
};

const imagePointFromWorldEvent = (event) => {
  const worldPoint = pointFromEvent(event);
  return worldPoint ? measure.worldToImage(worldPoint) : null;
};

const beginMoveIfActive = (event, target) => {
  const point = pointFromEvent(event);
  if (!point) return;

  if (target === "draw" && draw.isActiveWorldMove(draw.state.selectedItemId)) {
    dragTarget.value = "draw-world";
    isDragging.value = true;
    svgRef.value?.setPointerCapture?.(event.pointerId);
    draw.begin(point);
    return;
  }

  if (target === "measure" && measure.isActiveWorldMove(measure.state.selectedItemId)) {
    dragTarget.value = "measure-world";
    isDragging.value = true;
    svgRef.value?.setPointerCapture?.(event.pointerId);
    measure.begin(point);
  }
};

const onPointerDown = (event) => {
  services.stageService.activePanel = "court";
  if (!measure.gridItem) return;

  const imagePoint = imagePointFromWorldEvent(event);
  if (!imagePoint) return;

  if (measure.state.selectedTool || measure.state.editMode) {
    dragTarget.value = "measure-image";
    isDragging.value = true;
    svgRef.value?.setPointerCapture?.(event.pointerId);
    measure.begin(imagePoint);
    return;
  }

  if (draw.state.mode !== "move" && draw.state.selectedTool === "polyline") {
    draw.addPolylinePoint(imagePoint);
    return;
  }

  if (draw.state.mode !== "move" && draw.state.selectedTool) {
    dragTarget.value = "draw-image";
    isDragging.value = true;
    svgRef.value?.setPointerCapture?.(event.pointerId);
    draw.begin(imagePoint);
  }
};

const onPointerMove = (event) => {
  if (!isDragging.value) return;

  if (dragTarget.value === "draw-world") {
    const point = pointFromEvent(event);
    if (point) draw.update(point);
    return;
  }

  if (dragTarget.value === "measure-world") {
    const point = pointFromEvent(event);
    if (point) measure.update(point);
    return;
  }

  const imagePoint = imagePointFromWorldEvent(event);
  if (!imagePoint) return;

  if (dragTarget.value === "measure-image") {
    measure.update(imagePoint);
    return;
  }

  if (dragTarget.value === "draw-image") {
    draw.update(imagePoint);
  }
};

const onPointerUp = (event) => {
  if (!isDragging.value) return;
  isDragging.value = false;

  if (dragTarget.value === "draw-world") {
    const point = pointFromEvent(event);
    if (point) draw.finish(point);
    dragTarget.value = null;
    return;
  }

  if (dragTarget.value === "measure-world") {
    const point = pointFromEvent(event);
    if (point) measure.finish(point);
    dragTarget.value = null;
    return;
  }

  const imagePoint = imagePointFromWorldEvent(event);
  if (dragTarget.value === "measure-image" && imagePoint) {
    measure.finish(imagePoint);
  } else if (dragTarget.value === "draw-image" && imagePoint) {
    draw.finish(imagePoint);
  }
  dragTarget.value = null;
};

const colorFor = (item) => {
  if (item.type === "ball") return item.color || measure.state.playerConfig.ballColor;
  return item.team === "home" ? measure.state.playerConfig.homeColor : measure.state.playerConfig.guestColor;
};

const chronoLabel = (item) => {
  const duration = Math.max(0, (Number(item.time_to) || 0) - (Number(item.time_from) || 0));
  const elapsed = Math.min(duration, Math.max(0, timeline.state.currentTime - (Number(item.time_from) || 0)));
  return formatTime(elapsed);
};

const formatTime = (time) => {
  const value = Math.max(0, Number.isFinite(time) ? time : 0);
  const minutes = Math.floor(value / 60);
  const seconds = Math.floor(value % 60);
  const millis = Math.floor((value % 1) * 1000);
  return `00:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")},${String(millis).padStart(3, "0")}`;
};
</script>

<style scoped>
.court-2d {
  position: relative;
  min-width: 0;
  min-height: 0;
  display: grid;
  place-items: center;
  background: #151515;
}

.court-2d__svg {
  width: 100%;
  height: 100%;
}

.court-2d__area {
  fill: #1d2422;
  stroke: rgb(232 232 232 / 0.28);
  stroke-width: 0.045;
}

.court-2d__field {
  fill: rgb(69 255 162 / 0.06);
  stroke: #e8e8e8;
  stroke-width: 0.06;
}

.court-2d__grid-line {
  fill: none;
  pointer-events: none;
}

.court-2d__chess-square {
  opacity: 0.16;
  pointer-events: none;
}

.court-2d__vertex circle {
  fill: var(--accent-primary);
  stroke: #111;
  stroke-width: 0.025;
  pointer-events: none;
}

.court-2d__vertex text {
  fill: #fff;
  stroke: #111;
  stroke-width: 0.045;
  paint-order: stroke;
  font-size: 0.62px;
  font-weight: 700;
  pointer-events: none;
}

.court-2d__measure {
  stroke: #ffd84d;
  stroke-width: 0.08;
  cursor: pointer;
  pointer-events: stroke;
}

.court-2d__shape {
  cursor: pointer;
  vector-effect: non-scaling-stroke;
}

.court-2d__player {
  stroke: #111;
  stroke-width: 0.04;
  cursor: pointer;
}

.court-2d__label {
  fill: #fff;
  stroke: #111;
  stroke-width: 0.04;
  paint-order: stroke;
  font-size: 0.45px;
}

.court-2d__chrono {
  position: absolute;
  top: 14px;
  right: 14px;
  padding: 7px 10px;
  background: #000;
  color: #fff;
  font-variant-numeric: tabular-nums;
  font-size: 14px;
}
</style>
