import { reactive } from "vue";

const clonePoint = (point) => ({ x: point.x, y: point.y });
const pathFromPoints = (points) => points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ");
const movePath = (path, dx, dy) => String(path || "").replace(
    /([ML])\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)/g,
    (_, command, x, y) => `${command} ${Number(x) + dx} ${Number(y) + dy}`
);
const pathPoints = (path) => Array.from(String(path || "").matchAll(/[ML]\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)/g))
    .map((match) => ({ x: Number(match[1]), y: Number(match[2]) }));

export class DrawItemsService {
    constructor(projectService, timelineService) {
        this.projectService = projectService;
        this.timelineService = timelineService;
        this.state = reactive({
            selectedTool: null,
            selectedItemId: null,
            mode: "draw",
            editMode: null,
            editPointIndex: null,
            focusItemId: null,
            draftItem: null,
            moveSpace: "canvas",
            config: {
                color: "#45FFA2",
                width: 2,
                opacity: 0.8
            }
        });
        this.dragStart = null;
        this.moveStartPoints = [];
        this.moveStartCenter = null;
        this.moveStartRadius = null;
        this.moveStartHeight = null;
        this.moveStartPath = "";
        this.moveStartWorldPoints = [];
        this.moveMeasureService = null;
    }

    get data() {
        return this.projectService.state.data;
    }

    get items() {
        return this.data.items || [];
    }

    get selectedItem() {
        return this.items.find((item) => item.id === this.state.selectedItemId) || null;
    }

    selectTool(tool) {
        if (this.state.draftItem?.type === "polyline") {
            this.finishPolyline();
        }
        this.state.selectedTool = tool;
        this.state.mode = "draw";
        this.state.editMode = null;
        this.state.editPointIndex = null;
    }

    selectItem(id) {
        this.state.selectedItemId = id;
        this.prepareKeyframedItemForEdit(this.selectedItem);
    }

    focusItem(id) {
        this.state.selectedItemId = id;
        this.state.focusItemId = id;
    }

    consumeFocusItem() {
        const id = this.state.focusItemId;
        this.state.focusItemId = null;
        return id;
    }

    startMoveSelected(id = this.state.selectedItemId) {
        if (this.isActiveMove(id, "move")) {
            this.finishMoveMode();
            return;
        }

        this.selectItem(id);
        this.prepareKeyframedItemForEdit(this.selectedItem);
        if (!this.selectedItem) return;
        this.state.mode = "move";
        this.state.editMode = "move";
        this.state.editPointIndex = null;
        this.state.moveSpace = "canvas";
    }

    startWorldMoveSelected(id = this.state.selectedItemId, measureService) {
        if (this.isActiveWorldMove(id)) {
            this.finishMoveMode();
            return;
        }

        this.selectItem(id);
        this.prepareKeyframedItemForEdit(this.selectedItem);
        if (!this.selectedItem || !measureService?.gridItem) return;
        this.state.mode = "move";
        this.state.editMode = "world-move";
        this.state.editPointIndex = null;
        this.state.moveSpace = "court";
        this.moveMeasureService = measureService;
    }

    startMovePoint(id, index) {
        if (this.isActiveMove(id, "point", index)) {
            this.finishMoveMode();
            return;
        }

        this.selectItem(id);
        this.prepareKeyframedItemForEdit(this.selectedItem);
        if (!this.selectedItem?.points?.[index]) return;
        this.state.mode = "move";
        this.state.editMode = "point";
        this.state.editPointIndex = index;
        this.state.moveSpace = "canvas";
    }

    startResizeCircle(id) {
        if (this.isActiveMove(id, "radius")) {
            this.finishMoveMode();
            return;
        }

        this.selectItem(id);
        this.prepareKeyframedItemForEdit(this.selectedItem);
        if (this.selectedItem?.type !== "circle") return;
        this.state.mode = "move";
        this.state.editMode = "radius";
        this.state.editPointIndex = null;
        this.state.moveSpace = "canvas";
    }

    startResizeCircleHeight(id) {
        if (this.isActiveMove(id, "height")) {
            this.finishMoveMode();
            return;
        }

        this.selectItem(id);
        this.prepareKeyframedItemForEdit(this.selectedItem);
        if (this.selectedItem?.type !== "circle") return;
        this.state.mode = "move";
        this.state.editMode = "height";
        this.state.editPointIndex = null;
        this.state.moveSpace = "canvas";
    }

