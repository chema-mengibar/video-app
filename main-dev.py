import webview
from backend.bridge import ApiBridge
from backend.video_stream_server import VideoStreamServer


DEV_SERVER_URL = "http://localhost:5174"


def start_window():
    media_server = VideoStreamServer()
    media_server.start()
    api = ApiBridge(media_server)
    webview.create_window(
        "Motuo | Video app (dev)",
        DEV_SERVER_URL,
        js_api=api,
        width=1400,
        height=900,
        min_size=(1000, 700),
    )
    webview.start(debug=True)


if __name__ == "__main__":
    start_window()
