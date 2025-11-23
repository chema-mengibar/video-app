# src/app/adapters/opencv_video_processor.py

import cv2
import time
import os
from PySide6.QtCore import QThread, Signal, Slot, QObject, QMutex
from typing import Optional
import numpy as np # Importar numpy para tipado de frames

class VideoThread(QThread):
    """
    Hilo dedicado a manejar el loop de lectura de frames de OpenCV.
    """
    frame_ready = Signal(object)
    time_updated = Signal(int)
    video_loaded_info = Signal(bool, int, str) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cap = None 
        self.path = None
        self.playing = False
        self.running = True 
        self.frame_rate = 30.0
        self.duration_msec = 0
        self.frame_skip_factor = 1.0 
        self.mutex = QMutex()
        
        # --- ALMACENAMIENTO DE DATOS PARA SCREENSHOT ---
        self._last_frame: Optional[np.ndarray] = None
        self._current_msec: int = 0
        # ---------------------------------------------

    @Slot(str)
    def load_video(self, path: str):
        self.path = path
        
        self.mutex.lock()
        try:
            if self.cap and self.cap.isOpened():
                self.cap.release()
                
            self.cap = cv2.VideoCapture(path)
            
            success = False
            if self.cap.isOpened():
                success = True
                self.frame_rate = self.cap.get(cv2.CAP_PROP_FPS)
                frame_count = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
                self.duration_msec = int((frame_count / self.frame_rate) * 1000)
                
            self.video_loaded_info.emit(success, self.duration_msec if success else 0, path)
        finally:
            self.mutex.unlock()


    @Slot(bool)
    def set_playing(self, play: bool):
        self.playing = play

    @Slot(int)
    def seek(self, msec: int):
        if self.cap and self.cap.isOpened():
            self.mutex.lock()
            try:
                self.cap.set(cv2.CAP_PROP_POS_MSEC, msec)
            finally:
                self.mutex.unlock()
            
            # Forzar lectura y emisión en la nueva posición
            self.read_and_emit_frame() 
            self.time_updated.emit(msec)

    @Slot(float)
    def set_quality(self, factor: float):
        self.frame_skip_factor = factor

    def read_and_emit_frame(self):
        ret = False
        frame = None
        current_msec = 0
        
        self.mutex.lock()
        try:
            if self.cap and self.cap.isOpened():
                skip_frames = int(1 / self.frame_skip_factor) if self.frame_skip_factor > 0 else 1
                
                # Leer N frames para simular el skip
                for _ in range(skip_frames):
                    ret, frame = self.cap.read()
                    if not ret:
                        self.playing = False
                        self.cap.set(cv2.CAP_PROP_POS_MSEC, 0) 
                        break
                    
                if ret:
                    current_msec = int(self.cap.get(cv2.CAP_PROP_POS_MSEC))
                    # --- ALMACENAR DATOS ---
                    self._last_frame = frame
                    self._current_msec = current_msec
                    # -----------------------
                    
        finally:
            self.mutex.unlock()
        
        if ret:
            self.frame_ready.emit(frame)
            self.time_updated.emit(current_msec)
            return True
        elif self.cap and not ret: 
            self.time_updated.emit(0) 
        return False

    def run(self):
        while self.running:
            if self.cap and self.cap.isOpened() and self.playing:
                self.read_and_emit_frame() 
                
                if self.frame_rate > 0:
                    skip_frames = int(1 / self.frame_skip_factor) if self.frame_skip_factor > 0 else 1
                    delay = (1.0 / self.frame_rate) * skip_frames
                else:
                    delay = 0.033 

                time.sleep(delay)
            else:
                time.sleep(0.01) 
                
        if self.cap:
            self.cap.release()

    def stop(self):
        """
        Detiene el hilo de forma segura.
        """
        self.running = False
        self.quit()
        self.wait()

    # --- NUEVOS MÉTODOS DE ACCESO SEGURO ---
    
    def get_last_frame(self) -> Optional[np.ndarray]:
        """Retorna el último frame almacenado (usado para screenshots)."""
        # Se requiere bloqueo porque este método puede ser llamado desde otro hilo (VideoService)
        self.mutex.lock()
        frame_copy = self._last_frame.copy() if self._last_frame is not None else None
        self.mutex.unlock()
        return frame_copy

    def get_current_time_msec(self) -> int:
        """Retorna el tiempo actual almacenado (usado para nombrar screenshots)."""
        self.mutex.lock()
        current_time = self._current_msec
        self.mutex.unlock()
        return current_time
    # ------------------------------------
    
    
class OpenCVVideoProcessor(QObject):
    """
    Adaptador de Procesamiento de Video usando OpenCV.
    Maneja la interacción con VideoThread.
    """
    
    frame_ready_signal = Signal(object) 
    time_updated_signal = Signal(int) 
    video_loaded_signal = Signal(bool, int, str) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_loaded = False
        self.current_quality = 1.0 
        
        self.thread = VideoThread()
        self.thread.frame_ready.connect(self.frame_ready_signal)
        self.thread.time_updated.connect(self.time_updated_signal)
        self.thread.video_loaded_info.connect(self.video_loaded_signal)
        
        self.thread.start() 

    # --- API pública (Usada por VideoService) ---

    def load_video(self, path: str):
        if not os.path.exists(path):
            self.video_loaded_signal.emit(False, 0, path)
            self.is_loaded = False
            return

        self.thread.load_video(path)
        self.is_loaded = True
        
    def set_playing(self, play: bool):
        self.thread.set_playing(play)

    def seek(self, msec: int):
        self.thread.seek(msec)

    def set_quality(self, factor: float):
        self.current_quality = factor
        self.thread.set_quality(factor)
        
    def stop_processing(self):
        if self.thread.isRunning():
            self.thread.stop() 

    # --- NUEVOS MÉTODOS REQUERIDOS POR VideoService ---
    
    def get_last_frame(self) -> Optional[np.ndarray]:
        """Delega la obtención del último frame al hilo de procesamiento."""
        return self.thread.get_last_frame()

    def get_current_time_msec(self) -> int:
        """Delega la obtención del tiempo actual al hilo de procesamiento."""
        return self.thread.get_current_time_msec()
