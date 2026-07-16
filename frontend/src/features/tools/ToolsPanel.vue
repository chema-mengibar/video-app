<template>
  <EditorPanel>
    <div class="tools-panel">
      <div class="tools-panel__tabs">
        <button
          class="tools-panel__tab"
          :class="{ 'tools-panel__tab--active': activeTab === 'draw' }"
          type="button"
          @click="activeTab = 'draw'"
        >
          Draw
        </button>
        <button
          class="tools-panel__tab"
          :class="{ 'tools-panel__tab--active': activeTab === 'measure' }"
          type="button"
          @click="activeTab = 'measure'"
        >
          Measure
        </button>
        <button
          class="tools-panel__tab"
          :class="{ 'tools-panel__tab--active': activeTab === 'players' }"
          type="button"
          @click="activeTab = 'players'"
        >
          Players
        </button>
        <button
          class="tools-panel__tab"
          :class="{ 'tools-panel__tab--active': activeTab === 'analyse' }"
          type="button"
          @click="activeTab = 'analyse'"
        >
          Analyse
        </button>
      </div>

      <div v-if="activeTab === 'draw'" class="tools-panel__body">
        <div class="tools-panel__section-title">
          <AppIcon name="draw" />
          <span>Tools</span>
        </div>

        <div class="tools-panel__grid">
          <IconButton
            v-for="tool in tools"
            :key="tool.id"
            :icon="tool.icon"
            :title="tool.label"
            :active="draw.state.selectedTool === tool.id"
            @click="selectDrawTool(tool.id)"
          />
        </div>

        <div class="tools-panel__section-title tools-panel__section-title--spaced">
          <AppIcon :name="activeTool?.icon || 'draw'" />
          <span>{{ activeTool.label }}</span>
        </div>

        <div class="tools-panel__config">
          <div class="tools-panel__row">
            <span class="tools-panel__line"></span>
            <span class="tools-panel__dash"></span>
          </div>
          <div class="tools-panel__row">
            <input v-model="draw.state.config.color" class="tools-panel__color" type="color" title="Color" />
            <input v-model.number="draw.state.config.opacity" class="tools-panel__input" type="number" min="0" max="1" step="0.1" />
          </div>
          <label class="tools-panel__field">
            <span>Width:</span>
            <input v-model.number="draw.state.config.width" class="tools-panel__input" type="number" min="1" max="12" />
          </label>
        </div>
      </div>

      <div v-else-if="activeTab === 'measure'" class="tools-panel__body">
        <div class="tools-panel__section-title">
          <AppIcon name="square" />
          <span>Grid</span>
        </div>

        <div class="tools-panel__config">
          <label class="tools-panel__field tools-panel__field--wide">
            <span>Preset</span>
            <select
              :value="gridPresetId"
              class="tools-panel__select"
              @change="setGridPreset($event.target.value)"
            >
              <option v-for="preset in dimensionPresets" :key="preset.id" :value="preset.id">
                {{ preset.label }}
              </option>
            </select>
          </label>
          <label class="tools-panel__field tools-panel__field--wide">
            <span>AB m</span>
            <input :value="gridWidth" class="tools-panel__input" type="number" min="0.1" step="0.1" :disabled="!canEditDimensions" @change="updateFreeDimension('abMeters', $event.target.value)" />
          </label>
          <label class="tools-panel__field tools-panel__field--wide">
            <span>AC m</span>
            <input :value="gridLength" class="tools-panel__input" type="number" min="0.1" step="0.1" :disabled="!canEditDimensions" @change="updateFreeDimension('acMeters', $event.target.value)" />
          </label>
          <div class="tools-panel__court-thumb" aria-hidden="true">
            <svg class="tools-panel__court-svg" viewBox="0 0 120 86" preserveAspectRatio="xMidYMid meet">
              <rect
                class="tools-panel__court-field"
                :x="courtThumbRect.x"
                :y="courtThumbRect.y"
                :width="courtThumbRect.width"
                :height="courtThumbRect.height"
              />
              <line
                class="tools-panel__court-midline"
                :x1="courtThumbRect.x + courtThumbRect.width / 2"
                :y1="courtThumbRect.y"
                :x2="courtThumbRect.x + courtThumbRect.width / 2"
                :y2="courtThumbRect.y + courtThumbRect.height"
              />
              <line
                class="tools-panel__court-midline"
                :x1="courtThumbRect.x"
                :y1="courtThumbRect.y + courtThumbRect.height / 2"
                :x2="courtThumbRect.x + courtThumbRect.width"
                :y2="courtThumbRect.y + courtThumbRect.height / 2"
              />
              <g v-for="vertex in courtThumbVertices" :key="vertex.label" class="tools-panel__court-vertex">
                <circle :cx="vertex.x" :cy="vertex.y" r="2.5" />
                <text :x="vertex.labelX" :y="vertex.labelY">{{ vertex.label }}</text>
              </g>
            </svg>
          </div>
          <button class="tools-panel__action" type="button" @click="addGrid">Add grid</button>
        </div>

        <div class="tools-panel__section-title tools-panel__section-title--spaced-small">
          <AppIcon name="measure" />
          <span>Tools</span>
        </div>

        <div class="tools-panel__grid">
          <IconButton
            icon="measure"
            title="Linear measure"
            :active="measure.state.selectedTool === 'measure-line'"
            @click="selectMeasureTool('measure-line')"
          />
          <IconButton
            icon="chrono"
            title="Chrono"
            @click="addChrono"
          />
          <IconButton
            icon="pause"
            title="Delay"
            @click="addDelay"
          />
          <IconButton
            icon="triangle"
            title="Goal projection"
            @click="addGoalProjection"
          />
        </div>
      </div>

      <div v-else-if="activeTab === 'players'" class="tools-panel__body">
        <div class="tools-panel__section-title">
          <AppIcon name="player" />
          <span>Players</span>
        </div>

        <div class="tools-panel__team-actions">
          <button
            class="tools-panel__team-button"
            :class="{ 'tools-panel__team-button--active': measure.state.selectedTool === 'player' && measure.state.selectedPlayerTeam === 'guest' }"
            type="button"
            @click="selectPlayerTool('guest')"
          >
            <span class="tools-panel__team-swatch" :style="{ background: measure.state.playerConfig.guestColor }"></span>
            <span>Guest</span>
          </button>
          <button
            class="tools-panel__team-button"
            :class="{ 'tools-panel__team-button--active': measure.state.selectedTool === 'player' && measure.state.selectedPlayerTeam === 'home' }"
            type="button"
            @click="selectPlayerTool('home')"
          >
            <span class="tools-panel__team-swatch" :style="{ background: measure.state.playerConfig.homeColor }"></span>
            <span>Home</span>
          </button>
          <IconButton
            icon="ball"
            title="Ball"
            :active="measure.state.selectedTool === 'ball'"
            @click="selectMeasureTool('ball')"
          />
        </div>

        <div class="tools-panel__section-title tools-panel__section-title--spaced-small">
          <AppIcon name="player" />
          <span>Teams</span>
        </div>

        <div class="tools-panel__config">
          <label class="tools-panel__field tools-panel__field--wide">
            <span>Guest</span>
            <input :value="measure.state.playerConfig.guestColor" class="tools-panel__color" type="color" @input="measure.updatePlayerConfig({ guestColor: $event.target.value })" />
          </label>
          <label class="tools-panel__field tools-panel__field--wide">
            <span>Home</span>
            <input :value="measure.state.playerConfig.homeColor" class="tools-panel__color" type="color" @input="measure.updatePlayerConfig({ homeColor: $event.target.value })" />
          </label>
        </div>

        <div class="tools-panel__section-title tools-panel__section-title--spaced-small">
          <AppIcon name="ball" />
          <span>Ball</span>
        </div>

        <div class="tools-panel__config">
          <label class="tools-panel__field tools-panel__field--wide">
            <span>Color</span>
            <input :value="measure.state.playerConfig.ballColor" class="tools-panel__color" type="color" @input="measure.updatePlayerConfig({ ballColor: $event.target.value })" />
          </label>
        </div>

        <div class="tools-panel__section-title tools-panel__section-title--spaced-small">
          <AppIcon name="measure" />
          <span>Marker size</span>
        </div>

        <div class="tools-panel__config">
          <label class="tools-panel__field tools-panel__field--wide">
            <span>Width px</span>
            <input v-model.number="measure.state.playerConfig.widthPx" class="tools-panel__input" type="number" min="4" max="120" />
          </label>
          <label class="tools-panel__field tools-panel__field--wide">
            <span>Length px</span>
            <input v-model.number="measure.state.playerConfig.lengthPx" class="tools-panel__input" type="number" min="4" max="120" />
          </label>
        </div>
      </div>

      <div v-else-if="activeTab === 'analyse'" class="tools-panel__body">
        <div class="tools-panel__section-title">
          <AppIcon name="triangle" />
          <span>Analyse</span>
        </div>

        <div v-if="activeAnalysisItem" class="tools-panel__config">
          <div class="tools-panel__measure-grid">
            <label>
              <span>V-C</span>
              <input :value="analysisMeasures.vc" type="number" min="0.01" step="0.1" @change="updateAnalysisMeasure('vc', $event.target.value)" />
            </label>
            <label>
              <span>U-V</span>
              <input :value="analysisMeasures.uv" type="number" min="0.01" step="0.1" @change="updateAnalysisMeasure('uv', $event.target.value)" />
            </label>
            <label>
              <span>U-u</span>
              <input :value="analysisMeasures.uHeight" type="number" min="0.01" step="0.1" @change="updateAnalysisMeasure('uHeight', $event.target.value)" />
            </label>
            <label>
              <span>U-C</span>
              <input :value="analysisMeasures.uc" type="number" min="0.01" step="0.1" @change="updateAnalysisMeasure('uc', $event.target.value)" />
            </label>
            <label>
              <span>V-v</span>
              <input :value="analysisMeasures.vHeight" type="number" min="0.01" step="0.1" @change="updateAnalysisMeasure('vHeight', $event.target.value)" />
            </label>
            <label>
              <span>players h</span>
              <input :value="analysisMeasures.playerHeight" type="number" min="0" step="0.1" @change="updateAnalysisMeasure('playerHeight', $event.target.value)" />
            </label>
          </div>

          <svg class="tools-panel__analyse-svg" viewBox="0 0 220 170" preserveAspectRatio="xMidYMid meet">
            <path :d="analysisTrianglePath" class="tools-panel__analyse-triangle" />
            <text
              v-for="label in arealLabels"
              :key="label.text"
              class="tools-panel__analyse-label"
              :x="label.x"
              :y="label.y"
            >
              {{ label.text }}
            </text>
            <g v-for="point in arealObstaclePoints" :key="point.id">
              <circle
                :cx="point.x"
                :cy="point.y"
                :r="point.radius"
                :fill="point.color"
                :class="point.inside ? 'tools-panel__analyse-point--inside' : 'tools-panel__analyse-point--outside'"
              />
            </g>
          </svg>

          <svg class="tools-panel__analyse-svg" viewBox="0 0 220 170" preserveAspectRatio="xMidYMid meet">
            <rect
              class="tools-panel__analyse-front-rect"
              :x="frontRect.x"
              :y="frontRect.y"
              :width="frontRect.width"
              :height="frontRect.height"
            />
            <line class="tools-panel__analyse-ground" :x1="frontRect.x" :y1="frontGroundY" :x2="frontRect.x + frontRect.width" :y2="frontGroundY" />
            <rect class="tools-panel__analyse-c-marker" :x="frontCX - 3" :y="frontGroundY - 3" width="6" height="6" />
            <text
              v-for="label in frontLabels"
              :key="label.text"
              class="tools-panel__analyse-label"
              :x="label.x"
              :y="label.y"
            >
              {{ label.text }}
            </text>
            <g v-for="point in frontObstaclePoints" :key="point.id">
              <rect
                :x="point.x - point.width / 2"
                :y="point.y"
                :width="point.width"
                :height="point.height"
                :fill="point.color"
                class="tools-panel__analyse-front-obstacle"
              />
            </g>
          </svg>
        </div>

        <p v-else class="tools-panel__empty">Select a vertical projection item and click Analyse.</p>
      </div>
    </div>
  </EditorPanel>