    begin(point) {
        if (this.state.mode === "move" && this.state.editMode === "world-move") {
            this.beginWorldMove(point);
            return;
        }

        if (this.state.mode === "move") {
            this.dragStart = clonePoint(point);
            this.moveStartPoints = (this.selectedItem?.points || []).map(clonePoint);
            const circle = this.circleGeometry(this.selectedItem);
            this.moveStartCenter = circle ? clonePoint(circle.center) : null;
            this.moveStartRadius = circle?.radius || 0;
            this.moveStartHeight = circle?.height || circle?.radius || 0;
            this.moveStartPath = this.selectedItem?.path || "";
            return;
        }

        if (!this.state.selectedTool) return;

        if (this.state.selectedTool === "polyline") {
            this.addPolylinePoint(point);
            return;
        }

        const start = this.timelineService.state.currentTime;
        const item = {
            id: crypto.randomUUID(),
            type: this.state.selectedTool,
            label: this.labelFor(this.state.selectedTool),
            time_from: start,
            time_to: start + 3,
            color: this.state.config.color,
            width: this.state.config.width,
            opacity: this.state.config.opacity,
            fillOpacity: 0.4,
            fillMode: "normal",
            points: [clonePoint(point)]
        };

        if (this.state.selectedTool === "circle") {
            item.center = clonePoint(point);
            item.radius = 0;
            item.height = 0;
            item.oval = false;
            item.rotation = 0;
            delete item.points;
        }

        this.dragStart = clonePoint(point);
        this.state.draftItem = item;
        this.state.selectedItemId = item.id;
        this.update(point);
    }

    update(point) {
        if (this.state.mode === "move" && this.state.editMode === "world-move") {
            this.moveSelectedInWorld(point);
            return;
        }

        if (this.state.mode === "move") {
            this.moveSelected(point);
            return;
        }

        if (!this.state.draftItem || !this.dragStart) return;
        this.applyDraftGeometry(this.state.draftItem, this.state.selectedTool, this.dragStart, point);
    }

    finish(point) {
        if (this.state.mode === "move" && this.state.editMode === "world-move") {
            this.moveSelectedInWorld(point);
            this.saveMoveResult(this.selectedItem);
            this.clearMoveState();
            return;
        }

        if (this.state.mode === "move") {
            this.moveSelected(point);
            this.saveMoveResult(this.selectedItem);
            this.clearMoveState();
            return;
        }

        if (this.state.draftItem?.type === "polyline") {
            this.finishPolyline();
            return;
        }

        if (!this.state.draftItem) return;
        this.update(point);
        if (this.state.draftItem.type === "free-line") {
            this.state.draftItem.path = pathFromPoints(this.state.draftItem.points || []);
            delete this.state.draftItem.points;
        }
        this.items.push(this.state.draftItem);
        this.state.selectedItemId = this.state.draftItem.id;
        this.state.draftItem = null;
        this.dragStart = null;
        this.state.selectedTool = null;
        this.projectService.save();
    }

    cancel() {
        this.state.draftItem = null;
        this.dragStart = null;
        this.moveStartPoints = [];
        this.moveStartCenter = null;
        this.moveStartRadius = null;
        this.moveStartPath = "";
        this.moveStartWorldPoints = [];
    }

    addPolylinePoint(point) {
        const start = this.timelineService.state.currentTime;
        if (!this.state.draftItem || this.state.draftItem.type !== "polyline") {
            const item = {
                id: crypto.randomUUID(),
                type: "polyline",
                label: this.labelFor("polyline"),
                time_from: start,
                time_to: start + 3,
                color: this.state.config.color,
                width: this.state.config.width,
                opacity: this.state.config.opacity,
                fillOpacity: 0.4,
                fillMode: "normal",
                closed: false,
                points: []
            };
            this.state.draftItem = item;
            this.state.selectedItemId = item.id;
        }

        this.state.draftItem.points.push(clonePoint(point));
    }

    finishPolyline() {
        if (!this.state.draftItem || this.state.draftItem.type !== "polyline") return;
        const draftId = this.state.draftItem.id;
        if ((this.state.draftItem.points || []).length >= 2) {
            this.items.push(this.state.draftItem);
            this.state.selectedItemId = this.state.draftItem.id;
            this.projectService.save();
        } else if (this.state.selectedItemId === draftId) {
            this.state.selectedItemId = null;
        }
        this.state.draftItem = null;
        this.dragStart = null;
        this.state.selectedTool = null;
    }

    updateSelected(patch) {
        if (!this.selectedItem) return;
        this.prepareKeyframedItemForEdit(this.selectedItem);
        Object.assign(this.selectedItem, patch);
        this.saveMoveResult(this.selectedItem);
    }

