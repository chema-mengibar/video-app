import { reactive } from "vue";

export class CutService {
    constructor(projectService, timelineService) {
        this.projectService = projectService;
        this.timelineService = timelineService;
        this.state = reactive({
            status: "idle",
            message: "",
            taskId: null,
            path: "",
            progress: 0,
            estimatedSeconds: null,
            oneToOneVelocity: true,
            quality: 90
        });
        this.pollTimer = null;
    }

    setFromNow() {
        this.projectService.state.data.cut.time_from = this.timelineService.state.currentTime;
        this.projectService.save();
    }

    setToNow() {
        this.projectService.state.data.cut.time_to = this.timelineService.state.currentTime;
        this.projectService.save();
    }

    async export() {
        const data = this.projectService.state.data;
        this.state.status = "idle";
        this.state.message = "";
        this.state.taskId = null;
        this.state.path = "";
        this.state.progress = 0;
        this.state.estimatedSeconds = null;
        this.stopPolling();

        if (!data.video_path) {
            this.state.status = "error";
            this.state.message = "Load a video first.";
            return;
        }

        if (this.timelineService.state.mediaType === "image") {
            this.state.status = "error";
            this.state.message = "Cut export is only available for videos.";
            return;
        }

        const start = Math.min(Number(data.cut.time_from) || 0, Number(data.cut.time_to) || 0);
        const end = Math.max(Number(data.cut.time_from) || 0, Number(data.cut.time_to) || 0);
        if (end <= start) {
            this.state.status = "error";
            this.state.message = "Set a valid cut range.";
            return;
        }

        if (!window.pywebview?.api?.export_clip) {
            this.state.status = "error";
            this.state.message = "Cut export requires the desktop app.";
            return;
        }

        this.state.status = "processing";
        this.state.message = "Saving cut...";
        const result = await window.pywebview.api.export_clip({
            video_path: data.video_path,
            start: Math.round(start * 1000),
            end: Math.round(end * 1000),
            playback_speed: this.state.oneToOneVelocity ? 1 : this.timelineService.state.speed,
            quality: this.state.quality,
            overlay_data: JSON.parse(JSON.stringify(data))
        });

        if (result?.status === "error") {
            this.state.status = "error";
            this.state.message = result.message || "Could not save cut.";
            return;
        }

        this.state.taskId = result?.task_id || null;
        this.state.path = result?.path || "";
        this.startPolling();
    }

    startPolling() {
        this.stopPolling();
        if (!this.state.taskId || !window.pywebview?.api?.get_export_status) return;
        this.pollTimer = window.setInterval(() => this.pollStatus(), 500);
        this.pollStatus();
    }

    stopPolling() {
        if (this.pollTimer) {
            window.clearInterval(this.pollTimer);
            this.pollTimer = null;
        }
    }

    async pollStatus() {
        if (!this.state.taskId || !window.pywebview?.api?.get_export_status) return;
        const result = await window.pywebview.api.get_export_status(this.state.taskId);
        this.state.status = result?.status || "error";
        this.state.message = result?.message || "";
        this.state.path = result?.path || this.state.path;
        this.state.progress = Number.isFinite(result?.progress) ? result.progress : this.state.progress;
        this.state.estimatedSeconds = Number.isFinite(result?.estimated_seconds) ? result.estimated_seconds : null;
        if (this.state.status === "done") {
            this.state.message = `Cut saved: ${this.state.path}`;
            this.stopPolling();
        } else if (this.state.status === "error") {
            this.state.message = result?.message || "Could not save cut.";
            this.stopPolling();
        } else if (this.state.status === "canceled") {
            this.state.message = result?.message || "Export canceled.";
            this.state.path = "";
            this.state.progress = 0;
            this.stopPolling();
        }
    }

    async cancelExport() {
        if (!this.state.taskId || !window.pywebview?.api?.cancel_export) return;
        this.state.message = "Canceling export...";
        await window.pywebview.api.cancel_export(this.state.taskId);
        await this.pollStatus();
    }

    async openOutputFolder() {
        if (!this.state.path || !window.pywebview?.api?.open_path_in_explorer) return;
        await window.pywebview.api.open_path_in_explorer(this.state.path);
    }

    jumpToFrom() {
        this.timelineService.setCurrentTime(Number(this.projectService.state.data.cut.time_from) || 0);
    }

    jumpToTo() {
        this.timelineService.setCurrentTime(Number(this.projectService.state.data.cut.time_to) || 0);
    }
}
