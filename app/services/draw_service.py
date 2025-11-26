# src/app/services/draw_service.py

from PySide6.QtCore import QObject, Signal
# Importamos la lógica de la Feature (el adaptador de lógica de persistencia)
from features.draw.manager import DrawManager

class DrawService(QObject):
    """
    Servicio de Dibujo (Draw Service).

    Actúa como el mediador (Port) entre la capa de Presentación (MainWindow) 
    y la lógica de negocio/persistencia específica de la feature (DrawManager).
    """
    
    drawing_saved = Signal() 

    # 🟢 CORRECCIÓN: Cambiar el nombre del argumento de 'draw_manager' a 'manager'
    def __init__(self, manager: DrawManager, parent=None): 
        super().__init__(parent)
        self.manager = manager # Asigna el manager inyectado

    # --- Métodos de la API del Servicio (Usados por la MainWindow) ---
    
    def save_drawing(self, current_time_msec: int, duration_msec: int, paths_data: list):
        """
        Delega la lógica de guardar un nuevo dibujo al manager.
        """
        self.manager.add_drawing_entry(current_time_msec, duration_msec, paths_data)
        self.drawing_saved.emit()

    def get_paths_at_time(self, current_msec: int) -> list:
        """
        Obtiene los paths que deben ser visibles en el tiempo dado.
        """
        return self.manager.get_active_drawing_paths(current_msec)

    def load_data(self, path: str):
        """
        Delega la carga de datos de dibujo desde un archivo.
        """
        self.manager.load_data_from_file(path)

    def save_data(self, path: str):
        """
        Delega el guardado de datos de dibujo a un archivo.
        """
        self.manager.save_data_to_file(path)