    updateSelectedPoint(index, patch, id = this.state.selectedItemId) {
        const item = this.items.find((candidate) => candidate.id === id);
        this.prepareKeyframedItemForEdit(item);
        if (!item?.points?.[index]) return;
        Object.assign(item.points[index], patch);
        this.saveMoveResult(item);
    }

    deletePoint(id, index) {
        const item = this.items.find((candidate) => candidate.id === id);
        if (item?.type !== "polyline" || !item.points?.[index]) return;

        item.points.splice(index, 1);
        if (this.state.selectedItemId === id && this.state.editMode === "point") {
            this.finishMoveMode();
        }
        if (item.points.length < 2) {
            this.deleteItem(id);
            return;
        }
        this.projectService.save();
    }

    deleteItem(id = this.state.selectedItemId) {
        const index = this.items.findIndex((item) => item.id === id);
        if (index < 0) return;
        const [removed] = this.items.splice(index, 1);
        if (removed?.type === "measure-grid") {
            for (let childIndex = this.items.length - 1; childIndex >= 0; childIndex -= 1) {
                const child = this.items[childIndex];
                if (child.parentId === id || child.type === "measure-line") {
                    this.items.splice(childIndex, 1);
                }
            }
        }
        if (this.state.selectedItemId === id) {
            this.state.selectedItemId = null;
        }
        this.projectService.save();
    }

    deleteSelected() {
        this.deleteItem();
    }

    moveSelected(point) {
        if (!this.selectedItem || !this.dragStart) return;
        const dx = point.x - this.dragStart.x;
        const dy = point.y - this.dragStart.y;

        if (this.state.editMode === "point" && this.selectedItem.points?.[this.state.editPointIndex]) {
            this.selectedItem.points[this.state.editPointIndex] = {
                x: this.moveStartPoints[this.state.editPointIndex].x + dx,
                y: this.moveStartPoints[this.state.editPointIndex].y + dy
            };
            return;
        }

        if (this.selectedItem.type === "free-line" && this.moveStartPath) {
            this.selectedItem.path = movePath(this.moveStartPath, dx, dy);
            return;
        }

        if (this.state.editMode === "radius" && this.selectedItem.type === "circle") {
            if (this.moveStartCenter) {
                this.selectedItem.center = clonePoint(this.moveStartCenter);
            }
            this.selectedItem.radius = Math.max(1, Math.hypot(point.x - this.selectedItem.center.x, point.y - this.selectedItem.center.y));
            return;
        }

        if (this.state.editMode === "height" && this.selectedItem.type === "circle") {
            if (this.moveStartCenter) {
                this.selectedItem.center = clonePoint(this.moveStartCenter);
            }
            this.selectedItem.height = Math.max(1, Math.hypot(point.x - this.selectedItem.center.x, point.y - this.selectedItem.center.y));
            return;
        }

        if (this.selectedItem.type === "circle" && this.moveStartCenter) {
            this.selectedItem.center = {
                x: this.moveStartCenter.x + dx,
                y: this.moveStartCenter.y + dy
            };
            return;
        }

        if (this.selectedItem.points) {
            this.selectedItem.points = this.moveStartPoints.map((startPoint) => ({
                x: startPoint.x + dx,
                y: startPoint.y + dy
            }));
        }
    }

    beginWorldMove(worldPoint) {
        if (!this.selectedItem || !this.moveMeasureService) return;
        this.dragStart = clonePoint(worldPoint);
        this.moveStartWorldPoints = this.worldPointsForItem(this.selectedItem, this.moveMeasureService);
    }

    moveSelectedInWorld(worldPoint) {
        if (!this.selectedItem || !this.dragStart || !this.moveMeasureService) return;
        const dx = worldPoint.x - this.dragStart.x;
        const dy = worldPoint.y - this.dragStart.y;

        if (this.selectedItem.type === "circle") {
            const startCenter = this.moveStartWorldPoints[0];
            const nextCenter = startCenter ? this.moveMeasureService.worldToImage({ x: startCenter.x + dx, y: startCenter.y + dy }) : null;
            if (nextCenter) {
                this.selectedItem.center = nextCenter;
            }
            return;
        }

        if (this.selectedItem.type === "free-line" && this.selectedItem.path) {
            const moved = this.moveStartWorldPoints
                .map((point) => this.moveMeasureService.worldToImage({ x: point.x + dx, y: point.y + dy }))
                .filter(Boolean);
            if (moved.length >= 2) {
                this.selectedItem.path = pathFromPoints(moved);
            }
            return;
        }

        if (this.selectedItem.points?.length) {
            const moved = this.moveStartWorldPoints
                .map((point) => this.moveMeasureService.worldToImage({ x: point.x + dx, y: point.y + dy }))
                .filter(Boolean);
            if (moved.length === this.selectedItem.points.length) {
                this.selectedItem.points = moved;
            }
        }
    }

