from PySide6.QtCore import QObject, Signal, Slot, QThread
import os
import cv2
import numpy as np
from adapters.opencv_video_processor import OpenCVVideoProcessor


class ClipSaveThread(QThread):
    finished_signal = Signal(str)  # Ruta del clip guardado
    error_signal = Signal(str)     # Mensaje de error

    def __init__(self, video_path, start_msec, end_msec, output_filename, freeze_msec: int, freeze_duration: int, parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.start_msec = start_msec
        self.end_msec = end_msec
        self.output_filename = output_filename
        self.freeze_msec = freeze_msec
        self.freeze_duration = freeze_duration  # en segundos, int

    def run(self):
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            self.error_signal.emit(f"No se pudo abrir el video: {self.video_path}")
            return

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.output_filename, fourcc, fps, (width, height))

        start_frame = int(self.start_msec / 1000.0 * fps)
        end_frame = int(self.end_msec / 1000.0 * fps)

        # Solo hacemos freeze si freeze_msec > 0 y freeze_duration > 0
 
        freeze_duration_frames = int((self.freeze_duration or 0) * fps)
        freeze_frame_index = int((self.freeze_msec or 0) / 1000.0 * fps) if (self.freeze_msec or 0) > 0 else None

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        current_frame = start_frame
        frozen_frame = None

        while current_frame <= end_frame:
            ret, frame = cap.read()
            if not ret:
                break

            if freeze_frame_index and current_frame == freeze_frame_index and freeze_duration_frames > 0:
                frozen_frame = frame.copy()

                # --- Dibujar icono de pausa ---
                rect_width = 10
                rect_height = 30
                padding = 5
                # Primer rectángulo
                top_left = (padding, padding)
                bottom_right = (padding + rect_width, padding + rect_height)
                cv2.rectangle(frozen_frame, top_left, bottom_right, (255, 255, 255), -1)
                # Segundo rectángulo
                top_left2 = (padding + rect_width + 5, padding)
                bottom_right2 = (padding + 2*rect_width + 5, padding + rect_height)
                cv2.rectangle(frozen_frame, top_left2, bottom_right2, (255, 255, 255), -1)

                # Escribimos el frame congelado varias veces
                for _ in range(freeze_duration_frames):
                    out.write(frozen_frame)

            # Solo escribimos frames normales si no es el frame del freeze
            if not (freeze_frame_index and current_frame == freeze_frame_index):
                out.write(frame)

            current_frame += 1

        cap.release()
        out.release()
        self.finished_signal.emit(self.output_filename)


class VideoService(QObject):
    frame_ready_signal = Signal(object)          # Emite frame (numpy array)
    time_updated_signal = Signal(int)           # Emite tiempo actual en msec
    video_loaded_signal = Signal(bool, int, str) # éxito, duración, path del video

    def __init__(self, processor: OpenCVVideoProcessor, parent=None):
        super().__init__(parent)

        self.processor = processor
        self.current_time_msec = 0
        self.duration_msec = 0
        self.video_path = None
        self.is_playing = False
        self.is_slider_down = False

        self.video_directory = None
        self.video_filename_base = None

        self._clip_thread = None

        self._connect_processor_signals()

    def _connect_processor_signals(self):
        self.processor.frame_ready_signal.connect(self.frame_ready_signal)
        self.processor.time_updated_signal.connect(self._handle_time_update)
        self.processor.video_loaded_signal.connect(self._handle_video_loaded)

    @staticmethod
    def format_time(msec: int, char=':') -> str:
        msec = int(msec)
        milliseconds = msec % 1000
        total_seconds = msec // 1000
        seconds = total_seconds % 60
        minutes = (total_seconds // 60) % 60
        hours = total_seconds // 3600
        if hours > 0:
            return f"{hours:02d}{char}{minutes:02d}{char}{seconds:02d}{char}{milliseconds:03d}"
        return f"{minutes:02d}{char}{seconds:02d}{char}{milliseconds:03d}"

    @Slot(int)
    def _handle_time_update(self, current_msec):
        self.current_time_msec = current_msec
        if not self.is_slider_down:
            self.time_updated_signal.emit(current_msec)

    @Slot(bool, int, str)
    def _handle_video_loaded(self, success: bool, duration_msec: int, video_path: str):
        self.duration_msec = duration_msec
        self.video_path = video_path
        if success:
            self.video_directory = os.path.dirname(video_path)
            self.video_filename_base = os.path.splitext(os.path.basename(video_path))[0]
            self.toggle_play_pause(False)
        self.video_loaded_signal.emit(success, duration_msec, video_path)

    # --- API Pública ---
    def is_video_loaded(self) -> bool:
        return self.processor.is_loaded

    def get_current_time(self) -> int:
        return self.current_time_msec

    def load_video_file(self, path: str):
        self.video_path = path
        self.processor.load_video(path)
        self.toggle_play_pause(False)   # pausa
        self.processor.seek(0)          # ir al primer frame

    def toggle_play_pause(self, play: bool):
        if self.processor.is_loaded:
            self.is_playing = play
            self.processor.set_playing(play)

    def seek(self, msec: int):
        self.is_slider_down = False
        self.processor.seek(msec)
        self.time_updated_signal.emit(msec)

    def slider_moved(self):
        self.is_slider_down = True

    def set_quality(self, factor: float):
        self.processor.set_quality(factor)

    def stop_service(self):
        self.processor.stop_processing()

    @Slot()
    def save_screenshot(self):
        frame = self.processor.get_last_frame()
        current_msec = self.processor.get_current_time_msec()
        if frame is None or not self.processor.is_loaded:
            print("VideoService: No hay frame disponible o video no cargado.")
            return
        if not (self.video_directory and self.video_filename_base):
            print("VideoService: ERROR. Video no configurado.")
            return

        time_str = self.format_time(current_msec, '_')
        screenshot_dir = os.path.join(self.video_directory, f"{self.video_filename_base}__screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        filepath = os.path.join(screenshot_dir, f"capture_{time_str}.jpeg")

        try:
            success = cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            if success:
                print(f"VideoService: Captura guardada en: {filepath}")
            else:
                print(f"VideoService: ERROR al guardar captura en: {filepath}")
        except Exception as e:
            print(f"VideoService: EXCEPCIÓN al guardar captura: {e}")

    @Slot(int, int, int, int, str)
    def save_video_clip(self, start_msec: int, end_msec: int, freeze_msec: int = 0, freeze_duration: int = 0, output_filename: str = None):
        """
        Guarda un clip del video. Si freeze_msec y freeze_duration son >0,
        congela ese frame durante freeze_duration segundos y dibuja un icono de pausa.
        """
        if not self.processor.is_loaded or self.video_path is None:
            print("VideoService: No hay video cargado para cortar.")
            return
        if end_msec <= start_msec:
            print("VideoService: Tiempo final debe ser mayor que inicial.")
            return

        clips_dir = os.path.join(self.video_directory, f"{self.video_filename_base}__clips")
        os.makedirs(clips_dir, exist_ok=True)

        if output_filename is None:
            output_filename = os.path.join(
                clips_dir,
                f"clip__{self.video_filename_base}__{start_msec}_{end_msec}.mp4"
            )

        self._clip_thread = ClipSaveThread(
            self.video_path,
            start_msec,
            end_msec,
            output_filename,
            freeze_msec,
            freeze_duration
        )
        self._clip_thread.finished_signal.connect(lambda path: print(f"VideoService: Clip guardado en {path}"))
        self._clip_thread.error_signal.connect(lambda msg: print(f"VideoService: Error al guardar clip: {msg}"))
        self._clip_thread.start()
