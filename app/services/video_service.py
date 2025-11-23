# src/app/services/video_service.py

from PySide6.QtCore import QObject, Signal

# ----------------------------------------------------------------------
# 1. INTERFAZ: Contrato para cualquier procesador de video (Adaptador)
# ----------------------------------------------------------------------
class VideoProcessorInterface(QObject):
    """
    Define los métodos y señales que el adaptador (e.g., OpenCV) 
    debe implementar para el Servicio.
    """
    
    # Señales emitidas por el Procesador (escuchadas por el Servicio)
    frame_ready = Signal(object) # object es el frame de cv2
    video_loaded = Signal(bool, int, str) # success, duration_msec, video_directory
    time_updated = Signal(int) # current_msec
    
    # Métodos a implementar
    def open(self, path: str) -> bool: pass
    def run_playback_loop(self): pass
    def stop_thread(self): pass
    def toggle_play_pause(self, play: bool): pass
    def seek(self, msec: int): pass
    def slider_moved(self, msec: int): pass
    def slider_released(self): pass
    def set_scale_factor(self, scale: float): pass
    def get_metadata(self) -> dict: pass
    
    # Métodos que solo tiene el adaptador, pero útiles para el servicio
    def get_current_time(self) -> int: pass
    def is_video_loaded(self) -> bool: pass


# ----------------------------------------------------------------------
# 2. SERVICIO: La Capa de Coordinación (El Port)
# ----------------------------------------------------------------------
class VideoService(QObject):
    """
    Servicio de la capa de aplicación. 
    Mantiene la interfaz de comunicación con la UI.
    """
    # Señales que el Servicio EMITE (y la UI ESCUCHA)
    frame_ready_signal = Signal(object) 
    video_loaded_signal = Signal(bool, int, str)
    time_updated_signal = Signal(int)

    def __init__(self, processor: VideoProcessorInterface, parent=None):
        super().__init__(parent)
        self.processor = processor # Inyección de dependencia (el Adaptador)
        
        # Cableado: Adaptador (Procesador) -> Servicio
        self.processor.frame_ready.connect(self.frame_ready_signal.emit)
        self.processor.video_loaded.connect(self.video_loaded_signal.emit)
        self.processor.time_updated.connect(self.time_updated_signal.emit)
        
        # Inicializar el hilo de trabajo del procesador
        self.processor.run_playback_loop()

    # Métodos que la UI invoca directamente en el Servicio
    def load_video_file(self, path: str):
        """Intenta cargar el video en el procesador."""
        self.processor.open(path)
        
    def toggle_play_pause(self, play: bool):
        self.processor.toggle_play_pause(play)
        
    def seek(self, msec: int):
        self.processor.seek(msec)
        
    def slider_moved(self, msec: int):
        self.processor.slider_moved(msec)
        
    def slider_released(self):
        self.processor.slider_released()

    def set_quality(self, scale: float):
        self.processor.set_scale_factor(scale)
        
    def stop_service(self):
        self.processor.stop_thread()
        
    # Helpers para la UI
    def get_current_time(self) -> int:
        return self.processor.get_current_time()
        
    def is_video_loaded(self) -> bool:
        return self.processor.is_video_loaded()
    
    def get_metadata(self) -> dict:
        return self.processor.get_metadata()
        
    @staticmethod
    def format_time(msec):
        """Helper estático para formatear tiempo (milisegundos a HH:MM:SS:ms)."""
        total_seconds = int(msec / 1000)
        ms = msec % 1000
        seconds = total_seconds % 60
        minutes = (total_seconds // 60) % 60
        hours = total_seconds // 3600
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{ms:03d}"