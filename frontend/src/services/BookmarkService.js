import { reactive } from "vue";

export class BookmarkService {
    constructor(videoService) {
        this.state = reactive({ items: [] });
        this.videoService = videoService;
    }

    async load(videoPath) {
        if (!videoPath || videoPath.startsWith('blob:')) return;
        const results = await window.pywebview?.api?.get_bookmarks?.(videoPath);
        this.state.items = results || [];
    }

    async add(videoPath, timeMsec, label) {
        if (!videoPath || videoPath.startsWith('blob:')) return;

        this.state.items.push({ time_msec: timeMsec, label });
        this.state.items.sort((a, b) => a.time_msec - b.time_msec);
        await this.sync(videoPath);
    }

    async remove(videoPath, index) {
        if (!videoPath || !Number.isInteger(index)) return;

        this.state.items.splice(index, 1);

        await this.sync(videoPath);
    }

    async sync(videoPath) {
        if (!videoPath) return;

        await window.pywebview?.api?.save_bookmarks?.({
            video_path: videoPath,
            marks: JSON.parse(JSON.stringify(this.state.items))
        });
    }

    seek(msec) {
        this.videoService?.seek(msec);
    }
}
