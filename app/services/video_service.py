# src/app/services/video_service.py

from PySide6.QtCore import QObject, Signal, Slot
import os

# Importamos la clase del adaptador solo para tipado
# from adapters.opencv_video_processor import OpenCVVideoProcessor 

class VideoService(QObject):
    """
    Servicio de Video (Video Service).
    
    Actúa como el mediador entre la UI (MainWindow/Widgets) y el procesador de video 
    de bajo nivel (el adaptador). Gestiona el estado de reproducción.
    """
    
    # Señales emitidas a la UI o a otros módulos
    frame_ready_signal = Signal(object) # Emite el frame (numpy array)
    time_updated_signal = Signal(int)    # Emite el tiempo actual en msec
    video_loaded_signal = Signal(bool, int, str) # éxito, duración, path del video

    def __init__(self, processor, parent=None): # 'processor' es la instancia de OpenCVVideoProcessor
        super().__init__(parent)
        
        # Inyección de Dependencia: El procesador de bajo nivel
        self.processor = processor 
        self.current_time_msec = 0
        self.duration_msec = 0
        self.video_path = None
        self.is_playing = False
        self.is_slider_down = False 

        self._connect_processor_signals()

    def _connect_processor_signals(self):
        """
        Conecta las señales del procesador de video a los slots del servicio.
        Asegura que se usen los nombres de señales correctos (..._signal).
        """
        # 🟢 CORRECCIÓN: Usar frame_ready_signal, time_updated_signal, video_loaded_signal
        self.processor.frame_ready_signal.connect(self.frame_ready_signal)
        self.processor.time_updated_signal.connect(self._handle_time_update)
        self.processor.video_loaded_signal.connect(self._handle_video_loaded)

    # --- Métodos de Ayuda ---
    
    @staticmethod
    def format_time(msec):
        """Formatea milisegundos a una cadena de tiempo (HH:MM:SS)."""
        sec = msec // 1000
        min = sec // 60
        sec %= 60
        hr = min // 60
        min %= 60
        return f"{hr:02}:{min:02}:{sec:02}"
        
    def is_video_loaded(self) -> bool:
        """Verifica si hay un video cargado."""
        return self.processor.is_loaded

    def get_current_time(self) -> int:
        """Retorna el tiempo actual de reproducción."""
        return self.current_time_msec
        
    # --- Slots Internos (Reciben del Procesador) ---

    @Slot(int)
    def _handle_time_update(self, current_msec):
        """Actualiza el tiempo interno y notifica a la UI."""
        self.current_time_msec = current_msec
        if not self.is_slider_down:
            self.time_updated_signal.emit(current_msec)
            
    @Slot(bool, int, str)
    def _handle_video_loaded(self, success: bool, duration_msec: int, video_path: str):
        """
        Maneja la carga exitosa/fallida del video desde el procesador.
        """
        self.duration_msec = duration_msec
        self.video_path = video_path
        
        if success:
            self.toggle_play_pause(False) # Iniciar en pausa
            
        self.video_loaded_signal.emit(success, duration_msec, video_path)


    # --- Métodos de Control (API del Servicio usados por la UI) ---

    def load_video_file(self, path: str):
        """Solicita al procesador que cargue un archivo de video."""
        self.video_path = path
        self.processor.load_video(path)

    def toggle_play_pause(self, play: bool):
        """Alterna el estado de reproducción."""
        if self.processor.is_loaded:
            self.is_playing = play
            self.processor.set_playing(play)

    def seek(self, msec: int):
        """Solicita al procesador que se mueva a un tiempo específico."""
        self.is_slider_down = False
        self.processor.seek(msec)
        self.time_updated_signal.emit(msec) 

    def slider_moved(self):
        """Marca que el slider está siendo arrastrado por el usuario."""
        self.is_slider_down = True
        
    def set_quality(self, factor: float):
        """Solicita al procesador que cambie la calidad de reproducción."""
        self.processor.set_quality(factor)
        
    def stop_service(self):
        """Detiene el hilo de procesamiento de video al cerrar la aplicación."""
        self.processor.stop_processing()