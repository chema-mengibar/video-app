<template>
  <EditorPanel title="">
    <div class="inspector">
      <div class="inspector__tabs">
        <button
          v-for="tab in tabs"
          :key="tab"
          class="inspector__tab"
          :class="{ 'inspector__tab--active': activeTab === tab }"
          type="button"
          @click="activeTab = tab"
        >
          {{ tab }}
        </button>
      </div>

      <div v-if="activeTab === 'Events'" class="inspector__body inspector__body--events">
        <header class="inspector__events-header">
          <span>Events</span>
          <div class="inspector__events-actions">
            <button class="inspector__action" type="button" @click="events.add()">Add event</button>
            <button class="inspector__action" type="button" @click="events.clear()">Delete all</button>
          </div>
        </header>

        <div v-for="(event, index) in project.state.data.events" :key="event.id" class="inspector__row inspector__row--event">
          <span class="inspector__index" :class="{ 'inspector__index--active': isActiveEvent(event) }">{{ index + 1 }}</span>
          <input class="inspector__text" :value="event.label" @change="events.update(event.id, { label: $event.target.value })" />
          <span>{{ formatTime(event.time_from) }}</span>
          <IconButton icon="jump" title="Jump to event" @click="events.jump(event)" />
          <IconButton icon="trash" title="Delete event" @click="events.remove(event.id)" />
        </div>
      </div>

      <div v-else-if="activeTab === 'Items'" class="inspector__body">
        <header class="inspector__items-header">
          <button class="inspector__collapse" type="button" @click="collapseAllItems">+</button>
          <span>Items</span>
        </header>
        <div
          v-for="item in project.state.data.items"
          :key="item.id"
          class="inspector__item"
          :class="{ 'inspector__item--active': isSelectedItem(item) }"
          @click="selectItem(item)"
        >
          <div class="inspector__row inspector__row--item">
            <button class="inspector__collapse" type="button" @click.stop="toggleCollapsed(item.id)">
              {{ isCollapsed(item.id) ? "+" : "-" }}
            </button>
            <input
              class="inspector__color"
              :value="item.color"
              type="color"
              title="Item color"
              @click.stop
              @input="updateItem(item, { color: $event.target.value })"
            />
            <input class="inspector__text" :value="item.label" @change="updateItem(item, { label: $event.target.value })" />
            <span>{{ formatTime(item.time_from) }} - {{ formatTime(item.time_to) }}</span>
            <IconButton
              :icon="item.visible === false ? 'eye-off' : 'eye'"
              :title="item.visible === false ? 'Show item' : 'Hide item'"
              @click.stop="updateItem(item, { visible: item.visible === false })"
            />
            <IconButton
              v-if="!['measure-grid', 'measure-line', 'chrono', 'player', 'ball', 'delay'].includes(item.type)"
              icon="move"
              title="Move item"
              :active="isActiveItemMove(item)"
              @click.stop="startItemMove(item)"
            />
            <IconButton
              v-if="item.type === 'measure-line'"
              icon="move"
              title="Move measure"
              :active="isActiveMeasureItemMove(item)"
              @click.stop="startMeasureItemMove(item)"
            />
            <IconButton
              v-if="['player', 'ball'].includes(item.type)"
              icon="move"
              :title="item.type === 'ball' ? 'Move ball' : 'Move player'"
              :active="isActiveMeasureItemMove(item)"
              @click.stop="startPlayerMove(item)"
            />
            <IconButton icon="trash" title="Delete item" @click.stop="draw.deleteItem(item.id)" />
          </div>
          <template v-if="!isCollapsed(item.id)">
          <div v-if="item.type === 'circle'" class="inspector__points">
            <label class="inspector__point">
              <span>Center</span>
              <input :value="round(circleFor(item).center.x)" type="number" step="0.1" @change="updateCircleCenter(item, 'x', $event.target.value)" />
              <input :value="round(circleFor(item).center.y)" type="number" step="0.1" @change="updateCircleCenter(item, 'y', $event.target.value)" />
              <IconButton icon="move" title="Move circle" :active="isActiveMove(item.id, 'move')" @click.stop="startItemMove(item)" />
            </label>
            <label class="inspector__point">
              <span>Radius</span>
              <input :value="round(circleFor(item).radius)" type="number" min="1" step="0.1" @change="updateCircleRadius(item, $event.target.value)" />
              <span></span>
              <IconButton icon="cursor" title="Drag radius" :active="isActiveMove(item.id, 'radius')" @click.stop="draw.startResizeCircle(item.id)" />
            </label>
            <label class="inspector__point inspector__point--checkbox">
              <span>Oval</span>
              <input :checked="!!item.oval" type="checkbox" @change="toggleCircleOval(item, $event.target.checked)" />
            </label>
            <label v-if="item.oval" class="inspector__point">
              <span>Height</span>
              <input :value="round(circleFor(item).height)" type="number" min="1" step="0.1" @change="updateCircleHeight(item, $event.target.value)" />
              <span></span>
              <IconButton icon="cursor" title="Drag height" :active="isActiveMove(item.id, 'height')" @click.stop="draw.startResizeCircleHeight(item.id)" />
            </label>
            <label v-if="item.oval" class="inspector__point inspector__point--range">
              <span>Rotation</span>
              <input :value="circleFor(item).rotation" type="range" min="0" max="180" step="1" @input="updateItem(item, { rotation: Number($event.target.value) })" />
              <input :value="round(circleFor(item).rotation)" type="number" min="0" max="180" step="1" @change="updateItem(item, { rotation: Number($event.target.value) })" />
            </label>
          </div>
          <div v-else-if="['player', 'ball'].includes(item.type) && item.point" class="inspector__points">
            <label class="inspector__point">
              <span>Point</span>
              <input :value="round(item.point.x)" type="number" step="0.1" @change="measure.updatePlayerPoint(item.id, { x: Number($event.target.value) })" />
              <input :value="round(item.point.y)" type="number" step="0.1" @change="measure.updatePlayerPoint(item.id, { y: Number($event.target.value) })" />
            </label>
          </div>
          <div v-else-if="item.type === 'delay'" class="inspector__points">
            <label class="inspector__point">
              <span>Start</span>
              <input :value="round(item.time_from)" type="number" min="0" step="0.1" @change="updateDelayStart(item, $event.target.value)" />
              <span></span>
              <IconButton icon="jump" title="Jump to delay start" @click.stop="timeline.setCurrentTime(Number(item.time_from) || 0)" />
            </label>
            <label class="inspector__point">
              <span>Duration</span>
              <input :value="round(item.duration)" type="number" min="0.1" step="0.1" @change="updateDelayDuration(item, $event.target.value)" />
            </label>
          </div>
          <div v-else-if="item.points?.length" class="inspector__points">
            <label v-for="(point, index) in item.points" :key="index" class="inspector__point">
              <span>{{ pointLabel(item, index) }}</span>
              <input :value="round(point.x)" type="number" step="0.1" @change="updateItemPoint(item, index, { x: Number($event.target.value) })" />
              <input :value="round(point.y)" type="number" step="0.1" @change="updateItemPoint(item, index, { y: Number($event.target.value) })" />
              <IconButton icon="cursor" title="Drag point" :active="isActivePointMove(item, index)" @click.stop="startPointMove(item, index)" />
              <IconButton v-if="item.type === 'polyline'" icon="trash" title="Delete point" @click.stop="draw.deletePoint(item.id, index)" />
            </label>
          </div>
          <div v-if="item.type === 'measure-grid'" class="inspector__item-config">
            <label class="inspector__checkbox">
              <span>Chess grid</span>
              <input :checked="!!item.chessboard" type="checkbox" @change="updateItem(item, { chessboard: $event.target.checked })" />
            </label>
            <label>
              <span>Left/right m</span>
              <input :value="item.paddingX || 0" type="number" min="0" step="0.1" @change="updateGridPadding(item, 'paddingX', $event.target.value)" />
            </label>
            <label>
              <span>Top/bottom m</span>
              <input :value="item.paddingY || 0" type="number" min="0" step="0.1" @change="updateGridPadding(item, 'paddingY', $event.target.value)" />
            </label>
          </div>
          <div v-if="isSelectedItem(item)" class="inspector__item-config">
            <label v-if="item.type === 'polyline'" class="inspector__checkbox">
              <span>Close polyline</span>
              <input :checked="!!item.closed" type="checkbox" @change="updateItem(item, { closed: $event.target.checked })" />
            </label>
            <label v-if="item.type === 'square'" class="inspector__checkbox">
              <span>As circle</span>
              <input :checked="!!item.asCircle" type="checkbox" @change="updateItem(item, { asCircle: $event.target.checked })" />
            </label>
            <label v-if="item.type === 'player'">
              <span>Team</span>
              <select :value="item.team || 'guest'" @change="measure.updatePlayerTeam(item.id, $event.target.value)">
                <option value="guest">Guest</option>
                <option value="home">Home</option>
              </select>
            </label>
            <label v-if="['player', 'ball'].includes(item.type)">
              <span>Plus width</span>
              <input :value="item.width" type="number" min="4" max="120" @change="updateItem(item, { width: Number($event.target.value) })" />
            </label>
            <label v-if="['player', 'ball'].includes(item.type)">
              <span>Plus length</span>
              <input :value="item.length" type="number" min="4" max="120" @change="updateItem(item, { length: Number($event.target.value) })" />
            </label>
            <label v-if="hasFill(item)">
              <span>Fill mode</span>
              <select :value="item.fillMode || 'normal'" @change="updateItem(item, { fillMode: $event.target.value })">
                <option v-for="mode in fillModes" :key="mode" :value="mode">{{ mode }}</option>
              </select>
            </label>
            <label v-if="hasFill(item)">
              <span>Fill opacity</span>
              <input :value="fillOpacityValue(item)" type="number" min="0" max="1" step="0.05" @change="updateItem(item, { fillOpacity: Number($event.target.value) })" />
            </label>
            <label v-if="!['player', 'ball'].includes(item.type)">
              <span>Width</span>
              <input :value="item.width" type="number" min="1" max="12" @change="updateItem(item, { width: Number($event.target.value) })" />
            </label>
            <label>
              <span>Opacity</span>
              <input :value="item.opacity" type="number" min="0" max="1" step="0.1" @change="updateItem(item, { opacity: Number($event.target.value) })" />
            </label>
          </div>
          </template>
        </div>
      </div>

      <div v-else class="inspector__body inspector__form">
        <label class="inspector__time-row">
          <span>From</span>
          <input v-model.number="project.state.data.cut.time_from" type="number" step="0.1" />
          <IconButton icon="jump" title="Jump to from time" @click="cut.jumpToFrom()" />
          <button type="button" @click="cut.setFromNow()">Now</button>
        </label>
        <label class="inspector__time-row">
          <span>To</span>
          <input v-model.number="project.state.data.cut.time_to" type="number" step="0.1" />
          <IconButton icon="jump" title="Jump to to time" @click="cut.jumpToTo()" />
          <button type="button" @click="cut.setToNow()">Now</button>
        </label>
        <label class="inspector__checkbox-row">
          <span>1:1 velocity</span>
          <input v-model="cut.state.oneToOneVelocity" type="checkbox" />
        </label>
        <label class="inspector__checkbox-row">
          <span>Add draws</span>
          <input v-model="cut.state.addDraws" type="checkbox" />
        </label>
        <label>
          <span>Quality</span>
          <input v-model.number="cut.state.quality" type="range" min="50" max="100" step="5" />
          <span>{{ cut.state.quality }}%</span>
        </label>
        <button class="inspector__action" type="button" :disabled="cut.state.status === 'processing'" @click="cut.export()">
          {{ cut.state.status === 'processing' ? 'Saving...' : 'Save cut' }}
        </button>
        <button
          v-if="cut.state.status === 'processing'"
          class="inspector__action inspector__action--danger"
          type="button"
          @click="cut.cancelExport()"
        >
          Cancel
        </button>
        <div v-if="cut.state.status === 'processing'" class="inspector__progress">
          <span class="inspector__spinner"></span>
          <progress :value="cut.state.progress" max="100"></progress>
          <span>{{ cut.state.progress }}%</span>
        </div>
        <p v-if="cut.state.status === 'processing' && cut.state.estimatedSeconds !== null" class="inspector__status">
          Estimated remaining: {{ cut.state.estimatedSeconds }}s
        </p>
        <p v-if="cut.state.message" class="inspector__status" :class="`inspector__status--${cut.state.status}`">
          {{ cut.state.message }}
        </p>
        <button
          v-if="cut.state.path && cut.state.status !== 'processing'"
          class="inspector__action"
          type="button"
          @click="cut.openOutputFolder()"
        >
          Open in Explorer
        </button>
      </div>
    </div>
  </EditorPanel>
