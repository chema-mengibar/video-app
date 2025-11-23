# src/app/adapters/opencv_video_processor.py

import cv2
import time
import os
from PySide6.QtCore import QThread, Signal, Slot, QObject, QMutex


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
            self.thread.stop()  # Detiene el hilo de forma segura


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
        self.running = True  # controla el while del hilo
        self.frame_rate = 30.0
        self.duration_msec = 0
        self.frame_skip_factor = 1.0 
        self.mutex = QMutex()

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
                
                for _ in range(skip_frames):
                    ret, frame = self.cap.read()
                    if not ret:
                        self.playing = False
                        self.cap.set(cv2.CAP_PROP_POS_MSEC, 0) 
                        break
                    
                current_msec = int(self.cap.get(cv2.CAP_PROP_POS_MSEC))
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

    # --- Nuevo método agregado ---
    def stop(self):
        """
        Detiene el hilo de forma segura.
        Llamar desde stop_processing() antes de cerrar la ventana.
        """
        self.running = False
        self.quit()
        self.wait()