</template>

<script setup>
import { computed, inject, ref, watch } from "vue";
import EditorPanel from "@/components/common/EditorPanel.vue";
import IconButton from "@/components/common/IconButton.vue";
import AppIcon from "@/components/common/AppIcon.vue";
import { SERVICES_KEY } from "@/services/ServiceRegistry.js";

const services = inject(SERVICES_KEY);
const draw = services.drawService;
const measure = services.measureService;
const project = services.projectService;
const activeTab = ref("draw");
const selectedGridPresetId = ref("Basketball NBA");
const freeGridDimensions = ref({ abMeters: 15.24, acMeters: 28.65 });

const tools = [
  { id: "free-line", icon: "line", label: "Free line" },
  { id: "straight-line", icon: "straight", label: "Straight line" },
  { id: "polyline", icon: "straight", label: "Polyline" },
  { id: "triangle", icon: "triangle", label: "Triangle" },
  { id: "square", icon: "square", label: "Square" },
  { id: "polygon", icon: "polygon", label: "Polygon" },
  { id: "circle", icon: "circle", label: "Circle" }
];
const dimensionPresets = [
  { id: "Free", label: "Free", width: 10, length: 10 },
  { id: "Tennis Singles", label: "Tennis Singles", width: 8.23, length: 23.77 },
  { id: "Tennis Doubles", label: "Tennis Doubles", width: 10.97, length: 23.77 },
  { id: "Inline Hockey (IIHF)", label: "Inline Hockey (IIHF)", width: 26, length: 44 },
  { id: "Ice Hockey IIHF", label: "Ice Hockey IIHF", width: 30, length: 60 },
  { id: "Ice Hockey NHL", label: "Ice Hockey NHL", width: 26, length: 60.96 },
  { id: "Football (FIFA)", label: "Football (FIFA)", width: 68, length: 105 },
  { id: "Futsal", label: "Futsal", width: 20, length: 40 },
  { id: "Basketball FIBA", label: "Basketball FIBA", width: 15, length: 28 },
  { id: "Basketball NBA", label: "Basketball NBA", width: 15.24, length: 28.65 },
  { id: "Handball", label: "Handball", width: 20, length: 40 },
  { id: "Pool (8/9 Ball)", label: "Pool (8/9 Ball)", width: 1.27, length: 2.54 }
];