</template>

<script setup>
import { inject, reactive, ref, watch } from "vue";
import EditorPanel from "@/components/common/EditorPanel.vue";
import IconButton from "@/components/common/IconButton.vue";
import { SERVICES_KEY } from "@/services/ServiceRegistry.js";

const services = inject(SERVICES_KEY);
const project = services.projectService;
const events = services.eventsService;
const draw = services.drawService;
const measure = services.measureService;
const cut = services.cutService;
const timeline = services.timelineService;
const stage = services.stageService;
const tabs = ["Events", "Items", "Cut"];
const activeTab = ref("Events");
const collapsedItems = reactive({});
const fillModes = ["normal", "multiply", "screen", "overlay", "darken", "lighten", "color-dodge", "color-burn", "soft-light", "hard-light"];

const formatTime = (time) => {
  const value = Math.max(0, Number.isFinite(time) ? time : 0);
  const minutes = Math.floor(value / 60);
  const seconds = Math.floor(value % 60);
  const millis = Math.floor((value % 1) * 1000);
  return `00:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")},${String(millis).padStart(3, "0")}`;
};

const round = (value) => Math.round((Number(value) || 0) * 10) / 10;
const gridPointLabels = ["A", "B", "C", "D"];

const pointLabel = (item, index) => {
  if (item.type === "measure-grid") return gridPointLabels[index] || `Point ${index + 1}`;
  return `Point ${index + 1}`;
};

