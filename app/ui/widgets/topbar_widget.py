# src/app/ui/widgets/topbar_widget.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal, QObject

class TopBarWidget(QWidget):
    """
    Barra superior que contiene los controles principales de la aplicación:
    - Cargar video (a la izquierda).
    - Botones de alternancia para el Sidebar (a la derecha).
    """
    
    # Señales emitidas a la MainWindow
    load_video_request = Signal()
    toggle_bookmarks_request = Signal(bool) # Emite el estado checked del botón
    toggle_drawing_request = Signal(bool)  # Emite el estado checked del botón

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        top_bar_layout = QHBoxLayout(self)
        top_bar_layout.setContentsMargins(10, 5, 10, 5)

        # A. Botón Load (Izquierda)
        self.btn_load_video = QPushButton("📂 Load Video")
        top_bar_layout.addWidget(self.btn_load_video)

        # Espaciador (ocupa todo el espacio central)
        top_bar_layout.addStretch(1)

        # B. Botones de Toggle de Sidebar (Derecha)
        self.btn_toggle_bookmarks = QPushButton("⭐ Bookmarks")
        self.btn_toggle_drawing = QPushButton("🎨 Drawing Controls")
        
        # Marcar los botones como "checkable" para simular un selector de pestaña
        self.btn_toggle_bookmarks.setCheckable(True)
        self.btn_toggle_drawing.setCheckable(True)

        # Por defecto, iniciar con Drawing activo
        self.btn_toggle_drawing.setChecked(True)

        top_bar_layout.addWidget(self.btn_toggle_bookmarks)
        top_bar_layout.addWidget(self.btn_toggle_drawing)
        
    def connect_signals(self):
        # Conexión interna para emitir las señales externas
        self.btn_load_video.clicked.connect(self.load_video_request.emit)
        self.btn_toggle_bookmarks.toggled.connect(self.toggle_bookmarks_request.emit)
        self.btn_toggle_drawing.toggled.connect(self.toggle_drawing_request.emit)
        
        # Conexión interna para simular el comportamiento de "radio button"
        self.btn_toggle_bookmarks.toggled.connect(self._handle_toggle_bookmarks)
        self.btn_toggle_drawing.toggled.connect(self._handle_toggle_drawing)
        
    def _handle_toggle_bookmarks(self, checked: bool):
        """Si Bookmarks se activa, desactiva Drawing, si se desactiva y el otro está apagado, lo enciende."""
        if checked:
            self.btn_toggle_drawing.setChecked(False)
        elif not self.btn_toggle_drawing.isChecked():
            # Evita que ambos se apaguen a la vez. Si uno se apaga y el otro no está,
            # forzamos el encendido del otro para mantener al menos una pestaña visible.
            self.btn_toggle_drawing.setChecked(True)

    def _handle_toggle_drawing(self, checked: bool):
        """Si Drawing se activa, desactiva Bookmarks, si se desactiva y el otro está apagado, lo enciende."""
        if checked:
            self.btn_toggle_bookmarks.setChecked(False)
        elif not self.btn_toggle_bookmarks.isChecked():
            # Evita que ambos se apaguen a la vez
            self.btn_toggle_bookmarks.setChecked(True)