const activeTool = computed(() => tools.find((tool) => tool.id === draw.state.selectedTool) || { icon: "draw", label: "No tool selected" });
const gridPresetId = computed(() => measure.gridItem?.dimensionPreset || selectedGridPresetId.value);
const currentGridPreset = computed(() => dimensionPresets.find((preset) => preset.id === gridPresetId.value) || dimensionPresets[0]);
const canEditDimensions = computed(() => gridPresetId.value === "Free");
const gridWidth = computed(() => measure.gridItem?.abMeters || (canEditDimensions.value ? freeGridDimensions.value.abMeters : currentGridPreset.value.width));
const gridLength = computed(() => measure.gridItem?.acMeters || (canEditDimensions.value ? freeGridDimensions.value.acMeters : currentGridPreset.value.length));
const courtThumbRect = computed(() => {
  const width = Math.max(0.1, Number(gridWidth.value) || 0.1);
  const length = Math.max(0.1, Number(gridLength.value) || 0.1);
  const maxWidth = 92;
  const maxHeight = 58;
  const scale = Math.min(maxWidth / width, maxHeight / length);
  const rectWidth = width * scale;
  const rectHeight = length * scale;
  return {
    x: (120 - rectWidth) / 2,
    y: (86 - rectHeight) / 2,
    width: rectWidth,
    height: rectHeight
  };
});
const courtThumbVertices = computed(() => {
  const rect = courtThumbRect.value;
  const offset = 6;
  return [
    { label: "A", x: rect.x, y: rect.y, labelX: rect.x - offset, labelY: rect.y - 4 },
    { label: "B", x: rect.x + rect.width, y: rect.y, labelX: rect.x + rect.width + 4, labelY: rect.y - 4 },
    { label: "C", x: rect.x, y: rect.y + rect.height, labelX: rect.x - offset, labelY: rect.y + rect.height + 10 },
    { label: "D", x: rect.x + rect.width, y: rect.y + rect.height, labelX: rect.x + rect.width + 4, labelY: rect.y + rect.height + 10 }
  ];
});
const activeAnalysisItem = computed(() => {
  return (project.state.data.items || []).find((item) => item.id === measure.state.analysisItemId && item.type === "vertical-projection") || null;
});
const analysisCandidates = computed(() => {
  const selectedProjectionId = activeAnalysisItem.value?.id;
  const currentTime = services.timelineService.state.currentTime;
  return (project.state.data.items || [])
    .filter((item) => {
      if (item.id === selectedProjectionId || !["player", "ball"].includes(item.type) || !item.point) return false;
      const from = Number.isFinite(item.time_from) ? item.time_from : 0;
      const to = Number.isFinite(item.time_to) ? item.time_to : from;
      return currentTime >= from && currentTime <= to;
    });
});
const analysisMeasures = computed(() => ({
  vc: Number(activeAnalysisItem.value?.analysisMeasures?.vc) || 8,
  uc: Number(activeAnalysisItem.value?.analysisMeasures?.uc) || 8,
  uv: Number(activeAnalysisItem.value?.analysisMeasures?.uv) || 4,
  uHeight: Number(activeAnalysisItem.value?.analysisMeasures?.uHeight) || 2,
  vHeight: Number(activeAnalysisItem.value?.analysisMeasures?.vHeight) || 2,
  playerHeight: Number(activeAnalysisItem.value?.analysisMeasures?.playerHeight) || 1.8
}));
const analysisBase = computed(() => {
  const [a, b, projectionB, projectionA, c] = activeAnalysisItem.value?.points || [];
  if (!a || !b || !projectionB || !projectionA || !c) return null;
  return {
    sourceA: projectionA,
    sourceB: projectionB,
    sourceC: c,
    sourceU: projectionA,
    sourceV: projectionB,
    sourceu: a,
    sourcev: b
  };
});
const arealView = computed(() => {
  const measures = analysisMeasures.value;
  const uv = Math.max(0.01, Math.min(measures.uv, measures.uc + measures.vc - 0.01));
  const cX = Math.max(0, Math.min(uv, (measures.uc ** 2 - measures.vc ** 2 + uv ** 2) / (2 * uv)));
  const height = Math.max(0.01, Math.sqrt(Math.max(measures.uc ** 2 - cX ** 2, 0.01)));
  const maxWidth = 168;
  const maxHeight = 118;
  const scale = Math.min(maxWidth / uv, maxHeight / height);
  const width = uv * scale;
  const viewHeight = height * scale;
  const left = (220 - width) / 2;
  const baseY = 136;
  return {
    scale,
    U: { x: left, y: baseY },
    V: { x: left + width, y: baseY },
    C: { x: left + cX * scale, y: baseY - viewHeight },
    width,
    height,
    cX
  };
});
const analysisTrianglePath = computed(() => {
  const view = arealView.value;
  if (!view) return "";
  return `M ${view.U.x} ${view.U.y} L ${view.V.x} ${view.V.y} L ${view.C.x} ${view.C.y} Z`;
});
const arealLabels = computed(() => {
  const view = arealView.value;
  return [
    { text: "U", x: view.U.x - 11, y: view.U.y + 18 },
    { text: "V", x: view.V.x + 8, y: view.V.y + 18 },
    { text: "C", x: view.C.x + 8, y: view.C.y - 8 }
  ];
});
const projectedObstacles = computed(() => {
  const base = analysisBase.value;
  if (!base) return [];
  return analysisCandidates.value
    .map((item) => {
      const mapped = mapPointToAnalysisWeights(item.point, base);
      return mapped?.inside ? {
        id: item.id,
        label: item.label || item.type,
        color: obstacleColor(item),
        heightMeters: Number(item.heightMeters) || analysisMeasures.value.playerHeight,
        ...mapped
      } : null;
    })
    .filter(Boolean);
});
const arealObstaclePoints = computed(() => {
  const view = arealView.value;
  return projectedObstacles.value.map((point) => ({
    ...point,
    x: point.u * view.U.x + point.v * view.V.x + point.w * view.C.x,
    y: point.u * view.U.y + point.v * view.V.y + point.w * view.C.y,
    radius: 5
  }));
});
const frontRect = computed(() => {
  const measures = analysisMeasures.value;
  const maxHeightMeters = Math.max(measures.uHeight, measures.vHeight, measures.playerHeight, 0.1);
  const scaleY = 100 / maxHeightMeters;
  const width = Math.max(42, Math.min(156, measures.uv * 24));
  return {
    x: (220 - width) / 2,
    y: 34,
    width,
    height: Math.max(28, Math.max(measures.uHeight, measures.vHeight) * scaleY),
    scaleY
  };
});
const frontGroundY = computed(() => frontRect.value.y + frontRect.value.height + 20);
const frontCRatio = computed(() => {
  const view = arealView.value;
  if (!view?.width) return 0.5;
  return Math.max(0, Math.min(1, (view.C.x - view.U.x) / view.width));
});
const frontCX = computed(() => frontRect.value.x + frontRect.value.width * frontCRatio.value);
const frontLabels = computed(() => {
  const rect = frontRect.value;
  const ground = frontGroundY.value;
  const cX = frontCX.value;
  return [
    { text: "u", x: rect.x - 11, y: rect.y - 8 },
    { text: "v", x: rect.x + rect.width + 7, y: rect.y - 8 },
    { text: "U", x: rect.x - 11, y: rect.y + rect.height + 16 },
    { text: "V", x: rect.x + rect.width + 7, y: rect.y + rect.height + 16 },
    { text: "C", x: cX + 8, y: ground + 14 }
  ];
});
const frontObstaclePoints = computed(() => {
  const rect = frontRect.value;
  const cRatio = frontCRatio.value;
  return projectedObstacles.value.map((point) => {
    const ratio = Math.max(0, Math.min(1, point.v + point.w * cRatio));
    const height = Math.max(4, point.heightMeters * rect.scaleY);
    return {
      ...point,
      x: rect.x + rect.width * ratio,
      y: rect.y + rect.height - height,
      width: 5,
      height
    };
  });
});

