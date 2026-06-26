import json
import os
from pathlib import Path


class ProjectDataService:
    def __init__(self):
        self.extension = ".json"

    def _clean_path(self, video_path):
        clean_path = str(video_path or "").replace("file:///", "").replace("file://", "")
        if not clean_path or "http://localhost" in clean_path or "blob:" in clean_path:
            raise ValueError("Invalid video path")
        normalized_path = os.path.normpath(clean_path)
        if not os.path.isabs(normalized_path):
            raise ValueError("Video path must be absolute")
        return normalized_path

    def _project_path(self, video_path):
        base, _ = os.path.splitext(self._clean_path(video_path))
        return base + self.extension

    def file_url(self, video_path):
        return Path(self._clean_path(video_path)).as_uri()

    def _empty_data(self, video_path):
        return {
            "video_path": video_path,
            "events": [],
            "items": [],
            "cut": {
                "time_from": 0,
                "time_to": 0,
            },
        }

    def load(self, video_path):
        try:
            clean_path = self._clean_path(video_path)
            project_path = self._project_path(clean_path)
            if not os.path.exists(project_path):
                data = self._empty_data(clean_path)
                self.save(clean_path, data)
                return data

            with open(project_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            return {
                **self._empty_data(clean_path),
                **data,
                "video_path": clean_path,
            }
        except Exception as error:
            print(f"Error loading project data: {error}")
            return self._empty_data(video_path)

    def save(self, video_path, data):
        try:
            clean_path = self._clean_path(video_path)
            project_path = self._project_path(clean_path)
            payload = {
                **self._empty_data(clean_path),
                **(data or {}),
                "video_path": clean_path,
            }

            with open(project_path, "w", encoding="utf-8") as file:
                json.dump(payload, file, indent=2, ensure_ascii=False)

            return {"status": "success", "path": project_path}
        except Exception as error:
            print(f"Error saving project data: {error}")
            return {"status": "error", "message": str(error)}

    def save_events(self, video_path, events):
        data = self.load(video_path)
        data["events"] = events or []
        return self.save(video_path, data)

    def update_event(self, video_path, event_id, patch):
        data = self.load(video_path)
        for event in data["events"]:
            if event.get("id") == event_id:
                event.update(patch or {})
                break
        return self.save(video_path, data)

    def delete_event(self, video_path, event_id):
        data = self.load(video_path)
        data["events"] = [event for event in data["events"] if event.get("id") != event_id]
        return self.save(video_path, data)

    def delete_all_events(self, video_path):
        data = self.load(video_path)
        data["events"] = []
        return self.save(video_path, data)