    worldPointsForItem(item, measureService) {
        if (item.type === "circle") {
            const circle = this.circleGeometry(item);
            const center = circle ? measureService.imageToWorld(circle.center) : null;
            return center ? [center] : [];
        }

        if (item.type === "free-line" && item.path) {
            return pathPoints(item.path)
                .map((point) => measureService.imageToWorld(point))
                .filter(Boolean);
        }

        return (item.points || [])
            .map((point) => measureService.imageToWorld(point))
            .filter(Boolean);
    }

    finishMoveMode() {
        this.saveMoveResult(this.selectedItem);
        this.clearMoveState();
    }

    clearMoveState() {
        this.state.mode = "draw";
        this.state.editMode = null;
        this.state.editPointIndex = null;
        this.dragStart = null;
        this.moveStartPoints = [];
        this.moveStartCenter = null;
        this.moveStartRadius = null;
        this.moveStartHeight = null;
        this.moveStartPath = "";
        this.moveStartWorldPoints = [];
        this.moveMeasureService = null;
        this.state.moveSpace = "canvas";
    }

    saveMoveResult(item) {
        if (this.keyframeService?.updateCurrentKeyframeIfActive(item)) return;
        this.projectService.save();
    }

    prepareKeyframedItemForEdit(item) {
        this.keyframeService?.applyCurrentKeyframeGeometry(item);
    }

    isActiveMove(id, mode, pointIndex = null) {
        if (this.state.mode !== "move") return false;
        if (this.state.selectedItemId !== id) return false;
        if (this.state.editMode !== mode) return false;
        return mode !== "point" || this.state.editPointIndex === pointIndex;
    }

    isActiveWorldMove(id) {
        return this.state.mode === "move" && this.state.editMode === "world-move" && this.state.selectedItemId === id;
    }

    applyDraftGeometry(item, tool, start, end) {
        const safeEnd = this.hasDistance(start, end) ? end : { x: start.x + 12, y: start.y + 8 };

        if (tool === "free-line") {
            const current = item.points || [start];
            const last = current[current.length - 1];
            if (!last || Math.hypot(last.x - end.x, last.y - end.y) > 0.6) {
                item.points = [...current, clonePoint(end)];
            }
            return;
        }

        if (tool === "straight-line") {
            item.points = [clonePoint(start), clonePoint(safeEnd)];
            return;
        }

        if (tool === "triangle") {
            item.points = [
                { x: start.x, y: safeEnd.y },
                { x: (start.x + safeEnd.x) / 2, y: start.y },
                { x: safeEnd.x, y: safeEnd.y }
            ];
            return;
        }

        if (tool === "square") {
            item.asCircle = item.asCircle || false;
            item.points = [
                clonePoint(start),
                { x: safeEnd.x, y: start.y },
                clonePoint(safeEnd),
                { x: start.x, y: safeEnd.y }
            ];
            return;
        }

        if (tool === "polygon") {
            const center = { x: (start.x + safeEnd.x) / 2, y: (start.y + safeEnd.y) / 2 };
            const radiusX = Math.max(5, Math.abs(safeEnd.x - start.x) / 2);
            const radiusY = Math.max(5, Math.abs(safeEnd.y - start.y) / 2);
            item.points = Array.from({ length: 5 }, (_, index) => {
                const angle = -Math.PI / 2 + index * ((Math.PI * 2) / 5);
                return {
                    x: center.x + Math.cos(angle) * radiusX,
                    y: center.y + Math.sin(angle) * radiusY
                };
            });
            return;
        }

        if (tool === "circle") {
            item.center = clonePoint(start);
            item.radius = Math.max(1, Math.hypot(safeEnd.x - start.x, safeEnd.y - start.y));
            item.height = item.radius;
            item.oval = false;
            item.rotation = 0;
            delete item.points;
            return;
        }

        item.points = [clonePoint(start), clonePoint(safeEnd)];
    }

    hasDistance(start, end) {
        return Math.hypot(start.x - end.x, start.y - end.y) > 1;
    }

    circleGeometry(item) {
        if (!item || item.type !== "circle") return null;
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
    }

    labelFor(tool) {
        return tool
            .split("-")
            .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
            .join(" ");
    }
}
