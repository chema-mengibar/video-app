import { reactive } from "vue";

export class VideoTimelineService {
    constructor(projectService) {
        this.projectService = projectService;
        this.state = reactive({
            videoUrl: null,
            videoPath: null,
            mediaType: null,
            currentTime: 0,
            duration: 0,
            speed: 1,
            isPlaying: false,
            direction: 1
        });
    }

    async loadFile(file) {
        if (!file) return;

        const videoPath = file.path || file.name;
        const mediaType = this.mediaTypeFor(videoPath, file.type);
        const videoUrl = await this.resolveVideoUrl(videoPath, file);

        await this.loadVideo(videoPath, videoUrl, mediaType);
    }

    async loadFromPicker() {
        const selected = await (window.pywebview?.api?.choose_media_file?.() || window.pywebview?.api?.choose_video_file?.());
        if (!selected?.path || !selected?.url) return false;

        const videoUrl = await this.resolveVideoUrl(selected.path, null, selected.url);
        if (!videoUrl) return false;

        await this.loadVideo(selected.path, videoUrl, selected.media_type || this.mediaTypeFor(selected.path));
        return true;
    }

    async resolveVideoUrl(videoPath, file = null, providedUrl = null) {
        if (providedUrl && !providedUrl.startsWith("file:")) {
            return providedUrl;
        }

        const bridgeUrl = await window.pywebview?.api?.get_video_url?.(videoPath);
        if (bridgeUrl) {
            return bridgeUrl;
        }

        return file ? URL.createObjectURL(file) : null;
    }

    async loadVideo(videoPath, videoUrl, mediaType = "video") {
        if (this.state.videoUrl?.startsWith("blob:")) {
            URL.revokeObjectURL(this.state.videoUrl);
        }

        this.state.videoPath = videoPath;
        this.state.videoUrl = videoUrl;
        this.state.mediaType = mediaType;
        this.state.currentTime = 0;
        this.state.duration = mediaType === "image" ? 10 : 0;
        this.state.isPlaying = false;

        await this.projectService?.load(videoPath);
    }

    mediaTypeFor(path = "", mimeType = "") {
        if (String(mimeType).startsWith("image/")) return "image";
        if (String(mimeType).startsWith("video/")) return "video";

        const extension = String(path).split(".").pop()?.toLowerCase();
        return ["png", "jpg", "jpeg", "webp", "gif", "bmp"].includes(extension) ? "image" : "video";
    }

    setDuration(duration) {
        this.state.duration = Number.isFinite(duration) ? duration : 0;
    }

    getDisplayDuration() {
        return this.state.duration + this.delayItems().reduce((total, item) => total + this.delayDuration(item), 0);
    }

    delayItems() {
        return (this.projectService?.state?.data?.items || [])
            .filter((item) => item.type === "delay" && item.visible !== false)
            .sort((a, b) => this.delayStart(a) - this.delayStart(b));
    }

    delayStart(item) {
        return Math.max(0, Number(item?.time_from) || 0);
    }

    delayDuration(item) {
        return Math.max(0, Number(item?.duration) || 0);
    }

    delayEnd(item) {
        return this.delayStart(item) + this.delayDuration(item);
    }

    activeDelayAt(displayTime = this.state.currentTime) {
        return this.delayItems().find((item) => displayTime >= this.delayStart(item) && displayTime <= this.delayEnd(item)) || null;
    }

    displayToSourceTime(displayTime = this.state.currentTime) {
        const safeDisplayTime = Math.max(0, Number(displayTime) || 0);
        let accumulatedDelay = 0;
        for (const item of this.delayItems()) {
            const start = this.delayStart(item);
            const duration = this.delayDuration(item);
            if (safeDisplayTime < start) {
                break;
            }
            if (safeDisplayTime <= start + duration) {
                return Math.max(0, start - accumulatedDelay);
            }
            accumulatedDelay += duration;
        }
        const sourceTime = safeDisplayTime - accumulatedDelay;
        return Math.min(this.state.duration, Math.max(0, sourceTime));
    }

    setCurrentTime(time) {
        const maxTime = this.getDisplayDuration();
        this.state.currentTime = Math.min(maxTime, Math.max(0, Number.isFinite(time) ? time : 0));
    }

    setSpeed(speed) {
        this.state.speed = Number(speed) || 1;
    }

    seek(deltaSeconds) {
        this.setCurrentTime(this.state.currentTime + deltaSeconds);
    }

    frame(delta) {
        this.seek(delta / 30);
    }

    play(direction = 1) {
        if (!this.state.videoUrl) return;
        if (this.state.mediaType === "image") return;
        this.state.direction = direction;
        this.state.isPlaying = true;
    }

    pause() {
        this.state.isPlaying = false;
    }

    togglePlay() {
        if (this.state.isPlaying) {
            this.pause();
        } else {
            this.play(1);
        }
    }

}
