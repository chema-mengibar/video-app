import { reactive } from "vue";

const clonePoint = (point) => ({ x: point.x, y: point.y });

const defaultField = () => ({
    points: [
        { x: 20, y: 20 },
        { x: 80, y: 20 },
        { x: 20, y: 80 },
        { x: 80, y: 80 }
    ],
    abMeters: 28.65,
    acMeters: 15.24,
    paddingX: 0,
    paddingY: 0
});

const defaultGridItem = (source = defaultField()) => ({
    id: crypto.randomUUID(),
    type: "measure-grid",
    label: "Measure Grid",
    time_from: 0,
    time_to: 3,
    color: "#45FFA2",
    width: 2,
    opacity: 0.85,
    visible: true,
    chessboard: false,
    dimensionPreset: source.dimensionPreset || "Basketball NBA",
    points: source.points.map(clonePoint),
    abMeters: source.abMeters,
    acMeters: source.acMeters,
    paddingX: Number(source.paddingX) || 0,
    paddingY: Number(source.paddingY) || 0
});

export class MeasureService {
    constructor(projectService, timelineService) {
        this.projectService = projectService;
        this.timelineService = timelineService;
        this.state = reactive({
            selectedTool: null,
            editMode: null,
            editPointIndex: null,
            selectedItemId: null,
            draftItem: null,
            displayGrid: null,
            fieldDraft: defaultField(),
            playerConfig: {
                widthPx: 22,
                lengthPx: 22,
                guestColor: "#ff4d4d",
                homeColor: "#4d8dff",
                ballColor: "#ffd84d"
            }
        });
        this.dragStart = null;
        this.moveStartPoints = [];
        this.moveStartPoint = null;
        this.moveStartWorldPoints = [];
    }

    get data() {
        return this.projectService.state.data;
    }

    get field() {
        return this.gridItem || this.data.measure?.field || this.state.fieldDraft;
    }

    get gridItem() {
        const sourceGrid = this.items.find((item) => item.type === "measure-grid") || null;
        return this.normalizeGridItem(this.state.editMode ? sourceGrid : this.state.displayGrid || sourceGrid);
    }

    normalizeGridItem(grid) {
        if (!grid) {
            return null;
        }

        grid.visible = grid.visible !== false;
        grid.chessboard = !!grid.chessboard;
        grid.dimensionPreset = grid.dimensionPreset || "Basketball NBA";
        grid.points = grid.points?.length ? grid.points : defaultField().points;
        grid.abMeters = Number(grid.abMeters) || 28.65;
        grid.acMeters = Number(grid.acMeters) || 15.24;
        grid.paddingX = Math.max(0, Number(grid.paddingX) || 0);
        grid.paddingY = Math.max(0, Number(grid.paddingY) || 0);
        return grid;
    }

    get items() {
        if (!this.data.items) {
            this.data.items = [];
        }
        return this.data.items;
    }

    get selectedItem() {
        return this.items.find((item) => item.id === this.state.selectedItemId) || null;
    }

    get sourceGridItem() {
        return this.items.find((item) => item.type === "measure-grid") || null;
    }

    selectTool(tool) {
        this.state.selectedTool = this.state.selectedTool === tool ? null : tool;
        this.state.editMode = null;
        this.state.editPointIndex = null;
    }

    clearTool() {
        this.state.selectedTool = null;
        this.state.editMode = null;
        this.state.editPointIndex = null;
    }

    startMoveFieldPoint(index) {
        const grid = this.sourceGridItem;
        this.prepareKeyframedItemForEdit(grid);
        if (!grid) return;
        if (this.isActiveFieldPoint(index)) {
            this.finishMove();
            return;
        }
        this.state.selectedTool = null;
        this.state.editMode = "field-point";
        this.state.editPointIndex = index;
    }

    startMoveMeasurePoint(id, index) {
        if (this.isActiveMeasurePoint(id, index)) {
            this.finishMove();
            return;
        }
        this.state.selectedItemId = id;
        this.prepareKeyframedItemForEdit(this.selectedItem);
        this.state.selectedTool = null;
        this.state.editMode = "measure-point";
        this.state.editPointIndex = index;
    }

