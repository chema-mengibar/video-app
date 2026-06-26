import { ProjectDataService } from "@/services/domain/ProjectDataService.js";
import { VideoTimelineService } from "@/services/domain/VideoTimelineService.js";
import { EventsService } from "@/services/domain/EventsService.js";
import { DrawItemsService } from "@/services/domain/DrawItemsService.js";
import { MeasureService } from "@/services/domain/MeasureService.js";
import { CutService } from "@/services/domain/CutService.js";
import { KeyframeService } from "@/services/domain/KeyframeService.js";
import { reactive } from "vue";

export const SERVICES_KEY = Symbol('AppServices');

export function createServiceRegistry() {
    const projectService = new ProjectDataService();
    const timelineService = new VideoTimelineService(projectService);
    const eventsService = new EventsService(projectService, timelineService);
    const drawService = new DrawItemsService(projectService, timelineService);
    const measureService = new MeasureService(projectService, timelineService);
    const cutService = new CutService(projectService, timelineService);
    const keyframeService = new KeyframeService(projectService, timelineService);
    drawService.keyframeService = keyframeService;
    measureService.keyframeService = keyframeService;
    const stageService = reactive({
        activePanel: "canvas"
    });

    return {
        projectService,
        timelineService,
        eventsService,
        drawService,
        measureService,
        cutService,
        keyframeService,
        stageService
    };
}
