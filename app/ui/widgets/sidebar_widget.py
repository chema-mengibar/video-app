from PySide6.QtWidgets import QFrame, QVBoxLayout, QStackedWidget, QLabel 
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow # Importación necesaria para el tipado de parent_app

from ui.styles.theme import DarkTheme

# Importaciones de módulos/features (Clases corregidas según tu estructura)
from features.timeline.videomarks_module import BookmarksModule 
from features.draw.drawing_module import DrawingModule
from features.grid.grid_module import GridModule
from services.video_service import VideoService 

class SidebarWidget(QFrame):
    """
    Contenedor principal para los módulos de funcionalidades (Features).
    Utiliza QStackedWidget para alternar entre Bookmarks, Drawing Controls y Grids.
    Ahora acepta una ubicación ('left' o 'right') para referencia en el coordinador.
    """

    # Se añade view_location y se eliminan las dependencias extra
    def __init__(self, 
                 video_service: VideoService, 
                 parent_app: QMainWindow, # El coordinador (MainWindow)
                 initial_color: QColor, 
                 view_location: str, # NUEVO: 'left' o 'right'
                 parent=None):
        
        super().__init__(parent)

        self.setObjectName("sidebar_widget")
        self.setStyleSheet(DarkTheme.GLOBAL_STYLES)

        # Inyección de dependencias
        self.video_service = video_service
        self.parent_app = parent_app 
        self.view_location = view_location # Guardamos la ubicación

        self.setup_ui(initial_color)

    def setup_ui(self, initial_color: QColor):
        """Configura la disposición principal con QStackedWidget."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # QStackedWidget para alternar entre Bookmarks, Drawing Controls y Grids
        self.tabs = QStackedWidget()

        # 1. Bookmarks Module (Index 0)
        self.bookmarks_module = BookmarksModule(
            self.video_service, 
            self.parent_app
        )
        self.tabs.addWidget(self.bookmarks_module)

        # 2. Drawing Module (Index 1)
        self.drawing_module = DrawingModule(initial_color)
        self.tabs.addWidget(self.drawing_module)

        # 3. Grids Module (Index 2)
        self.grid_module = GridModule(self.parent_app)
        self.tabs.addWidget(self.grid_module)

        main_layout.addWidget(self.tabs)

    # --- Interfaz para MainWindow ---

    def set_current_tab(self, index: int):
        """Establece la página activa del QStackedWidget."""
        if 0 <= index < self.tabs.count():
            self.tabs.setCurrentIndex(index)

    def get_bookmarks_module(self) -> BookmarksModule:
        """Retorna la instancia del módulo de Bookmarks."""
        return self.bookmarks_module

    def get_drawing_module(self) -> DrawingModule:
        """Retorna la instancia del módulo de dibujo."""
        return self.drawing_module

    def get_grid_module(self) -> GridModule:
        """Retorna la instancia del módulo de Grid."""
        return self.grid_module