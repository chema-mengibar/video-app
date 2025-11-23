# src/app/ui/widgets/sidebar_widget.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
)
from PySide6.QtCore import Slot

# Importaciones de los módulos que contendrá
from features.timeline.videomarks_module import BookmarksModule
from ui.widgets.drawing_controls_widget import DrawingControlsWidget

class SidebarWidget(QWidget):
    """
    Contenedor principal para las pestañas de las features (Bookmarks y Drawing Controls).
    """
    
    def __init__(self, video_service, parent_app, initial_pen_color, parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)
        # Importante: el BookmarksModule necesita el VideoService y la MainWindow (para format_time/paths)
        self.bookmarks_module = BookmarksModule(video_service, parent_app) 
        self.drawing_controls_widget = DrawingControlsWidget(initial_pen_color)
        
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Construye la estructura de la barra lateral (tabs y stack)."""
        main_v_layout = QVBoxLayout(self)
        
        # --- Pestañas de Features ---
        tab_bar = QWidget()
        tab_h_layout = QHBoxLayout(tab_bar)
        tab_h_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_tab_bookmarks = QPushButton("Bookmarks")
        self.btn_tab_draw = QPushButton("Drawing Controls")
        
        tab_h_layout.addWidget(self.btn_tab_bookmarks)
        tab_h_layout.addWidget(self.btn_tab_draw)
        main_v_layout.addWidget(tab_bar)
        
        # --- Stacked Widget (Contenido) ---
        self.body_stack = QStackedWidget()
        self.body_stack.addWidget(self.bookmarks_module)
        self.body_stack.addWidget(self.drawing_controls_widget)
        
        main_v_layout.addWidget(self.body_stack)

    def _connect_signals(self):
        """Conecta los botones de tabs a la vista correcta."""
        self.btn_tab_bookmarks.clicked.connect(lambda: self.body_stack.setCurrentIndex(0))
        self.btn_tab_draw.clicked.connect(lambda: self.body_stack.setCurrentIndex(1))

    # Acceso directo a los widgets internos para que el coordinador (MainWindow) pueda usarlos.
    def get_bookmarks_module(self) -> BookmarksModule:
        return self.bookmarks_module

    def get_drawing_controls_widget(self) -> DrawingControlsWidget:
        return self.drawing_controls_widget