    isActiveFieldPoint(index) {
        return this.state.editMode === "field-point" && this.state.editPointIndex === index;
    }

    isActiveMeasurePoint(id, index) {
        return this.state.editMode === "measure-point" && this.state.selectedItemId === id && this.state.editPointIndex === index;
    }

    updateFieldPoint(index, patch, id = null) {
        const grid = id ? this.items.find((item) => item.id === id) : this.sourceGridItem;
        this.prepareKeyframedItemForEdit(grid);
        if (!grid?.points?.[index]) return;
        Object.assign(grid.points[index], patch);
        this.saveMoveResult(grid);
    }

    updateFieldDimensions(patch) {
        const grid = this.sourceGridItem;
        this.prepareKeyframedItemForEdit(grid);
        if (!grid) return;
        Object.assign(grid, patch);
        this.saveMoveResult(grid);
    }

    applyDimensionPreset(preset) {
        const grid = this.sourceGridItem;
        this.prepareKeyframedItemForEdit(grid);
        if (!grid || !preset) return;
        Object.assign(grid, {
            dimensionPreset: preset.id,
            abMeters: preset.width,
            acMeters: preset.length
        });
        this.saveMoveResult(grid);
    }

    begin(point) {
        if (this.state.editMode === "image-item") {
            const item = this.selectedItem;
            this.prepareKeyframedItemForEdit(item);
            this.dragStart = clonePoint(point);
            this.moveStartPoint = item?.point ? clonePoint(item.point) : null;
            this.moveStartPoints = (item?.points || []).map(clonePoint);
            return;
        }

        if (this.state.editMode === "world-item") {
            const item = this.selectedItem;
            this.prepareKeyframedItemForEdit(item);
            this.dragStart = clonePoint(point);
            this.moveStartPoint = item?.point ? this.imageToWorld(item.point) : null;
            this.moveStartWorldPoints = (item?.points || []).map((candidate) => this.imageToWorld(candidate)).filter(Boolean);
            return;
        }

        if (this.state.editMode === "player-point") {
            this.prepareKeyframedItemForEdit(this.selectedItem);
            this.dragStart = clonePoint(point);
            this.moveStartPoints = [clonePoint(this.selectedItem.point)];
            return;
        }

        if (this.state.editMode === "field-point") {
            this.prepareKeyframedItemForEdit(this.sourceGridItem);
            this.dragStart = clonePoint(point);
            this.moveStartPoints = this.field.points.map(clonePoint);
            return;
        }

        if (this.state.editMode === "measure-point") {
            this.prepareKeyframedItemForEdit(this.selectedItem);
            this.dragStart = clonePoint(point);
            this.moveStartPoints = (this.selectedItem?.points || []).map(clonePoint);
            return;
        }

        if (this.state.selectedTool === "player" || this.state.selectedTool === "ball") {
            const start = this.timelineService.state.currentTime;
            const isBall = this.state.selectedTool === "ball";
            const item = {
                id: crypto.randomUUID(),
                type: this.state.selectedTool,
                label: isBall ? "Ball" : "Player",
                time_from: start,
                time_to: start + 3,
                color: isBall ? this.state.playerConfig.ballColor : this.state.playerConfig.guestColor,
                width: this.state.playerConfig.widthPx,
                length: this.state.playerConfig.lengthPx,
                opacity: 1,
                visible: true,
                point: clonePoint(point)
            };
            if (!isBall) {
                item.team = "guest";
            }
            this.items.push(item);
            this.state.selectedItemId = item.id;
            this.state.selectedTool = null;
            this.projectService.save();
            return;
        }

        if (this.state.selectedTool !== "measure-line") return;
        const grid = this.gridItem;
        if (!grid) return;
        const start = this.timelineService.state.currentTime;
        const item = {
            id: crypto.randomUUID(),
            type: "measure-line",
            label: "Measure",
            parentId: grid.id,
            time_from: start,
            time_to: start + 3,
            color: "#FFD84D",
            width: 2,
            opacity: 0.95,
            points: [clonePoint(point), clonePoint(point)]
        };
        this.state.draftItem = item;
        this.state.selectedItemId = item.id;
    }