const isActiveEvent = (event) => {
  const eventTime = Number(event?.time_from);
  if (!Number.isFinite(eventTime)) return false;
  return Math.abs(timeline.state.currentTime - eventTime) <= 0.15;
};

const isCollapsed = (id) => !!collapsedItems[id];

const toggleCollapsed = (id) => {
  collapsedItems[id] = !collapsedItems[id];
};

const collapseAllItems = () => {
  for (const item of project.state.data.items || []) {
    collapsedItems[item.id] = true;
  }
};

const isActiveMove = (itemId, mode, pointIndex = null) => {
  return draw.isActiveMove(itemId, mode, pointIndex);
};

const isActiveItemMove = (item) => {
  return stage.activePanel === "court" ? draw.isActiveWorldMove(item.id) : isActiveMove(item.id, "move");
};

const isActiveMeasureItemMove = (item) => {
  if (stage.activePanel === "court") return measure.isActiveWorldMove(item.id);
  return measure.isActiveImageMove(item.id) || measure.isActivePlayer(item.id);
};

const isActivePointMove = (item, index) => {
  if (item.type === "measure-grid") return measure.isActiveFieldPoint(index);
  if (item.type === "measure-line") return measure.isActiveMeasurePoint(item.id, index);
  return draw.isActiveMove(item.id, "point", index);
};

