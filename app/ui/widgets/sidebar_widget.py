from PySide6.QtWidgets import QFrame, QVBoxLayout, QStackedWidget, QLabel, QWidget 
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow 

from ui.styles.theme import DarkTheme

# Importaciones de módulos/features 
from features.timeline.videomarks_module import BookmarksModule 
from features.draw.drawing_module import DrawingModule
from features.grid.grid_module import GridModule
from services.video_service import VideoService 

class SidebarWidget(QFrame):
    """
    Contenedor principal para los módulos de funcionalidades (Features).
    Utiliza QStackedWidget para alternar entre Bookmarks, Drawing Controls y Grids.
    Controla la inyección del BookmarksModule para evitar el error de "widget parenting".
    """

    def __init__(self, 
                 video_service: VideoService, 
                 parent_app: QMainWindow, # El coordinador (MainWindow)
                 initial_color: QColor, 
                 view_location: str, # 'left' o 'right'
                 bookmarks_module: BookmarksModule, # Instancia única de BookmarksModule
                 parent=None
                 ):
        
        super().__init__(parent)

        self.setObjectName("sidebar_widget")
        self.setStyleSheet(DarkTheme.GLOBAL_STYLES)

        # Inyección de dependencias
        self.video_service = video_service
        self.parent_app = parent_app 
        self.view_location = view_location
        # Guardamos la referencia a la instancia única de Bookmarks (lógica)
        self._bookmarks_module = bookmarks_module 
        
        # Pasamos la instancia a setup_ui para decidir si añadir el widget real o un placeholder
        self.setup_ui(initial_color, self._bookmarks_module)

    def setup_ui(self, initial_color: QColor, bookmarks_module: BookmarksModule):
        """
        Configura la disposición principal con QStackedWidget. 
        Añade el widget real de Bookmarks solo si view_location es 'left'.
        """
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # QStackedWidget para alternar entre módulos
        self.tabs = QStackedWidget()

        # 1. Bookmarks Module (Index 0)
        # Solo el sidebar 'left' debe contener el widget BookmarksModule real 
        # para que Qt no lo mueva. El 'right' usa un placeholder para mantener el índice.
        if self.view_location == 'left':
            self.tabs.addWidget(bookmarks_module)
        else:
            # Placeholder vacío para ocupar el índice 0 en el lado derecho
            placeholder = QWidget()
            placeholder.setObjectName("BookmarksPlaceholder")
            self.tabs.addWidget(placeholder)


        # 2. Drawing Module (Index 1) - Mantenemos los índices consistentes
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


    def get_drawing_module(self) -> DrawingModule:
        """Retorna la instancia del módulo de dibujo."""
        return self.drawing_module

    def get_grid_module(self) -> GridModule:
        """Retorna la instancia del módulo de Grid."""
        return self.grid_module

    def get_bookmarks_module(self) -> BookmarksModule:
        """
        Retorna la instancia lógica y única del módulo de bookmarks 
        (inyectada en __init__), independientemente de qué lado contenga el widget visual.
        """
        return self._bookmarks_module