    update(point) {
        if (this.state.editMode === "image-item") {
            const item = this.selectedItem;
            if (!item || !this.dragStart) return;
            const dx = point.x - this.dragStart.x;
            const dy = point.y - this.dragStart.y;

            if (item.point && this.moveStartPoint) {
                item.point = {
                    x: this.moveStartPoint.x + dx,
                    y: this.moveStartPoint.y + dy
                };
                return;
            }

            if (item.points?.length) {
                item.points = this.moveStartPoints.map((candidate) => ({
                    x: candidate.x + dx,
                    y: candidate.y + dy
                }));
            }
            return;
        }

        if (this.state.editMode === "world-item") {
            const item = this.selectedItem;
            if (!item || !this.dragStart) return;
            const dx = point.x - this.dragStart.x;
            const dy = point.y - this.dragStart.y;

            if (item.point && this.moveStartPoint) {
                const nextPoint = this.worldToImage({ x: this.moveStartPoint.x + dx, y: this.moveStartPoint.y + dy });
                if (nextPoint) {
                    item.point = nextPoint;
                }
                return;
            }

            if (item.points?.length && this.moveStartWorldPoints.length === item.points.length) {
                const nextPoints = this.moveStartWorldPoints
                    .map((candidate) => this.worldToImage({ x: candidate.x + dx, y: candidate.y + dy }))
                    .filter(Boolean);
                if (nextPoints.length === item.points.length) {
                    item.points = nextPoints;
                }
            }
            return;
        }

        if (this.state.editMode === "player-point") {
            const item = this.selectedItem;
            if (!item?.point || !this.dragStart || !this.moveStartPoints[0]) return;
            item.point = {
                x: this.moveStartPoints[0].x + point.x - this.dragStart.x,
                y: this.moveStartPoints[0].y + point.y - this.dragStart.y
            };
            return;
        }

        if (this.state.editMode === "field-point") {
            const index = this.state.editPointIndex;
            if (!this.moveStartPoints[index] || !this.dragStart) return;
            this.field.points[index] = {
                x: this.moveStartPoints[index].x + point.x - this.dragStart.x,
                y: this.moveStartPoints[index].y + point.y - this.dragStart.y
            };
            return;
        }

        if (this.state.editMode === "measure-point") {
            const item = this.selectedItem;
            const index = this.state.editPointIndex;
            if (!item?.points?.[index] || !this.moveStartPoints[index] || !this.dragStart) return;
            item.points[index] = {
                x: this.moveStartPoints[index].x + point.x - this.dragStart.x,
                y: this.moveStartPoints[index].y + point.y - this.dragStart.y
            };
            return;
        }

        if (!this.state.draftItem) return;
        this.state.draftItem.points[1] = clonePoint(point);
    }

    finish(point) {
        this.update(point);

        if (this.state.editMode) {
            this.finishMove();
            return;
        }

        if (!this.state.draftItem) return;
        const [start, end] = this.state.draftItem.points;
        if (Math.hypot(start.x - end.x, start.y - end.y) > 1) {
            this.items.push(this.state.draftItem);
            this.projectService.save();
        }
        this.state.draftItem = null;
        this.state.selectedTool = null;
        this.dragStart = null;
    }

    addGrid() {
        const existingGrid = this.gridItem;
        const currentTime = this.timelineService.state.currentTime;
        if (existingGrid && this.isItemActiveAt(existingGrid, currentTime)) {
            this.state.selectedItemId = existingGrid.id;
            return existingGrid;
        }

        const start = currentTime;
        const item = {
            ...defaultGridItem(this.data.measure?.field || this.state.fieldDraft),
            time_from: start,
            time_to: start + 3
        };
        this.items.unshift(item);
        this.state.selectedItemId = item.id;
        this.projectService.save();
        return item;
    }

    isItemActiveAt(item, time) {
        if (!item || item.visible === false) return false;
        const from = Number.isFinite(item.time_from) ? item.time_from : 0;
        const to = Number.isFinite(item.time_to) ? item.time_to : from;
        return time >= from && time <= to;
    }