const startPointMove = (item, index) => {
  if (measure.state.editMode) {
    measure.finishMove();
  }
  if (item.type === "measure-grid") {
    if (draw.state.mode === "move") {
      draw.finishMoveMode();
    }
    measure.startMoveFieldPoint(index);
    return;
  }
  if (item.type === "measure-line") {
    if (draw.state.mode === "move") {
      draw.finishMoveMode();
    }
    measure.startMoveMeasurePoint(item.id, index);
    return;
  }
  draw.startMovePoint(item.id, index);
};

const startItemMove = (item) => {
  if (stage.activePanel === "court" && measure.gridItem) {
    if (measure.state.editMode) {
      measure.finishMove();
    }
    draw.startWorldMoveSelected(item.id, measure);
    return;
  }

  if (isActiveMove(item.id, "move")) {
    draw.startMoveSelected(item.id);
    return;
  }
  if (measure.state.editMode) {
    measure.finishMove();
  }
  draw.startMoveSelected(item.id);
};

const startMeasureItemMove = (item) => {
  if (draw.state.mode === "move") {
    draw.finishMoveMode();
  }

  if (stage.activePanel === "court" && measure.gridItem) {
    measure.startWorldMoveSelected(item.id);
    return;
  }

  measure.startImageMoveSelected(item.id);
};