const selectDrawTool = (tool) => {
  measure.clearTool();
  draw.selectTool(tool);
};

const selectMeasureTool = (tool) => {
  draw.state.selectedTool = null;
  measure.selectTool(tool);
};

const selectPlayerTool = (team) => {
  draw.state.selectedTool = null;
  measure.selectPlayerTool(team);
};

const addChrono = () => {
  draw.state.selectedTool = null;
  measure.clearTool();
  measure.addChrono();
};

const addDelay = () => {
  draw.state.selectedTool = null;
  measure.clearTool();
  measure.addDelay();
};

const addGoalProjection = () => {
  draw.state.selectedTool = null;
  measure.clearTool();
  measure.addGoalProjection();
};

const updateAnalysisMeasure = (key, value) => {
  if (!activeAnalysisItem.value) return;
  const nextValue = Math.max(0, Number(value) || 0);
  activeAnalysisItem.value.analysisMeasures = {
    ...(activeAnalysisItem.value.analysisMeasures || {}),
    [key]: key === "playerHeight" ? nextValue : Math.max(0.01, nextValue)
  };
  project.save();
};

const mapPointToAnalysisWeights = (point, base) => {
  const denominator = (base.sourceA.y - base.sourceC.y) * (base.sourceB.x - base.sourceC.x) + (base.sourceC.x - base.sourceA.x) * (base.sourceB.y - base.sourceC.y);
  if (Math.abs(denominator) < 0.000001) return null;
  const u = ((point.y - base.sourceC.y) * (base.sourceB.x - base.sourceC.x) + (base.sourceC.x - point.x) * (base.sourceB.y - base.sourceC.y)) / denominator;
  const v = ((base.sourceA.y - base.sourceC.y) * (point.x - base.sourceC.x) + (point.y - base.sourceC.y) * (base.sourceC.x - base.sourceA.x)) / denominator;
  const w = 1 - u - v;
  return {
    u,
    v,
    w,
    inside: u >= 0 && v >= 0 && w >= 0
  };
};

