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
    </div>
  </EditorPanel>
</template>

<script setup>
import { computed, inject, ref } from "vue";
import EditorPanel from "@/components/common/EditorPanel.vue";
import IconButton from "@/components/common/IconButton.vue";
import AppIcon from "@/components/common/AppIcon.vue";
import { SERVICES_KEY } from "@/services/ServiceRegistry.js";

const services = inject(SERVICES_KEY);
const draw = services.drawService;
const measure = services.measureService;
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
