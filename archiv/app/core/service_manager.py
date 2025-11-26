# src/app/core/service_manager.py

from PySide6.QtCore import QObject, Signal, Slot 
import os
from typing import TYPE_CHECKING, List # Para evitar referencias circulares en type hints

# Importaciones reales para la ejecución
# Nota: La estructura real requiere que estos módulos sean importables desde aquí
from services.video_service import VideoService
from services.draw_service import DrawService
from features.grid.grids_manager import GridsManager
from features.grid.grid_data import GridData # Necesario para type hints de guardado


# Nota: Utilizamos TYPE_CHECKING para evitar circular dependencies si el tipo se usa solo en hints
if TYPE_CHECKING:
    # Estos type hints son solo para el IDE y el análisis estático
    # No afectan la ejecución en tiempo de carga
    from services.video_service import VideoService
    from services.draw_service import DrawService
    from features.grid.grids_manager import GridsManager


class ServiceManager(QObject):
    """
    Centraliza la gestión y orquestación de los servicios (Video, Dibujo, Grid).
    Mantiene referencias a los servicios y managers, y orquesta la carga/guardado 
    de datos asociados a un video. Es el punto central de acceso a la lógica de negocio.
    """
    
    # Señal para notificar a la UI cuando la duración y el estado del video cambian
    # (success: bool, duration_msec: int, video_directory: str)
    video_loaded_info = Signal(bool, int, str) 

    def __init__(self, video_service: VideoService, draw_service: DrawService, grids_manager: GridsManager, parent=None):
        super().__init__(parent)
        
        # Diccionario para almacenar todos los servicios
        self._services = {}
        
        # Registrar los servicios y managers
        self.register_service('VideoService', video_service)
        self.register_service('DrawService', draw_service)
        self.register_service('GridsManager', grids_manager) # Añadido correctamente

        self._connect_service_signals()
        
    def register_service(self, name: str, service: QObject):
        """Registra un servicio con un nombre dado."""
        if name in self._services:
            print(f"Advertencia: El servicio '{name}' ya está registrado. Sobrescribiendo.")
        self._services[name] = service
        
    def get_service(self, name: str) -> QObject:
        """Recupera un servicio por su nombre."""
        if name not in self._services:
            # CRÍTICO: Levantar un error si un servicio esencial no se encuentra.
            raise ValueError(f"Error: Servicio '{name}' no encontrado en ServiceManager. Esto puede causar un fallo de arranque.")
        return self._services[name]

    def _connect_service_signals(self):
        """
        Conecta las señales internas de los servicios a los métodos de manejo interno
        del ServiceManager para orquestar la carga de datos.
        """
        self.video().video_loaded_signal.connect(self._handle_video_loaded_internal)

    @Slot(bool, int, str)
    def _handle_video_loaded_internal(self, success: bool, duration_msec: int, video_path: str):
        """Procesa la señal de carga del video, intenta cargar datos asociados y notifica a la UI."""
        
        video_directory = None
        if success and video_path:
            # Asegurarse de que el path no sea None antes de intentar obtener el directorio
            video_directory = os.path.dirname(video_path)
            self._load_associated_data(video_directory)
            
        # Emitir la señal externa (más simple para MainWindow)
        self.video_loaded_info.emit(success, duration_msec, video_directory)
        
    def _load_associated_data(self, video_directory: str):
        """Carga automáticamente los datos de dibujo, grids y otros features asociados."""
        
        # 1. Cargar DrawService data
        draw_path = os.path.join(video_directory, "drawings.json")
        self.draw().load_data(draw_path)
        
        # 2. Cargar GridsManager data
        grid_path = os.path.join(video_directory, "grids.json")
        self.grids().load_data(grid_path)
        
        
    # --- Métodos para la Coordinación (MainWindow) ---

    def get_active_drawing_paths(self, current_msec: int) -> list:
        """Pasa la petición de paths al DrawService."""
        return self.draw().get_paths_at_time(current_msec)
        
    def save_drawing_data(self, current_time: int, duration: int, paths_to_save: List[dict]):
        """Pasa la petición de guardado de dibujo al DrawService."""
        video_service = self.video()
        if video_service.video_path:
            video_directory = os.path.dirname(video_service.video_path)
            draw_path = os.path.join(video_directory, "drawings.json")
            
            # Delega el guardado
            self.draw().save_drawing_data(current_time, duration, paths_to_save, draw_path)

    # 2. GridsManager Delegation
    def save_grids_data(self):
        """Guarda todos los datos de GridsManager al archivo asociado al video."""
        video_service = self.video()
        if video_service.video_path:
            video_directory = os.path.dirname(video_service.video_path)
            grid_path = os.path.join(video_directory, "grids.json")
            
            # Asumimos que GridsManager tiene un método 'save_data'
            self.grids().save_data(grid_path)
    
    # --- Métodos Helper para Acceso Tipado (Convenience Accessors) ---
    # Facilitan el acceso a los servicios registrados por su nombre.
    
    def video(self) -> 'VideoService':
        """Acceso rápido a VideoService."""
        return self.get_service('VideoService')
    
    def draw(self) -> 'DrawService':
        """Acceso rápido a DrawService."""
        return self.get_service('DrawService')

    def grids(self) -> 'GridsManager':
        """Acceso rápido a GridsManager."""
        return self.get_service('GridsManager')