const obstacleColor = (item) => {
  if (item.type === "ball") return item.color || measure.state.playerConfig.ballColor;
  if (item.team === "home") return item.color || measure.state.playerConfig.homeColor;
  return item.color || measure.state.playerConfig.guestColor;
};

watch(
  () => measure.state.analysisItemId,
  (id) => {
    if (id) {
      activeTab.value = "analyse";
    }
  }
);

const addGrid = () => {
  draw.state.selectedTool = null;
  measure.clearTool();
  const selectedPresetId = selectedGridPresetId.value;
  const preset = dimensionPresets.find((candidate) => candidate.id === selectedPresetId) || dimensionPresets[0];
  const isFreePreset = selectedPresetId === "Free";
  const dimensions = {
    width: isFreePreset ? freeGridDimensions.value.abMeters : preset.width,
    length: isFreePreset ? freeGridDimensions.value.acMeters : preset.length
  };
  const item = measure.addGrid({
    ...preset,
    width: dimensions.width,
    length: dimensions.length
  });
  if (item && preset) {
    measure.applyDimensionPreset({
      ...preset,
      width: dimensions.width,
      length: dimensions.length
    });
  }
};

const setGridPreset = (id) => {
  selectedGridPresetId.value = id;
  const preset = dimensionPresets.find((candidate) => candidate.id === id);
  if (!preset) return;
  if (measure.gridItem) {
    measure.applyDimensionPreset(preset);
  }
};

