export class EventsService {
    constructor(projectService, timelineService) {
        this.projectService = projectService;
        this.timelineService = timelineService;
    }

    get state() {
        return this.projectService.state.data;
    }

    async add(label = "Shot") {
        const time = this.timelineService.state.currentTime;
        const event = {
            id: crypto.randomUUID(),
            label,
            time_from: time
        };

        this.state.events.push(event);
        await this.saveEvents();
    }

    async update(id, patch) {
        const item = this.state.events.find((event) => event.id === id);
        if (!item) return;
        Object.assign(item, patch);
        const videoPath = this.state.video_path;
        if (window.pywebview?.api?.update_event && videoPath) {
            await window.pywebview.api.update_event({ video_path: videoPath, id, patch });
            return;
        }

        await this.saveEvents();
    }

    async remove(id) {
        this.state.events = this.state.events.filter((event) => event.id !== id);
        const videoPath = this.state.video_path;
        if (window.pywebview?.api?.delete_event && videoPath) {
            await window.pywebview.api.delete_event({ video_path: videoPath, id });
            return;
        }

        await this.saveEvents();
    }

    async clear() {
        this.state.events = [];
        const videoPath = this.state.video_path;
        if (window.pywebview?.api?.delete_all_events && videoPath) {
            await window.pywebview.api.delete_all_events(videoPath);
            return;
        }

        await this.saveEvents();
    }

    jump(event) {
        this.timelineService.setCurrentTime(event?.time_from || 0);
    }

    async saveEvents() {
        const videoPath = this.state.video_path;
        if (window.pywebview?.api?.save_events && videoPath) {
            await window.pywebview.api.save_events({
                video_path: videoPath,
                events: JSON.parse(JSON.stringify(this.state.events))
            });
            return;
        }

        await this.projectService.save();
    }
}
