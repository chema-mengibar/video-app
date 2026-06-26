from .services.bookmark_service import BookmarkService
from .services.draw_service import DrawService
from .services.project_data_service import ProjectDataService
from .services.video_editor_service import VideoEditorService
import os
import webview


class ApiBridge:
    def __init__(self, media_server=None):
        self.editor = VideoEditorService()
        self.bookmarks = BookmarkService()
        self.draw = DrawService(self.editor)
        self.project_data = ProjectDataService()
        self.media_server = media_server

    def load_project(self, video_path):
        return self.project_data.load(video_path)

    def save_project(self, params):
        return self.project_data.save(params.get("video_path"), params.get("data"))

    def choose_video_file(self):
        return self.choose_media_file()

    def choose_media_file(self):
        window = webview.windows[0] if webview.windows else None
        if not window:
            return None

        paths = window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=(
                "Media files (*.mp4;*.mov;*.avi;*.mkv;*.webm;*.png;*.jpg;*.jpeg;*.webp;*.gif;*.bmp)",
                "Video files (*.mp4;*.mov;*.avi;*.mkv;*.webm)",
                "Image files (*.png;*.jpg;*.jpeg;*.webp;*.gif;*.bmp)",
                "All files (*.*)",
            ),
        )
        if not paths:
            return None

        video_path = paths[0]
        return {
            "path": video_path,
            "url": self.get_video_url(video_path),
            "media_type": self._media_type(video_path),
        }

    def _media_type(self, path):
        extension = str(path or "").lower().rsplit(".", 1)[-1]
        return "image" if extension in {"png", "jpg", "jpeg", "webp", "gif", "bmp"} else "video"

    def get_video_url(self, video_path):
        if not self.media_server:
            return None
        return self.media_server.url_for(video_path)

    def save_events(self, params):
        return self.project_data.save_events(params.get("video_path"), params.get("events"))

    def update_event(self, params):
        return self.project_data.update_event(
            params.get("video_path"),
            params.get("id"),
            params.get("patch"),
        )

    def delete_event(self, params):
        return self.project_data.delete_event(params.get("video_path"), params.get("id"))

    def delete_all_events(self, video_path):
        return self.project_data.delete_all_events(video_path)

    def export_clip(self, params):
        params = params or {}
        return self.editor.export_clip(
            params.get("video_path"),
            params.get("start"),
            params.get("end"),
            playback_speed=params.get("playback_speed", 1),
            quality=params.get("quality", 90),
            overlay_data=params.get("overlay_data"),
        )

    def get_export_status(self, task_id):
        return self.editor.get_export_status(task_id)

    def cancel_export(self, task_id):
        return self.editor.cancel_export(task_id)

    def open_path_in_explorer(self, path):
        clean_path = os.path.abspath(str(path or ""))
        target = clean_path if os.path.isdir(clean_path) else os.path.dirname(clean_path)
        if not target or not os.path.exists(target):
            return {"status": "error", "message": "Path was not found."}
        os.startfile(target)
        return {"status": "ok"}

    def get_bookmarks(self, video_path):
        return self.bookmarks.get_list(video_path)

    def save_bookmarks(self, params):
        return self.bookmarks.save_marks(params["video_path"], params["marks"])

    def save_drawings(self, params):
        return self.draw.save_drawing_data(params["video_path"], params["drawing_data"])

    def get_drawings(self, video_path):
        return self.draw.get_drawings(video_path)