const updateFreeDimension = (key, value) => {
  if (!canEditDimensions.value) return;
  const nextValue = Number(value);
  freeGridDimensions.value[key] = nextValue;
  if (measure.gridItem) {
    measure.updateFieldDimensions({ [key]: nextValue });
  }
};
</script>

<style scoped>
.tools-panel {
  height: 100%;
  min-height: 0;
  display: grid;
  grid-template-rows: 30px 1fr;
}

.tools-panel__tabs {
  display: flex;
  align-items: stretch;
  border-bottom: 1px solid var(--surface-outer);
  background: var(--surface-header);
}

.tools-panel__tab {
  border: 0;
  border-right: 1px solid var(--surface-outer);
  padding: 0 14px;
  background: transparent;
  color: var(--text-muted);
  font-size: var(--fs-ui-normal);
  cursor: pointer;
}

.tools-panel__tab--active {
  background: var(--surface-panel);
  color: var(--text-color);
}

.tools-panel__body {
  min-height: 0;
  overflow: auto;
  padding: 28px 22px;
}

.tools-panel__section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--surface-border);
  font-size: var(--fs-ui-normal);
}

.tools-panel__section-title--spaced {
  margin-top: 110px;
}

.tools-panel__section-title--spaced-small {
  margin-top: 28px;
}

