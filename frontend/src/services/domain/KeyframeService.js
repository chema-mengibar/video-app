const clone = (value) => JSON.parse(JSON.stringify(value));

const geometryKeys = [
    "points",
    "point",
    "center",
    "radius",
    "height",
    "rotation",
    "path",
    "abMeters",
    "acMeters",
    "paddingX",
    "paddingY"
];

const numberOrNull = (value) => Number.isFinite(Number(value)) ? Number(value) : null;

const lerp = (a, b, t) => a + (b - a) * t;

const interpolatePoint = (a, b, t) => {
    if (!a || !b) return null;
    return {
        x: lerp(Number(a.x) || 0, Number(b.x) || 0, t),
        y: lerp(Number(a.y) || 0, Number(b.y) || 0, t)
    };
};

const pathPoints = (path) => Array.from(String(path || "").matchAll(/[ML]\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)/g))
    .map((match) => ({ x: Number(match[1]), y: Number(match[2]) }));

const pathFromPoints = (points) => points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ");

const snapshotGeometry = (item) => {
    const geometry = {};
    for (const key of geometryKeys) {
        if (item[key] !== undefined) {
            geometry[key] = clone(item[key]);
        }
    }
    return geometry;
};

const applyGeometry = (item, geometry) => {
    const next = { ...item };
    for (const key of geometryKeys) {
        if (geometry[key] !== undefined) {
            next[key] = clone(geometry[key]);
        }
    }
    return next;
};

const interpolateGeometry = (from, to, ratio) => {
    const result = {};
    const keys = new Set([...Object.keys(from || {}), ...Object.keys(to || {})]);

    for (const key of keys) {
        const a = from?.[key];
        const b = to?.[key];

        if (key === "point" || key === "center") {
            result[key] = interpolatePoint(a, b, ratio) || clone(a ?? b);
            continue;
        }

        if (key === "points" && Array.isArray(a) && Array.isArray(b) && a.length === b.length) {
            result[key] = a.map((point, index) => interpolatePoint(point, b[index], ratio) || clone(point));
            continue;
        }

        if (key === "path") {
            const aPoints = pathPoints(a);
            const bPoints = pathPoints(b);
            if (aPoints.length >= 2 && aPoints.length === bPoints.length) {
                result[key] = pathFromPoints(aPoints.map((point, index) => interpolatePoint(point, bPoints[index], ratio) || clone(point)));
            } else {
                result[key] = ratio < 0.5 ? clone(a) : clone(b);
            }
            continue;
        }

        const aNumber = numberOrNull(a);
        const bNumber = numberOrNull(b);
        if (aNumber !== null && bNumber !== null) {
            result[key] = lerp(aNumber, bNumber, ratio);
            continue;
        }

        result[key] = ratio < 0.5 ? clone(a) : clone(b);
    }

    return result;
};

export class KeyframeService {
    constructor(projectService, timelineService) {
        this.projectService = projectService;
        this.timelineService = timelineService;
        this.epsilon = 0.05;
    }

    keyframesFor(item, create = false) {
        if (!item) return [];
        if (!Array.isArray(item.keyframes)) {
            if (!create) return [];
            item.keyframes = [];
        }
        return item.keyframes.sort((a, b) => (Number(a.time) || 0) - (Number(b.time) || 0));
    }

    itemAtTime(item, time = this.timelineService.state.currentTime) {
        const keyframes = this.keyframesFor(item);
        if (!keyframes.length) return item;

        const currentTime = Number(time) || 0;
        const exact = keyframes.find((keyframe) => Math.abs((Number(keyframe.time) || 0) - currentTime) <= this.epsilon);
        if (exact) return applyGeometry(item, exact.geometry || {});

        const previous = [...keyframes].reverse().find((keyframe) => (Number(keyframe.time) || 0) < currentTime);
        const next = keyframes.find((keyframe) => (Number(keyframe.time) || 0) > currentTime);
        if (!previous && !next) return item;
        if (!previous) return applyGeometry(item, next.geometry || {});
        if (!next) return applyGeometry(item, previous.geometry || {});

        const fromTime = Number(previous.time) || 0;
        const toTime = Number(next.time) || fromTime;
        const ratio = toTime === fromTime ? 0 : Math.min(1, Math.max(0, (currentTime - fromTime) / (toTime - fromTime)));
        return applyGeometry(item, interpolateGeometry(previous.geometry || {}, next.geometry || {}, ratio));
    }

    addKeyframe(item, time = this.timelineService.state.currentTime) {
        if (!item) return;
        const keyframes = this.keyframesFor(item, true);
        const currentTime = Number(time) || 0;
        const existing = keyframes.find((keyframe) => Math.abs((Number(keyframe.time) || 0) - currentTime) <= this.epsilon);
        const keyframe = {
            id: existing?.id || crypto.randomUUID(),
            time: currentTime,
            geometry: snapshotGeometry(item)
        };
        if (existing) {
            Object.assign(existing, keyframe);
        } else {
            keyframes.push(keyframe);
        }
        this.projectService.save();
    }

    removeKeyframeAt(item, time = this.timelineService.state.currentTime) {
        if (!item?.keyframes?.length) return;
        const currentTime = Number(time) || 0;
        const index = item.keyframes.findIndex((keyframe) => Math.abs((Number(keyframe.time) || 0) - currentTime) <= this.epsilon);
        if (index >= 0) {
            item.keyframes.splice(index, 1);
            this.projectService.save();
        }
    }

    hasKeyframeAt(item, time = this.timelineService.state.currentTime) {
        return !!item?.keyframes?.some((keyframe) => Math.abs((Number(keyframe.time) || 0) - (Number(time) || 0)) <= this.epsilon);
    }

    applyCurrentKeyframeGeometry(item, time = this.timelineService.state.currentTime) {
        if (!item?.keyframes?.length) return false;
        const currentTime = Number(time) || 0;
        const keyframe = item.keyframes.find((candidate) => Math.abs((Number(candidate.time) || 0) - currentTime) <= this.epsilon);
        if (!keyframe) return false;
        Object.assign(item, applyGeometry(item, keyframe.geometry || {}));
        return true;
    }

    updateCurrentKeyframeIfActive(item, time = this.timelineService.state.currentTime) {
        if (!this.hasKeyframeAt(item, time)) return false;
        this.addKeyframe(item, time);
        return true;
    }
}
