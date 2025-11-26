# src/app/ui/widgets/sidebar_widget.py

from PySide6.QtWidgets import QFrame, QVBoxLayout, QStackedWidget, QWidget, QMainWindow
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

# Importaciones de los módulos de features y servicios
from services.video_service import VideoService 
from features.timeline.videomarks_module import BookmarksModule
from features.draw.drawing_module import DrawingModule
from features.grid.grid_module import GridModule
from features.grid.grids_manager import GridsManager # CRÍTICO: Necesario para la composición

class SidebarWidget(QFrame):
    """
    Contenedor para las vistas de la barra lateral (Bookmarks, Drawing, Grids).
    Usa QStackedWidget para manejar las diferentes vistas.
    """
    
    def __init__(self, 
                 video_service: VideoService, 
                 parent_app: QMainWindow, 
                 initial_color: QColor, 
                 view_location: str, 
                 bookmarks_module: BookmarksModule, 
                 grids_manager: GridsManager, # 🟢 CORRECCIÓN: Ahora acepta GridsManager
                 parent=None
                 ):
        
        super().__init__(parent)

        self.video_service = video_service
        self.parent_app = parent_app
        self.view_location = view_location
        self.initial_color = initial_color
        self.bookmarks_module = bookmarks_module
        self.grids_manager = grids_manager # Guardar el manager

        self._setup_ui()

    def _setup_ui(self):
        # Establece un ancho fijo para las barras laterales
        self.setFixedWidth(300) 
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. QStackedWidget para las Vistas
        self.tabs = QStackedWidget(self)
        
        # 2. Bookmarks Module (Index 0)
        # El módulo de Bookmarks se inyecta desde MainWindow
        self.tabs.addWidget(self.bookmarks_module) 
        
        # 3. Drawing Module (Index 1)
        self.drawing_module = DrawingModule(self.initial_color)
        self.tabs.addWidget(self.drawing_module)
        
        # 4. Grids Module (Index 2)
        # 🟢 CRÍTICO: Se pasa self.grids_manager y self.parent_app
        self.grid_module = GridModule(self.grids_manager, self.parent_app) 
        self.tabs.addWidget(self.grid_module)
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    # --- Acceso a Features (Requerido por MainWindow) ---
    
    def set_current_tab(self, index: int):
        """Método para cambiar la vista activa del QStackedWidget."""
        self.tabs.setCurrentIndex(index)
        
    def get_drawing_module(self) -> DrawingModule:
        """Acceso al módulo de dibujo (para conexiones en MainWindow)."""
        return self.drawing_module

    def get_grid_module(self) -> GridModule:
        """Acceso al módulo de grids (para conexiones en MainWindow)."""
        return self.grid_module
        
    def get_bookmarks_module(self) -> BookmarksModule:
        """Acceso al módulo de bookmarks (si es necesario)."""
        return self.bookmarks_module