.tools-panel__grid,
.tools-panel__row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 18px;
}

.tools-panel__team-actions {
  display: grid;
  grid-template-columns: 1fr 1fr 34px;
  align-items: center;
  gap: 6px;
  margin-top: 18px;
}

.tools-panel__team-button {
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  border: 1px solid var(--surface-border);
  background: var(--surface-button);
  color: var(--text-color);
  cursor: pointer;
}

.tools-panel__team-button--active {
  border-color: var(--accent-primary);
  color: var(--surface-black);
  background: var(--accent-primary);
}

.tools-panel__team-swatch {
  width: 10px;
  height: 10px;
  border: 1px solid rgb(0 0 0 / 0.45);
}

.tools-panel__config {
  display: grid;
  gap: 12px;
  margin-top: 24px;
}

.tools-panel__measure-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 16px;
}

.tools-panel__measure-grid label {
  display: grid;
  grid-template-columns: 58px minmax(0, 1fr);
  align-items: center;
  gap: 8px;
}

.tools-panel__measure-grid input {
  min-width: 0;
  height: 28px;
  border: 0;
  padding: 0 8px;
  background: var(--surface-button);
  color: var(--text-color);
}

.tools-panel__line,
.tools-panel__dash {
  width: 42px;
  height: 18px;
  background: var(--surface-button);
  border-top: 2px solid var(--text-color);
}

.tools-panel__dash {
  border-top-style: dotted;
}

