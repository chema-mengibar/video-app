# src/app/adapters/opencv_video_processor.py

import cv2
import os
from PySide6.QtCore import QThread, Signal, Slot, QObject, QMutex, Qt, QMetaObject, Q_ARG
from typing import Optional
import numpy as np
import time

class VideoThread(QThread):
    frame_ready = Signal(object)
    time_updated = Signal(int)
    video_loaded_info = Signal(bool, int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cap: Optional[cv2.VideoCapture] = None
        self.path: Optional[str] = None
        self.playing = False
        self.running = True
        self.frame_rate = 30.0
        self.duration_msec = 0
        self.frame_skip_factor = 1.0
        self.mutex = QMutex()

        self._last_frame: Optional[np.ndarray] = None
        self._current_msec: int = 0

    @Slot(str)
    def load_video(self, path: str):
        """Carga un video y emite información de carga."""
        if not os.path.exists(path):
            self.video_loaded_info.emit(False, 0, path)
            return

        self.path = path
        self.mutex.lock()
        try:
            if self.cap and self.cap.isOpened():
                self.cap.release()
            self.cap = cv2.VideoCapture(path)
            if self.cap.isOpened():
                self.frame_rate = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
                frame_count = self.cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
                self.duration_msec = int((frame_count / self.frame_rate) * 1000)
                self.video_loaded_info.emit(True, self.duration_msec, path)
            else:
                self.video_loaded_info.emit(False, 0, path)
        finally:
            self.mutex.unlock()

    @Slot(bool)
    def set_playing(self, play: bool):
        """Inicia o pausa la reproducción."""
        self.playing = play

    @Slot(int)
    def seek(self, msec: int):
        """
        Actualiza la posición del video.
        No bloquea la UI: solo ajusta la posición y deja que run() emita el frame.
        """
        self.mutex.lock()
        try:
            if self.cap:
                self.cap.set(cv2.CAP_PROP_POS_MSEC, msec)
                self._current_msec = msec
        finally:
            self.mutex.unlock()

    @Slot(float)
    def set_quality(self, factor: float):
        """Ajusta el factor de saltos de frames para control de calidad."""
        self.frame_skip_factor = max(0.1, factor)

    def read_frame(self) -> bool:
        """Lee un solo frame y emite señales, seguro para hilos."""
        if not (self.cap and self.cap.isOpened()):
            return False

        self.mutex.lock()
        try:
            skip_frames = max(1, int(1 / self.frame_skip_factor))
            frame = None
            ret = False
            for _ in range(skip_frames):
                ret, frame = self.cap.read()
                if not ret:
                    # Fin de video: reiniciar desde 0
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self.cap.read()
                    break

            if ret:
                self._last_frame = frame.copy()
                self._current_msec = int(self.cap.get(cv2.CAP_PROP_POS_MSEC))
        finally:
            self.mutex.unlock()

        if ret:
            self.frame_ready.emit(frame)
            self.time_updated.emit(self._current_msec)
        return ret

    @Slot(int)
    def seek_in_thread(self, msec: int):
        """
        Método seguro para leer un frame al hacer seek.
        Llamar desde QMetaObject.invokeMethod para no bloquear UI.
        """
        if not self.cap:
            return
        self.mutex.lock()
        try:
            self.cap.set(cv2.CAP_PROP_POS_MSEC, msec)
            ret, frame = self.cap.read()
            if ret:
                self._last_frame = frame.copy()
                self._current_msec = int(self.cap.get(cv2.CAP_PROP_POS_MSEC))
        finally:
            self.mutex.unlock()

        if ret:
            self.frame_ready.emit(frame)
            self.time_updated.emit(self._current_msec)

    def run(self):
        """Bucle principal del hilo de video."""
        while self.running:
            if self.cap and self.cap.isOpened() and self.playing:
                start = time.perf_counter()
                self.read_frame()
                elapsed = time.perf_counter() - start
                delay = max(0, (1.0 / self.frame_rate) - elapsed)
                self.msleep(int(delay * 1000))
            else:
                self.msleep(10)

        if self.cap:
            self.cap.release()

    def stop(self):
        """Detiene el hilo."""
        self.running = False
        self.quit()
        self.wait()

    def get_last_frame(self) -> Optional[np.ndarray]:
        """Devuelve una copia del último frame leído."""
        self.mutex.lock()
        frame = self._last_frame.copy() if self._last_frame is not None else None
        self.mutex.unlock()
        return frame

    def get_current_time_msec(self) -> int:
        """Devuelve el tiempo actual en msec."""
        self.mutex.lock()
        t = self._current_msec
        self.mutex.unlock()
        return t


class OpenCVVideoProcessor(QObject):
    frame_ready_signal = Signal(object)
    time_updated_signal = Signal(int)
    video_loaded_signal = Signal(bool, int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = VideoThread()
        self.thread.frame_ready.connect(self.frame_ready_signal)
        self.thread.time_updated.connect(self.time_updated_signal)
        self.thread.video_loaded_info.connect(self.video_loaded_signal)

        self.is_loaded = False
        self.video_path = None

        self.thread.start()

    def load_video(self, path: str):
        if not os.path.exists(path):
            self.video_loaded_signal.emit(False, 0, path)
            self.is_loaded = False
            return

        self.is_loaded = True
        self.video_path = path
        self.thread.load_video(path)

    def set_playing(self, play: bool):
        self.thread.set_playing(play)

    def seek(self, msec: int):
        """Busca un tiempo específico y lee el frame en el hilo."""
        QMetaObject.invokeMethod(self.thread, "seek_in_thread", Qt.QueuedConnection, Q_ARG(int, msec))

    def set_quality(self, factor: float):
        self.thread.set_quality(factor)

    def stop_processing(self):
        if self.thread.isRunning():
            self.thread.stop()

    def get_last_frame(self):
        return self.thread.get_last_frame()

    def get_current_time_msec(self):
        return self.thread.get_current_time_msec()
