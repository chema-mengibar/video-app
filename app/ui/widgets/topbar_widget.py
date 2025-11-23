# src/app/ui/widgets/topbar_widget.py

from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon 
from ui.styles.theme import DarkTheme

class TopBarWidget(QFrame):
    """
    Barra superior que contiene los controles principales de la aplicación:
    - Botón Load Video (izquierda)
    - Botones toggle para Sidebar (derecha)
    """

    # Señales emitidas a la MainWindow
    load_video_request = Signal()
    toggle_bookmarks_request = Signal(bool)
    toggle_drawing_request = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Asignar objectName para aplicar CSS
        self.setObjectName("topbar_widget")
        self.setStyleSheet(DarkTheme.TOOLBAR_STYLES)

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Botón Load Video (izquierda)
        self.btn_load_video = QPushButton("Load Video")

        self.btn_load_video.setIcon(QIcon("assets/icons/photo-camera.svg"))
        self.btn_load_video.setIconSize(QSize(12, 12))
        self.btn_load_video.setToolTip("Open Video file")

        layout.addWidget(self.btn_load_video)

        # Botones toggle (derecha)
        self.btn_toggle_bookmarks = QPushButton("Marks")
        self.btn_toggle_drawing = QPushButton("Draw")

        self.btn_toggle_bookmarks.setCheckable(True)
        self.btn_toggle_drawing.setCheckable(True)

        # Inicial Tab
        self.btn_toggle_bookmarks.setChecked(True)

        layout.addStretch(1)  # Empuja los toggles hacia la derecha
        layout.addWidget(self.btn_toggle_bookmarks)
        layout.addWidget(self.btn_toggle_drawing)

    def connect_signals(self):
        # Conexiones externas
        self.btn_load_video.clicked.connect(self.load_video_request.emit)
        self.btn_toggle_bookmarks.toggled.connect(self.toggle_bookmarks_request.emit)
        self.btn_toggle_drawing.toggled.connect(self.toggle_drawing_request.emit)

        # Comportamiento tipo "radio button"
        self.btn_toggle_bookmarks.toggled.connect(self._handle_toggle_bookmarks)
        self.btn_toggle_drawing.toggled.connect(self._handle_toggle_drawing)

    def _handle_toggle_bookmarks(self, checked: bool):
        if checked:
            self.btn_toggle_drawing.setChecked(False)
        elif not self.btn_toggle_drawing.isChecked():
            self.btn_toggle_drawing.setChecked(True)

    def _handle_toggle_drawing(self, checked: bool):
        if checked:
            self.btn_toggle_bookmarks.setChecked(False)
        elif not self.btn_toggle_bookmarks.isChecked():
            self.btn_toggle_bookmarks.setChecked(True)
