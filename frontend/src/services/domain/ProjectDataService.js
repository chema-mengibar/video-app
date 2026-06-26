import { reactive } from "vue";

const emptyProject = () => ({
    video_path: null,
    events: [],
    items: [],
    measure: {
        field: {
            points: [
                { x: 20, y: 20 },
                { x: 80, y: 20 },
                { x: 20, y: 80 },
                { x: 80, y: 80 }
            ],
            abMeters: 60,
            acMeters: 30
        }
    },
    cut: {
        time_from: 0,
        time_to: 0
    }
});

export class ProjectDataService {
    constructor() {
        this.state = reactive({
            data: emptyProject(),
            saveStatus: "idle"
        });
    }

    async load(videoPath) {
        const loaded = await window.pywebview?.api?.load_project?.(videoPath);
        this.state.data = {
            ...emptyProject(),
            ...(loaded || {}),
            video_path: videoPath
        };
        return this.state.data;
    }

    async save() {
        const videoPath = this.state.data?.video_path;
        if (!videoPath) return;

        this.state.saveStatus = "saving";
        const result = await window.pywebview?.api?.save_project?.({
            video_path: videoPath,
            data: JSON.parse(JSON.stringify(this.state.data))
        });
        this.state.saveStatus = result?.status === "error" ? "error" : "saved";
    }
}
