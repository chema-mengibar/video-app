# src/app/adapters/opencv_video_processor.py

import cv2
import time
import os
from PySide6.QtCore import QObject, QThread, Signal, QMutex, QMutexLocker, QWaitCondition
from services.video_service import VideoProcessorInterface # Importar la interfaz

# ----------------------------------------------------------------------
# CLASE TRABAJADORA (Worker): Bucle de reproducción en el hilo secundario
# ----------------------------------------------------------------------
class OpenCVVideoWorker(QObject):
    
    def __init__(self, processor: VideoProcessorInterface, parent=None):
        super().__init__(parent)
        self.processor = processor # Referencia al procesador para acceder a metadatos
        self.cap = None
        self.is_playing = False
        self.exit_flag = False
        
        # Sincronización
        self.mutex = QMutex()
        self.wait_condition = QWaitCondition() 
        self.current_scale_factor = 1.0

    def run(self):
        """Bucle principal de reproducción/extracción de frames."""
        print("Worker thread started.")
        while not self.exit_flag:
            
            with QMutexLocker(self.mutex):
                # Esperar si está pausado o no hay video
                if not self.processor.is_video_loaded() or not self.is_playing:
                    self.wait_condition.wait(self.mutex)
                    
            if self.exit_flag:
                break
                
            # Leer el frame
            ret, frame = self.cap.read() if self.cap else (False, None)
            
            if ret:
                current_msec = self.cap.get(cv2.CAP_PROP_POS_MSEC)
                
                # Emitir frame y tiempo ANTES de dormir (para una UI más reactiva)
                self.processor.frame_ready.emit(frame)
                self.processor.time_updated.emit(int(current_msec))
                
                # Calcular el tiempo de espera
                delay = 1 / self.processor.get_metadata()['fps']
                # Ajuste de escala para alto rendimiento
                scaled_delay = delay * self.current_scale_factor
                
                time.sleep(scaled_delay)
            else:
                # Si llegamos al final, pausar
                with QMutexLocker(self.mutex):
                    self.is_playing = False
                self.processor.time_updated.emit(self.processor.get_metadata()['duration']) # Posicionar al final
        
        if self.cap:
            self.cap.release()
        print("Worker thread finished.")

# ----------------------------------------------------------------------
# ADAPTADOR: Implementa la interfaz para el Servicio
# ----------------------------------------------------------------------
class OpenCVVideoProcessor(VideoProcessorInterface):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = OpenCVVideoWorker(self)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start() # Iniciar el hilo del worker
        
        # Metadatos
        self._is_loaded = False
        self._current_time_msec = 0
        self._metadata = {
            'path': None, 
            'duration': 0, 
            'fps': 30.0, 
            'width': 0, 
            'height': 0,
            'directory': None
        }

    # --- Implementación de la Interfaz ---
    
    def open(self, path: str) -> bool:
        """Abre el archivo de video y lee metadatos."""
        with QMutexLocker(self.worker.mutex):
            if self._is_loaded:
                self.worker.cap.release()

            cap = cv2.VideoCapture(path)
            if not cap.isOpened():
                self.video_loaded.emit(False, 0, "")
                self._is_loaded = False
                return False

            # Cargar Metadatos
            self._metadata['path'] = path
            self._metadata['duration'] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS) * 1000)
            self._metadata['fps'] = cap.get(cv2.CAP_PROP_FPS)
            self._metadata['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self._metadata['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self._metadata['directory'] = os.path.dirname(path)
            
            self.worker.cap = cap
            self._is_loaded = True
            self.worker.is_playing = False # Inicia pausado
            self._current_time_msec = 0
            
            self.video_loaded.emit(True, self._metadata['duration'], self._metadata['directory'])
            return True

    def run_playback_loop(self):
        # El hilo ya se inició en __init__
        pass 

    def toggle_play_pause(self, play: bool):
        with QMutexLocker(self.worker.mutex):
            self.worker.is_playing = play
            if play:
                self.worker.wait_condition.wakeAll()
    
    def seek(self, msec: int):
        self.slider_moved(msec)
        
    def slider_moved(self, msec: int):
        with QMutexLocker(self.worker.mutex):
            if self.worker.cap:
                self.worker.cap.set(cv2.CAP_PROP_POS_MSEC, msec)
                # Forzar la lectura de un frame para actualizar la UI inmediatamente
                ret, frame = self.worker.cap.read()
                if ret:
                    self.frame_ready.emit(frame)
                    self._current_time_msec = msec
                    self.time_updated.emit(msec)
                else:
                    # En caso de error, volver a la posición deseada
                    self.worker.cap.set(cv2.CAP_PROP_POS_MSEC, msec)

    def slider_released(self):
        # En este diseño, slider_moved ya maneja la lógica de seek. No se requiere acción adicional.
        pass 

    def set_scale_factor(self, scale: float):
        self.worker.current_scale_factor = scale

    def stop_thread(self):
        with QMutexLocker(self.worker.mutex):
            self.worker.exit_flag = True
            self.worker.wait_condition.wakeAll()
        self.worker_thread.quit()
        self.worker_thread.wait(5000)

    # --- Helpers ---
    def is_video_loaded(self) -> bool:
        return self._is_loaded
        
    def get_current_time(self) -> int:
        return self._current_time_msec
        
    def get_metadata(self) -> dict:
        return self._metadata