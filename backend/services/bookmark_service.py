import json
import os

class BookmarkService:
    def __init__(self):
        self.extension = ".bookmarks.json"

    def _get_json_path(self, video_path):
        # Limpiar ruta de protocolos de navegador si existen
        clean_path = video_path.replace('file:///', '').replace('file://', '')
        # Si sigue siendo un blob o ruta inválida, fallar preventivamente
        if "http://localhost" in clean_path or "blob:" in clean_path:
            raise ValueError("Ruta de video inválida para guardar marcadores.")
        return os.path.normpath(clean_path) + self.extension

    def get_list(self, video_path):
        try:
            path = self._get_json_path(video_path)
            if not os.path.exists(path): return []
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando marcadores: {e}")
            return []

    def save_marks(self, video_path, marks_list):
        try:
            path = self._get_json_path(video_path)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(marks_list, f, indent=4, ensure_ascii=False)
            return {"status": "success"}
        except Exception as e:
            print(f"Error guardando marcadores: {e}")
            return {"status": "error", "message": str(e)}