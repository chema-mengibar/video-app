import { reactive } from "vue";

export class VideoService {
    constructor() {
        this.state = reactive({
            videoPath: null,
            videoUrl: null,
            isPlaying: false,
            currentTime: 0,
            duration: 0,
            isLoaded: false
        });
    }

    loadVideo(path, videoUrl) {
        this.state.videoPath = path;
        this.state.videoUrl = videoUrl;
        this.state.isLoaded = !!path;
        this.state.isPlaying = false;
        this.state.currentTime = 0;
        this.state.duration = 0;
    }

    seek(msec) {
        const seconds = Number.isFinite(msec) ? msec / 1000 : 0;
        this.state.currentTime = seconds;
    }

    play() {
        if (this.state.isLoaded) {
            this.state.isPlaying = true;
        }
    }

    pause() {
        this.state.isPlaying = false;
    }

    stop() {
        this.state.isPlaying = false;
        this.state.currentTime = 0;
    }

    togglePlay() {
        if (this.state.isPlaying) this.pause();
        else this.play();
    }

    updateDuration(duration) {
        this.state.duration = duration;
    }
}
