# src/app/ui/widgets/sidebar_widget.py

from PySide6.QtWidgets import QFrame, QVBoxLayout, QStackedWidget
from PySide6.QtGui import QColor

from ui.styles.theme import DarkTheme

# Importaciones de módulos/features
from features.timeline.videomarks_module import BookmarksModule 
from ui.widgets.drawing_controls_widget import DrawingControlsWidget
from services.video_service import VideoService  # Para tipado y estructura

class SidebarWidget(QFrame):
    """
    Contenedor principal para los módulos de funcionalidades (Features).
    Utiliza QStackedWidget para alternar entre Bookmarks y Drawing Controls.
    """

    def __init__(self, video_service: VideoService, parent_app, initial_color: QColor, parent=None):
        super().__init__(parent)

        # Asignar objectName para CSS si lo necesitas
        self.setObjectName("sidebar_widget")
        self.setStyleSheet(DarkTheme.GLOBAL_STYLES)

        # Inyección de dependencias
        self.video_service = video_service
        self.parent_app = parent_app 

        self.setup_ui(initial_color)

    def setup_ui(self, initial_color: QColor):
        """Configura la disposición principal con QStackedWidget."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # QStackedWidget para alternar entre Bookmarks y Drawing Controls
        self.tabs = QStackedWidget()

        # 1. Bookmarks Module (Index 0)
        self.bookmarks_module = BookmarksModule(
            self.video_service, 
            self.parent_app
        )
        self.tabs.addWidget(self.bookmarks_module)

        # 2. Drawing Controls Widget (Index 1)
        self.drawing_controls = DrawingControlsWidget(initial_color)
        self.tabs.addWidget(self.drawing_controls)

        main_layout.addWidget(self.tabs)

    # --- Interfaz para MainWindow ---

    def set_current_tab(self, index: int):
        """Establece la página activa del QStackedWidget."""
        if 0 <= index < self.tabs.count():
            self.tabs.setCurrentIndex(index)

    def get_bookmarks_module(self) -> BookmarksModule:
        """Retorna la instancia del módulo de Bookmarks."""
        return self.bookmarks_module

    def get_drawing_controls_widget(self) -> DrawingControlsWidget:
        """Retorna la instancia del widget de control de dibujo."""
        return self.drawing_controls
