import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, urlparse


class VideoStreamServer:
    def __init__(self, host="127.0.0.1", port=0):
        self.host = host
        self._httpd = ThreadingHTTPServer((host, port), _VideoRequestHandler)
        self._httpd.owner = self
        self.port = self._httpd.server_address[1]
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)

    def start(self):
        self._thread.start()

    def url_for(self, video_path):
        clean_path = os.path.abspath(video_path)
        return f"http://{self.host}:{self.port}/video?path={quote(clean_path)}"

    def shutdown(self):
        self._httpd.shutdown()


class _VideoRequestHandler(BaseHTTPRequestHandler):
    chunk_size = 1024 * 1024

    def log_message(self, format, *args):
        return

    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path != "/video":
            self.send_error(404)
            return

        query = parse_qs(parsed_url.query)
        raw_path = query.get("path", [""])[0]
        video_path = os.path.abspath(raw_path)

        if not os.path.isfile(video_path):
            self.send_error(404)
            return

        file_size = os.path.getsize(video_path)
        start, end = self._range_bounds(file_size)
        content_length = end - start + 1

        self.send_response(206 if self.headers.get("Range") else 200)
        self.send_header("Content-Type", self._content_type(video_path))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Range")
        self.send_header("Access-Control-Expose-Headers", "Content-Length, Content-Range, Accept-Ranges")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(content_length))
        if self.headers.get("Range"):
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.end_headers()

        with open(video_path, "rb") as file:
            file.seek(start)
            remaining = content_length
            while remaining > 0:
                data = file.read(min(self.chunk_size, remaining))
                if not data:
                    break
                try:
                    self.wfile.write(data)
                except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                    break
                remaining -= len(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Range")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.end_headers()

    def _range_bounds(self, file_size):
        range_header = self.headers.get("Range", "")
        if not range_header.startswith("bytes="):
            return 0, file_size - 1

        range_value = range_header.removeprefix("bytes=").split(",", 1)[0]
        start_value, _, end_value = range_value.partition("-")
        try:
            start = int(start_value) if start_value else 0
            end = int(end_value) if end_value else file_size - 1
        except ValueError:
            return 0, file_size - 1

        start = max(0, min(start, file_size - 1))
        end = max(start, min(end, file_size - 1))
        return start, end

    def _content_type(self, video_path):
        extension = os.path.splitext(video_path)[1].lower()
        return {
            ".mp4": "video/mp4",
            ".mov": "video/quicktime",
            ".webm": "video/webm",
            ".mkv": "video/x-matroska",
            ".avi": "video/x-msvideo",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
        }.get(extension, "application/octet-stream")
