import json
import os


class DrawService:
    def __init__(self, editor_service):
        self.editor_service = editor_service
        self.extension = ".drawings.json"

    def _drawing_path(self, video_path):
        clean_path = str(video_path or "").replace("file:///", "").replace("file://", "")
        if not clean_path or "http://localhost" in clean_path or "blob:" in clean_path:
            raise ValueError("Invalid video path")
        return os.path.normpath(clean_path) + self.extension

    def save_drawing_data(self, video_path, drawing_data):
        try:
            path = self._drawing_path(video_path)
            with open(path, "w", encoding="utf-8") as file:
                json.dump(drawing_data or [], file, indent=2, ensure_ascii=False)
            return {"status": "success", "path": path}
        except Exception as error:
            return {"status": "error", "message": str(error)}

    def get_drawings(self, video_path):
        try:
            path = self._drawing_path(video_path)
            if not os.path.exists(path):
                return []
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return []

    def export_video_with_drawings(self, video_path, drawing_id):
        return self.editor_service.export_clip(video_path, 0, 0, {"drawing_id": drawing_id})