.tools-panel__color {
  width: 22px;
  height: 22px;
  border: 0;
  padding: 0;
  background: transparent;
}

.tools-panel__field {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tools-panel__field--wide {
  justify-content: space-between;
}

.tools-panel__input,
.tools-panel__select {
  width: 82px;
  height: 28px;
  border: 0;
  padding: 0 8px;
  background: var(--surface-button);
  color: var(--text-color);
}

.tools-panel__select {
  width: 180px;
}

.tools-panel__input--wide {
  width: 180px;
}

.tools-panel__field--stacked {
  display: grid;
  align-items: start;
}

.tools-panel__input:disabled {
  opacity: 0.55;
}

.tools-panel__action {
  height: 30px;
  border: 1px solid var(--surface-border);
  background: var(--surface-button);
  color: var(--text-color);
  cursor: pointer;
}

.tools-panel__action:hover {
  border-color: var(--accent-primary);
}

.tools-panel__court-thumb {
  height: 102px;
  display: grid;
  place-items: center;
  border: 1px solid var(--surface-border);
  background:
    linear-gradient(90deg, rgb(255 255 255 / 0.04) 1px, transparent 1px),
    linear-gradient(rgb(255 255 255 / 0.04) 1px, transparent 1px),
    #1a2422;
  background-size: 12px 12px;
}

.tools-panel__court-svg {
  width: 100%;
  height: 100%;
}

.tools-panel__court-field {
  fill: rgb(69 255 162 / 0.12);
  stroke: var(--text-color);
  stroke-width: 1.4;
}

.tools-panel__court-midline {
  stroke: rgb(255 255 255 / 0.42);
  stroke-width: 0.8;
  stroke-dasharray: 3 3;
}

.tools-panel__court-vertex circle {
  fill: var(--accent-primary);
  stroke: #0d0d0d;
  stroke-width: 1;
}

.tools-panel__court-vertex text {
  fill: var(--text-color);
  stroke: #0d0d0d;
  stroke-width: 2;
  paint-order: stroke;
  font-size: 11px;
  font-weight: 700;
}

.tools-panel__points {
  display: grid;
  gap: 8px;
  margin-top: 18px;
}

.tools-panel__empty {
  margin-top: 18px;
  color: var(--text-muted);
}

.tools-panel__analyse-svg {
  width: 100%;
  height: 210px;
  border: 1px solid var(--surface-border);
  background: #050505;
}

.tools-panel__analyse-triangle {
  fill: rgb(69 255 162 / 0.13);
  stroke: var(--accent-primary);
  stroke-width: 2;
}

.tools-panel__analyse-goal {
  fill: rgb(75 131 216 / 0.18);
  stroke: #4b83d8;
  stroke-width: 2;
}

.tools-panel__analyse-front-rect {
  fill: #838383;
  stroke: #d0d0d0;
  stroke-width: 1;
}

.tools-panel__analyse-ground {
  stroke: #d0d0d0;
  stroke-width: 1;
}

.tools-panel__analyse-c-marker {
  fill: #4b83d8;
  stroke: #d0d0d0;
  stroke-width: 1;
}

.tools-panel__analyse-front-obstacle {
  stroke: #ffff00;
  stroke-width: 1;
}

.tools-panel__analyse-label,
.tools-panel__analyse-player-label {
  fill: var(--text-color);
  stroke: var(--surface-black);
  stroke-width: 3;
  paint-order: stroke;
  font-size: 11px;
  font-weight: 700;
}

.tools-panel__analyse-player-label {
  font-size: 9px;
  font-weight: 600;
}

.tools-panel__analyse-point--inside {
  stroke: #fff;
  stroke-width: 1.5;
}

.tools-panel__analyse-point--outside {
  stroke: var(--text-muted);
  stroke-width: 1.5;
}

.tools-panel__point {
  display: grid;
  grid-template-columns: 20px 1fr 1fr 36px;
  align-items: center;
  gap: 6px;
}

.tools-panel__point input {
  min-width: 0;
  height: 28px;
  border: 0;
  padding: 0 8px;
  background: var(--surface-button);
  color: var(--text-color);
}
</style>