const startPlayerMove = (item) => {
  if (stage.activePanel === "court" && measure.gridItem) {
    if (draw.state.mode === "move") {
      draw.finishMoveMode();
    }
    measure.startWorldMoveSelected(item.id);
    return;
  }

  if (draw.state.mode === "move") {
    draw.finishMoveMode();
  }
  measure.startImageMoveSelected(item.id);
};

const updateItemPoint = (item, index, patch) => {
  if (item.type === "measure-grid") {
    measure.updateFieldPoint(index, patch, item.id);
    return;
  }
  if (item.type === "measure-line") {
    measure.updateMeasurePoint(item.id, index, patch);
    return;
  }
  draw.updateSelectedPoint(index, patch, item.id);
};

const isMeasureItem = (item) => ["measure-line", "measure-grid", "chrono", "player", "ball", "delay"].includes(item.type);

const isSelectedItem = (item) => {
  return isMeasureItem(item) ? item.id === measure.state.selectedItemId : item.id === draw.state.selectedItemId;
};

const selectItem = (item) => {
  if (isMeasureItem(item)) {
    measure.state.selectedItemId = item.id;
    draw.selectItem(null);
    return;
  }
  draw.selectItem(item.id);
  measure.state.selectedItemId = null;
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
  if (!start || !end) {
    return { center: { x: 0, y: 0 }, radius: 1 };
  }

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

const updateCircleCenter = (item, axis, value) => {
  draw.selectItem(item.id);
  const circle = circleFor(item);
  draw.updateSelected({
    center: {
      ...circle.center,
      [axis]: Number(value)
    },
    radius: circle.radius
  });
};

const updateCircleRadius = (item, value) => {
  draw.selectItem(item.id);
  const circle = circleFor(item);
  draw.updateSelected({
    center: circle.center,
    radius: Math.max(1, Number(value) || circle.radius)
  });
};

const updateCircleHeight = (item, value) => {
  draw.selectItem(item.id);
  const circle = circleFor(item);
  draw.updateSelected({
    center: circle.center,
    height: Math.max(1, Number(value) || circle.height)
  });
};

const toggleCircleOval = (item, oval) => {
  const circle = circleFor(item);
  updateItem(item, {
    oval,
    height: Number.isFinite(item.height) ? item.height : circle.radius,
    rotation: Number.isFinite(item.rotation) ? item.rotation : 0
  });
};

const updateItem = (item, patch) => {
  selectItem(item);
  Object.assign(item, patch);
  project.save();
};

const updateGridPadding = (item, key, value) => {
  updateItem(item, {
    [key]: Math.max(0, Number(value) || 0)
  });
};

const updateDelayStart = (item, value) => {
  const start = Math.max(0, Number(value) || 0);
  const duration = Math.max(0.1, Number(item.duration) || 0.1);
  updateItem(item, {
    time_from: start,
    time_to: start + duration
  });
};

const updateDelayDuration = (item, value) => {
  const duration = Math.max(0.1, Number(value) || 0.1);
  const start = Math.max(0, Number(item.time_from) || 0);
  updateItem(item, {
    duration,
    time_to: start + duration
  });
};

const hasFill = (item) => {
  if (["triangle", "square", "polygon", "circle"].includes(item.type)) return true;
  return item.type === "polyline" && item.closed;
};

const fillOpacityValue = (item) => {
  return Number.isFinite(item.fillOpacity) ? item.fillOpacity : 0.4;
};

watch(
  () => draw.state.focusItemId,
  (id) => {
    if (!id) return;
    activeTab.value = "Items";
    collapsedItems[id] = false;
    draw.consumeFocusItem();
  }
);
</script>

<style scoped>
.inspector {
  height: 100%;
  display: grid;
  grid-template-rows: 30px 1fr;
}

.inspector__tabs {
  display: flex;
  background: var(--surface-header);
}

.inspector__tab {
  min-width: 86px;
  border: 0;
  border-right: 1px solid var(--surface-border);
  background: transparent;
  color: var(--text-muted);
  font-size: var(--fs-ui-normal);
  cursor: pointer;
}

.inspector__tab--active {
  background: var(--surface-control);
  color: var(--text-color);
}

.inspector__body {
  overflow: auto;
  padding: 14px;
}

.inspector__body--events {
  display: block;
}

.inspector__events-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 36px;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--surface-border);
}

