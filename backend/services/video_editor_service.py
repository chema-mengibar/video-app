import os
import threading
import time
import uuid
import math
import re

import cv2
import numpy as np


class VideoEditorService:
    def __init__(self):
        self.active_tasks = {}
        self._lock = threading.Lock()

    def export_clip(self, input_path, start_msec, end_msec, freeze_data=None, playback_speed=1.0, quality=90, overlay_data=None):
        try:
            input_path = self._clean_input_path(input_path)
            start_msec = int(start_msec)
            end_msec = int(end_msec)
            playback_speed = max(0.25, min(float(playback_speed or 1), 4))
            quality = max(50, min(int(quality or 90), 100))
            if not os.path.isfile(input_path):
                return {"status": "error", "message": "Input video was not found."}
            if end_msec <= start_msec:
                return {"status": "error", "message": "Cut end must be after cut start."}
        except (TypeError, ValueError):
            return {"status": "error", "message": "Invalid cut export parameters."}

        task_id = f"cut_{uuid.uuid4().hex}"
        output_path = self._generate_output_path(input_path, start_msec, end_msec)
        self._set_task(task_id, {
            "task_id": task_id,
            "status": "processing",
            "path": output_path,
            "progress": 0,
            "message": "Preparing export...",
            "estimated_seconds": None,
        })

        thread = threading.Thread(
            target=self._render_task,
            args=(task_id, input_path, output_path, start_msec, end_msec, freeze_data, playback_speed, quality, overlay_data or {}),
            daemon=True,
        )
        thread.start()
        return {"task_id": task_id, "status": "processing", "path": output_path}

    def get_export_status(self, task_id):
        with self._lock:
            task = self.active_tasks.get(task_id)
            return dict(task) if task else {"status": "error", "message": "Export task was not found."}

    def cancel_export(self, task_id):
        with self._lock:
            task = self.active_tasks.get(task_id)
            if not task:
                return {"status": "error", "message": "Export task was not found."}
            if task.get("status") != "processing":
                return dict(task)
            task["cancel_requested"] = True
            task["message"] = "Canceling export..."
            return dict(task)

    def _render_task(self, task_id, input_path, output_path, start, end, freeze_data, playback_speed, quality, overlay_data):
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            self._set_task(task_id, {"status": "error", "message": f"Could not open video: {input_path}"})
            return

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if width <= 0 or height <= 0:
            cap.release()
            self._set_task(task_id, {"status": "error", "message": "Invalid video dimensions."})
            return

        output_fps = max(1, fps * playback_speed)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, output_fps, (width, height))
        out.set(cv2.VIDEOWRITER_PROP_QUALITY, quality)
        if not out.isOpened():
            cap.release()
            self._set_task(task_id, {"status": "error", "message": f"Could not create output: {output_path}"})
            return

        start_display = start / 1000
        end_display = end / 1000
        total_frames = max(1, int((end_display - start_display) * output_fps))
        processed_frames = 0
        started_at = time.time()

        while processed_frames < total_frames:
            if self._is_cancel_requested(task_id):
                cap.release()
                out.release()
                self._remove_partial_file(output_path)
                self._set_task(task_id, {
                    "status": "canceled",
                    "progress": 0,
                    "message": "Export canceled.",
                    "estimated_seconds": 0,
                    "path": "",
                })
                return

            display_time = start_display + (processed_frames / output_fps)
            source_time = self._display_to_source_time(display_time, overlay_data)
            source_frame = max(0, int(source_time * fps))
            if frame_count > 0:
                source_frame = min(source_frame, max(0, frame_count - 1))
            cap.set(cv2.CAP_PROP_POS_FRAMES, source_frame)

            ret, frame = cap.read()
            if not ret:
                break

            self._draw_overlays(frame, overlay_data, display_time)
            out.write(frame)
            processed_frames += 1
            if processed_frames == 1 or processed_frames % 15 == 0:
                self._update_progress(task_id, processed_frames, total_frames, started_at)

        cap.release()
        out.release()

        if processed_frames <= 0:
            self._remove_partial_file(output_path)
            self._set_task(task_id, {
                "status": "error",
                "message": (
                    "No frames were exported. "
                    f"start={start}ms end={end}ms fps={fps:.3f} "
                    f"total_frames={total_frames} frame_count={frame_count}"
                ),
            })
            return

        self._set_task(task_id, {
            "status": "done",
            "progress": 100,
            "message": "Cut saved.",
            "estimated_seconds": 0,
        })

    def _update_progress(self, task_id, processed_frames, total_frames, started_at):
        progress = min(99, int((processed_frames / total_frames) * 100))
        elapsed = max(0.001, time.time() - started_at)
        estimated_seconds = None
        if progress > 0:
            estimated_seconds = max(0, int((elapsed / progress) * (100 - progress)))
        self._set_task(task_id, {
            "progress": progress,
            "message": f"Saving cut... {progress}%",
            "estimated_seconds": estimated_seconds,
        })

    def _set_task(self, task_id, patch):
        with self._lock:
            task = self.active_tasks.get(task_id, {})
            task.update(patch)
            self.active_tasks[task_id] = task

    def _is_cancel_requested(self, task_id):
        with self._lock:
            return bool(self.active_tasks.get(task_id, {}).get("cancel_requested"))

    def _remove_partial_file(self, output_path):
        try:
            if output_path and os.path.isfile(output_path):
                os.remove(output_path)
        except OSError:
            pass

    def _draw_overlays(self, frame, overlay_data, frame_time):
        items = (overlay_data or {}).get("items") or []
        height, width = frame.shape[:2]
        for item in items:
            if item.get("visible") is False or item.get("type") == "measure-grid":
                continue
            if not self._is_item_visible_at(item, frame_time):
                continue
            item_type = item.get("type")
            if item_type == "chrono":
                self._draw_chrono(frame, item, frame_time)
            elif item_type == "delay":
                self._draw_delay_indicator(frame, item, frame_time)
            elif item_type == "measure-line":
                self._draw_polyline_item(frame, item, width, height, label=True)
            elif item_type in {"player", "ball"}:
                self._draw_marker_item(frame, item, width, height)
            elif item_type == "circle":
                self._draw_circle_item(frame, item, width, height)
            else:
                self._draw_shape_item(frame, item, width, height)

    def _is_item_visible_at(self, item, frame_time):
        start = self._number(item.get("time_from"), 0)
        end = self._number(item.get("time_to"), start)
        return start <= frame_time <= end

    def _draw_shape_item(self, frame, item, width, height):
        color = self._bgr(item.get("color"), (69, 255, 162))
        thickness = max(1, int(self._number(item.get("width"), 2)))
        item_type = item.get("type")
        points = self._points(item.get("points"), width, height)

        if item_type == "free-line" and item.get("path"):
            points = self._path_points(item.get("path"), width, height)
        if len(points) < 2:
            return

        closed = item_type in {"triangle", "square", "polygon"} or bool(item.get("closed"))
        fill_opacity = self._fill_opacity(item)
        if closed:
            polygon = np.array(points, dtype=np.int32)
            if fill_opacity > 0:
                overlay = frame.copy()
                cv2.fillPoly(overlay, [polygon], color, cv2.LINE_AA)
                cv2.addWeighted(overlay, fill_opacity, frame, 1 - fill_opacity, 0, frame)
            cv2.polylines(frame, [polygon], True, color, thickness, cv2.LINE_AA)
        else:
            cv2.polylines(frame, [np.array(points, dtype=np.int32)], False, color, thickness, cv2.LINE_AA)

    def _draw_polyline_item(self, frame, item, width, height, label=False):
        color = self._bgr(item.get("color"), (77, 216, 255))
        thickness = max(1, int(self._number(item.get("width"), 2)))
        points = self._points(item.get("points"), width, height)
        if len(points) < 2:
            return
        cv2.line(frame, points[0], points[1], color, thickness, cv2.LINE_AA)
        if label:
            center = ((points[0][0] + points[1][0]) // 2, (points[0][1] + points[1][1]) // 2)
            label_text = item.get("label") or "Measure"
            cv2.putText(frame, label_text, center, cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 4, cv2.LINE_AA)
            cv2.putText(frame, label_text, center, cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2, cv2.LINE_AA)

    def _draw_marker_item(self, frame, item, width, height):
        point = self._point(item.get("point"), width, height)
        if not point:
            return
        color = self._bgr(item.get("color"), (255, 255, 255))
        half_w = max(3, int(self._number(item.get("width"), 22) / 2))
        half_h = max(3, int(self._number(item.get("length"), 22) / 2))
        cv2.line(frame, (point[0] - half_w, point[1]), (point[0] + half_w, point[1]), color, 2, cv2.LINE_AA)
        cv2.line(frame, (point[0], point[1] - half_h), (point[0], point[1] + half_h), color, 2, cv2.LINE_AA)
        label = str(item.get("label") or "")
        if label:
            cv2.putText(frame, label, (point[0] + 10, point[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

    def _draw_circle_item(self, frame, item, width, height):
        center_data = item.get("center")
        center = self._point(center_data, width, height)
        if not center:
            return
        color = self._bgr(item.get("color"), (69, 255, 162))
        thickness = max(1, int(self._number(item.get("width"), 2)))
        radius_px = max(1, int((self._number(item.get("radius"), 1) / 100) * height))
        fill_opacity = self._fill_opacity(item)
        if item.get("oval"):
            axis_x = radius_px
            axis_y = max(1, int((self._number(item.get("height"), item.get("radius", 1)) / 100) * height))
            angle = self._number(item.get("rotation"), 0)
            if fill_opacity > 0:
                overlay = frame.copy()
                cv2.ellipse(overlay, center, (axis_x, axis_y), angle, 0, 360, color, -1, cv2.LINE_AA)
                cv2.addWeighted(overlay, fill_opacity, frame, 1 - fill_opacity, 0, frame)
            cv2.ellipse(frame, center, (axis_x, axis_y), angle, 0, 360, color, thickness, cv2.LINE_AA)
        else:
            if fill_opacity > 0:
                overlay = frame.copy()
                cv2.circle(overlay, center, radius_px, color, -1, cv2.LINE_AA)
                cv2.addWeighted(overlay, fill_opacity, frame, 1 - fill_opacity, 0, frame)
            cv2.circle(frame, center, radius_px, color, thickness, cv2.LINE_AA)

    def _draw_chrono(self, frame, item, frame_time):
        start = self._number(item.get("time_from"), 0)
        end = self._number(item.get("time_to"), start)
        elapsed = max(0, min(end - start, frame_time - start))
        text = self._format_time(elapsed)
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.65
        thickness = 2
        text_size, baseline = cv2.getTextSize(text, font, scale, thickness)
        padding_x = 10
        padding_y = 8
        x2 = frame.shape[1] - 18
        y1 = 18
        x1 = x2 - text_size[0] - padding_x * 2
        y2 = y1 + text_size[1] + padding_y * 2
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), -1)
        cv2.putText(frame, text, (x1 + padding_x, y2 - padding_y - baseline // 2), font, scale, (255, 255, 255), thickness, cv2.LINE_AA)

    def _draw_delay_indicator(self, frame, item, frame_time):
        start = self._number(item.get("time_from"), 0)
        duration = self._number(item.get("duration"), 0)
        if not (start <= frame_time <= start + duration):
            return
        height = frame.shape[0]
        x = 18
        y = height - 52
        cv2.rectangle(frame, (x - 8, y - 8), (x + 28, y + 34), (0, 0, 0), -1)
        overlay = frame.copy()
        cv2.rectangle(overlay, (x - 8, y - 8), (x + 28, y + 34), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)
        cv2.rectangle(frame, (x, y), (x + 5, y + 24), (0, 0, 0), -1)
        cv2.rectangle(frame, (x + 13, y), (x + 18, y + 24), (0, 0, 0), -1)

    def _display_to_source_time(self, display_time, overlay_data):
        accumulated_delay = 0
        delay_items = sorted(
            [
                item for item in (overlay_data or {}).get("items", [])
                if item.get("type") == "delay" and item.get("visible") is not False
            ],
            key=lambda item: self._number(item.get("time_from"), 0),
        )
        for item in delay_items:
            start = max(0, self._number(item.get("time_from"), 0))
            duration = max(0, self._number(item.get("duration"), 0))
            if display_time < start:
                break
            if display_time <= start + duration:
                return max(0, start - accumulated_delay)
            accumulated_delay += duration
        return max(0, display_time - accumulated_delay)

    def _points(self, points, width, height):
        return [point for point in (self._point(candidate, width, height) for candidate in points or []) if point]

    def _point(self, point, width, height):
        if not isinstance(point, dict):
            return None
        return (int((self._number(point.get("x"), 0) / 100) * width), int((self._number(point.get("y"), 0) / 100) * height))

    def _path_points(self, path, width, height):
        matches = re.findall(r"[ML]\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)", str(path or ""))
        return [(int((float(x) / 100) * width), int((float(y) / 100) * height)) for x, y in matches]

    def _bgr(self, value, fallback):
        text = str(value or "").lstrip("#")
        if len(text) != 6:
            return fallback
        try:
            red = int(text[0:2], 16)
            green = int(text[2:4], 16)
            blue = int(text[4:6], 16)
            return (blue, green, red)
        except ValueError:
            return fallback

    def _fill_opacity(self, item):
        item_type = item.get("type")
        if item_type == "polyline" and not item.get("closed"):
            return 0
        if item_type in {"triangle", "square", "polygon", "circle"} or (item_type == "polyline" and item.get("closed")):
            fallback = self._number(item.get("opacity"), 0)
            return max(0, min(self._number(item.get("fillOpacity"), fallback), 1))
        return 0

    def _number(self, value, fallback):
        try:
            parsed = float(value)
            return parsed if math.isfinite(parsed) else fallback
        except (TypeError, ValueError):
            return fallback

    def _format_time(self, value):
        minutes = int(value // 60)
        seconds = int(value % 60)
        millis = int((value % 1) * 1000)
        return f"00:{minutes:02d}:{seconds:02d},{millis:03d}"

    def _generate_output_path(self, input_path, start_msec, end_msec):
        base, _ = os.path.splitext(input_path)
        return f"{base}_clip_{start_msec}_{end_msec}.mp4"

    def _clean_input_path(self, input_path):
        clean_path = str(input_path or "").replace("file:///", "").replace("file://", "")
        if clean_path.startswith("http://") or clean_path.startswith("https://") or clean_path.startswith("blob:"):
            raise ValueError("Input path must be a local file")
        return os.path.abspath(clean_path)
