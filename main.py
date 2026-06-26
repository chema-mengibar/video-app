from pathlib import Path

import webview
from backend.bridge import ApiBridge
from backend.video_stream_server import VideoStreamServer


ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIST_INDEX = ROOT_DIR / "frontend" / "dist" / "index.html"


def frontend_url():
    if not FRONTEND_DIST_INDEX.is_file():
        raise FileNotFoundError(
            f"Frontend build not found: {FRONTEND_DIST_INDEX}. "
            "Run `npm run build` in the frontend folder first."
        )

    return FRONTEND_DIST_INDEX.as_uri()


def start_window():
    media_server = VideoStreamServer()
    media_server.start()
    api = ApiBridge(media_server)
    webview.create_window(
        "Motuo | Video app",
        frontend_url(),
        js_api=api,
        width=1400,
        height=900,
        min_size=(1000, 700),
    )
    webview.start(debug=False)


if __name__ == "__main__":
    start_window()