    addChrono() {
        const start = this.timelineService.state.currentTime;
        const item = {
            id: crypto.randomUUID(),
            type: "chrono",
            label: "Chrono",
            time_from: start,
            time_to: start + 3,
            color: "#111111",
            width: 1,
            opacity: 1,
            visible: true
        };
        this.items.push(item);
        this.state.selectedItemId = item.id;
        this.projectService.save();
    }

    addDelay() {
        const start = this.timelineService.state.currentTime;
        const duration = 2;
        const item = {
            id: crypto.randomUUID(),
            type: "delay",
            label: "Delay",
            time_from: start,
            time_to: start + duration,
            duration,
            color: "#8FB8FF",
            width: 1,
            opacity: 0.75,
            visible: true
        };
        this.items.push(item);
        this.state.selectedItemId = item.id;
        this.projectService.save();
    }

    startMovePlayer(id) {
        const item = this.items.find((candidate) => candidate.id === id);
        this.prepareKeyframedItemForEdit(item);
        if (!item?.point) return;
        if (this.state.editMode === "player-point" && this.state.selectedItemId === id) {
            this.finishMove();
            return;
        }
        this.state.selectedItemId = id;
        this.state.selectedTool = null;
        this.state.editMode = "player-point";
        this.state.editPointIndex = null;
    }

    isActivePlayer(id) {
        return this.state.editMode === "player-point" && this.state.selectedItemId === id;
    }

    startImageMoveSelected(id) {
        const item = this.items.find((candidate) => candidate.id === id);
        this.prepareKeyframedItemForEdit(item);
        if (!item) return;
        if (this.isActiveImageMove(id)) {
            this.finishMove();
            return;
        }
        this.state.selectedItemId = id;
        this.state.selectedTool = null;
        this.state.editMode = "image-item";
        this.state.editPointIndex = null;
    }

    isActiveImageMove(id) {
        return this.state.editMode === "image-item" && this.state.selectedItemId === id;
    }

    startWorldMoveSelected(id) {
        const item = this.items.find((candidate) => candidate.id === id);
        this.prepareKeyframedItemForEdit(item);
        if (!item || !this.gridItem) return;
        if (this.isActiveWorldMove(id)) {
            this.finishMove();
            return;
        }
        this.state.selectedItemId = id;
        this.state.selectedTool = null;
        this.state.editMode = "world-item";
        this.state.editPointIndex = null;
    }

    isActiveWorldMove(id) {
        return this.state.editMode === "world-item" && this.state.selectedItemId === id;
    }

    updatePlayerPoint(id, patch) {
        const item = this.items.find((candidate) => candidate.id === id);
        this.prepareKeyframedItemForEdit(item);
        if (!item?.point) return;
        Object.assign(item.point, patch);
        this.saveMoveResult(item);
    }

    updateMeasurePoint(id, index, patch) {
        const item = this.items.find((candidate) => candidate.id === id);
        this.prepareKeyframedItemForEdit(item);
        if (!item?.points?.[index]) return;
        Object.assign(item.points[index], patch);
        this.saveMoveResult(item);
    }

    updatePlayerConfig(patch) {
        Object.assign(this.state.playerConfig, patch);
        if (patch.ballColor) {
            for (const item of this.items) {
                if (item.type === "ball") {
                    item.color = patch.ballColor;
                }
            }
            this.projectService.save();
        }
        if (patch.guestColor || patch.homeColor) {
            for (const item of this.items) {
                if (item.type === "player") {
                    item.color = item.team === "home" ? this.state.playerConfig.homeColor : this.state.playerConfig.guestColor;
                }
            }
            this.projectService.save();
        }
    }

    updatePlayerTeam(id, team) {
        const item = this.items.find((candidate) => candidate.id === id && candidate.type === "player");
        if (!item) return;
        item.team = team === "home" ? "home" : "guest";
        item.color = item.team === "home" ? this.state.playerConfig.homeColor : this.state.playerConfig.guestColor;
        this.projectService.save();
    }

    finishMove() {
        this.saveMoveResult(this.currentEditedItem());
        this.state.editMode = null;
        this.state.editPointIndex = null;
        this.dragStart = null;
        this.moveStartPoints = [];
        this.moveStartPoint = null;
        this.moveStartWorldPoints = [];
    }