.inspector__items-header {
  min-height: 36px;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  padding: 0 6px 8px;
  border-bottom: 1px solid var(--surface-border);
}

.inspector__events-actions {
  display: flex;
  gap: 8px;
}

.inspector__row {
  height: 36px;
  display: grid;
  grid-template-columns: 1fr auto 36px;
  align-items: center;
  gap: 10px;
  padding: 0 6px;
}

.inspector__row--event {
  grid-template-columns: 28px minmax(70px, 1fr) auto 36px 36px;
}

.inspector__row--item {
  grid-template-columns: 24px 14px minmax(70px, 1fr) auto 36px 36px 36px;
}

.inspector__row--event :deep(.icon-button) {
  width: 30px;
  height: 28px;
}

.inspector__row--item :deep(.icon-button),
.inspector__point :deep(.icon-button),
.inspector__time-row :deep(.icon-button) {
  width: 30px;
  height: 28px;
}

.inspector__index {
  min-width: 22px;
  height: 22px;
  display: inline-grid;
  place-items: center;
  border-radius: 2px;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}

.inspector__index--active {
  background: var(--accent-primary);
  color: #000;
}

.inspector__row:nth-child(even) {
  background: var(--surface-header);
}

.inspector__text,
.inspector__form input {
  min-width: 0;
  border: 0;
  background: transparent;
  color: var(--text-color);
}

.inspector__marker,
.inspector__color {
  width: 14px;
  height: 14px;
}

.inspector__color {
  border: 0;
  padding: 0;
  background: transparent;
}

.inspector__collapse {
  width: 22px;
  height: 22px;
  border: 1px solid var(--surface-border);
  background: var(--surface-button);
  color: var(--text-color);
  cursor: pointer;
}

.inspector__item {
  padding: 8px 0;
  border-bottom: 1px solid var(--surface-border);
  cursor: pointer;
}

.inspector__item--active {
  background: var(--surface-header);
}

.inspector__points {
  display: grid;
  gap: 8px;
  margin: 12px 0 0 38px;
  color: var(--text-muted);
}

.inspector__point,
.inspector__item-config label {
  display: grid;
  grid-template-columns: 72px 1fr 1fr 30px 30px;
  align-items: center;
  gap: 6px;
}

.inspector__item-config .inspector__checkbox {
  grid-template-columns: 112px 18px;
  justify-content: start;
}

.inspector__point input,
.inspector__item-config input,
.inspector__item-config select {
  min-width: 0;
  height: 26px;
  border: 1px solid var(--surface-border);
  background: var(--surface-button);
  color: var(--text-color);
}

.inspector__item-config {
  display: grid;
  gap: 8px;
  margin: 12px 0 0 38px;
}

.inspector__form {
  display: grid;
  align-content: start;
  gap: 12px;
}

.inspector__form label {
  display: grid;
  grid-template-columns: 48px 1fr 58px;
  align-items: center;
  gap: 8px;
}

.inspector__form .inspector__time-row {
  grid-template-columns: 48px 1fr 58px 48px;
}

.inspector__form .inspector__checkbox-row {
  grid-template-columns: 100px 18px;
  justify-content: start;
}

.inspector__form input,
.inspector__form button,
.inspector__action {
  min-height: 30px;
  border: 1px solid var(--surface-border);
  background: var(--surface-button);
  color: var(--text-color);
}

.inspector__action {
  padding: 0 12px;
  cursor: pointer;
}

.inspector__action:disabled {
  cursor: wait;
  opacity: 0.65;
}

.inspector__action--danger {
  border-color: #a33;
  color: #ff8f8f;
}

.inspector__progress {
  display: grid;
  grid-template-columns: 18px 1fr 40px;
  align-items: center;
  gap: 8px;
}

.inspector__progress progress {
  width: 100%;
  accent-color: var(--accent-primary);
}

.inspector__spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--surface-border);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: inspector-spin 0.8s linear infinite;
}

@keyframes inspector-spin {
  to {
    transform: rotate(360deg);
  }
}

.inspector__action--small {
  min-height: 28px;
  padding: 0 8px;
}

.inspector__status {
  margin: 0;
  color: var(--text-muted);
}

.inspector__status--error {
  color: #ff7878;
}
</style>
