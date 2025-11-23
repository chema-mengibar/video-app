# src/app/ui/widgets/sidebar_widget.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget # ⚠️ CAMBIO AQUÍ
from PySide6.QtGui import QColor

# Importaciones de los módulos de features (deben existir)
from features.timeline.videomarks_module import BookmarksModule 
from ui.widgets.drawing_controls_widget import DrawingControlsWidget
from services.video_service import VideoService # Usado para tipado y estructura

class SidebarWidget(QWidget):
    """
    Contenedor principal para todos los módulos de funcionalidades (Features).
    Utiliza QStackedWidget para alternar entre Bookmarks y Drawing Controls.
    """
    def __init__(self, video_service: VideoService, parent_app, initial_color: QColor, parent=None):
        super().__init__(parent)
        
        # Inyección de Dependencias
        self.video_service = video_service
        self.parent_app = parent_app 
        
        self.setup_ui(initial_color)
        
    def setup_ui(self, initial_color: QColor):
        """Configura la disposición principal con el QStackedWidget."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # ⚠️ CAMBIO: Usamos QStackedWidget en lugar de QTabWidget
        self.tabs = QStackedWidget() 
        
        # 1. Bookmarks Module (Index 0)
        self.bookmarks_module = BookmarksModule(
            self.video_service, 
            self.parent_app
        )
        # Añadir como una página, no como una pestaña
        self.tabs.addWidget(self.bookmarks_module) 
        
        # 2. Drawing Controls Widget (Index 1)
        self.drawing_controls = DrawingControlsWidget(
            initial_color        
        )
        # Añadir como otra página
        self.tabs.addWidget(self.drawing_controls)
        
        main_layout.addWidget(self.tabs)
        
    # --- Interfaz para MainWindow (Acceso y Control) ---

    def set_current_tab(self, index: int):
        """Establece la página activa del QStackedWidget."""
        # QStackedWidget usa setCurrentIndex() igual que QTabWidget, simplificando MainWindow.
        if 0 <= index < self.tabs.count():
            self.tabs.setCurrentIndex(index)

    def get_bookmarks_module(self) -> BookmarksModule:
        """Retorna la instancia del módulo de Bookmarks."""
        return self.bookmarks_module

    def get_drawing_controls_widget(self) -> DrawingControlsWidget:
        """Retorna la instancia del widget de control de dibujo."""
        return self.drawing_controls