    currentEditedItem() {
        if (this.state.editMode === "field-point") {
            return this.sourceGridItem;
        }
        return this.selectedItem;
    }

    saveMoveResult(item) {
        if (this.keyframeService?.updateCurrentKeyframeIfActive(item)) return;
        this.projectService.save();
    }

    prepareKeyframedItemForEdit(item) {
        this.keyframeService?.applyCurrentKeyframeGeometry(item);
    }

    measureLineMeters(item) {
        const [start, end] = item?.points || [];
        const startWorld = this.imageToWorld(start);
        const endWorld = this.imageToWorld(end);
        if (!startWorld || !endWorld) return null;

        return Math.hypot(endWorld.x - startWorld.x, endWorld.y - startWorld.y);
    }

    imageToWorld(point) {
        const matrix = this.homographyMatrix();
        if (!point || !matrix) return null;

        const denominator = matrix[6] * point.x + matrix[7] * point.y + 1;
        if (Math.abs(denominator) < 0.000001) return null;

        return {
            x: (matrix[0] * point.x + matrix[1] * point.y + matrix[2]) / denominator,
            y: (matrix[3] * point.x + matrix[4] * point.y + matrix[5]) / denominator
        };
    }

    worldToImage(point) {
        const matrix = this.inverseHomographyMatrix();
        if (!point || !matrix) return null;

        const denominator = matrix[6] * point.x + matrix[7] * point.y + 1;
        if (Math.abs(denominator) < 0.000001) return null;

        return {
            x: (matrix[0] * point.x + matrix[1] * point.y + matrix[2]) / denominator,
            y: (matrix[3] * point.x + matrix[4] * point.y + matrix[5]) / denominator
        };
    }

    homographyMatrix() {
        const field = this.gridItem;
        const [a, b, c, d] = field?.points || [];
        const width = Number(field?.abMeters) || 0;
        const height = Number(field?.acMeters) || 0;
        if (!a || !b || !c || !d || width <= 0 || height <= 0) return null;

        return solveHomography(
            [a, b, c, d],
            [
                { x: 0, y: 0 },
                { x: width, y: 0 },
                { x: 0, y: height },
                { x: width, y: height }
            ]
        );
    }

    inverseHomographyMatrix() {
        const field = this.gridItem;
        const [a, b, c, d] = field?.points || [];
        const width = Number(field?.abMeters) || 0;
        const height = Number(field?.acMeters) || 0;
        if (!a || !b || !c || !d || width <= 0 || height <= 0) return null;

        return solveHomography(
            [
                { x: 0, y: 0 },
                { x: width, y: 0 },
                { x: 0, y: height },
                { x: width, y: height }
            ],
            [a, b, c, d]
        );
    }
}

const solveHomography = (imagePoints, worldPoints) => {
    const rows = [];
    for (let index = 0; index < 4; index += 1) {
        const { x, y } = imagePoints[index];
        const { x: u, y: v } = worldPoints[index];
        rows.push([x, y, 1, 0, 0, 0, -u * x, -u * y, u]);
        rows.push([0, 0, 0, x, y, 1, -v * x, -v * y, v]);
    }

    const solution = solveLinearSystem(rows);
    return solution ? [...solution.slice(0, 8), 1] : null;
};

const solveLinearSystem = (matrix) => {
    const size = 8;
    const rows = matrix.map((row) => row.slice());

    for (let column = 0; column < size; column += 1) {
        let pivot = column;
        for (let row = column + 1; row < size; row += 1) {
            if (Math.abs(rows[row][column]) > Math.abs(rows[pivot][column])) {
                pivot = row;
            }
        }
        if (Math.abs(rows[pivot][column]) < 0.000001) return null;

        [rows[column], rows[pivot]] = [rows[pivot], rows[column]];
        const pivotValue = rows[column][column];
        for (let col = column; col <= size; col += 1) {
            rows[column][col] /= pivotValue;
        }

        for (let row = 0; row < size; row += 1) {
            if (row === column) continue;
            const factor = rows[row][column];
            for (let col = column; col <= size; col += 1) {
                rows[row][col] -= factor * rows[column][col];
            }
        }
    }

    return rows.map((row) => row[size]);
};
