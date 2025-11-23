# src/app/core/service_manager.py

# 🟢 CORRECCIÓN: Se añade Slot a las importaciones
from PySide6.QtCore import QObject, Signal, Slot 
import os

# Importamos todos los servicios y features que gestionaremos
from services.video_service import VideoService
from services.draw_service import DrawService

class ServiceManager(QObject):
    """
    Centraliza la gestión y orquestación de los servicios.
    Mantiene referencias a los servicios y facilita la carga/guardado de datos.
    """
    # Señal para notificar a la UI cuando la duración y el estado del video cambian
    video_loaded_info = Signal(bool, int, str) # success, duration_msec, video_directory

    def __init__(self, video_service: VideoService, draw_service: DrawService, parent=None):
        super().__init__(parent)
        self.video_service = video_service
        self.draw_service = draw_service
        self._connect_service_signals()
        
    def _connect_service_signals(self):
        """Conecta las señales internas del VideoService a las señales externas del Manager."""
        self.video_service.video_loaded_signal.connect(self._handle_video_loaded_internal)

    @Slot(bool, int, str)
    def _handle_video_loaded_internal(self, success, duration_msec, video_path):
        """Procesa la señal de carga del video, intenta cargar datos asociados y notifica a la UI."""
        
        video_directory = None
        if success and video_path:
            # Asegurarse de que el path no sea None antes de intentar obtener el directorio
            video_directory = os.path.dirname(video_path)
            self._load_associated_data(video_directory)
            
        # Emitir la señal externa (más simple para MainWindow)
        self.video_loaded_info.emit(success, duration_msec, video_directory)
        
    def _load_associated_data(self, video_directory: str):
        """Carga automáticamente los datos de dibujo y bookmarks."""
        # Aquí solo cargamos el DrawService. La MainWindow cargará los bookmarks después
        # de recibir la señal de video_loaded_info.
        
        draw_path = os.path.join(video_directory, "drawings.json")
        self.draw_service.load_data(draw_path)

    # Métodos para el coordinador (MainWindow)
    def get_active_drawing_paths(self, current_msec: int) -> list:
        """Pasa la petición de paths al DrawService."""
        return self.draw_service.get_paths_at_time(current_msec)
        
    def save_drawing_data(self, current_time: int, duration: int, paths_to_save: list):
        """Pasa la petición de guardar dibujo al DrawService."""
        self.draw_service.save_drawing(current_time, duration, paths_to_save)