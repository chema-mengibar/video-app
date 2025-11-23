# features/drawing_controls.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QPushButton, QLabel
from PySide6.QtCore import Qt
from theme import DarkTheme # Importar el tema

class DrawingControlsModule(QWidget):
    """Widget de la interfaz que contiene los controles para el Dibujo."""
    def __init__(self, parent_controller):
        super().__init__()
        self.controller = parent_controller
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.setStyleSheet("color: white; background-color: transparent;") 
        
        layout.addWidget(QLabel("### ✏️ Herramientas de Dibujo", alignment=Qt.AlignCenter))
        
        self.check_drawing = QCheckBox("Activar Trazado (Clic y Arrastre)")
        self.btn_clear_drawing = QPushButton("Limpiar Trazos")
        
        # Usar estilo de botón de acción del sidebar
        self.btn_clear_drawing.setStyleSheet(DarkTheme.SIDEBAR_ACTION_BUTTON)

        layout.addWidget(self.check_drawing)
        layout.addWidget(self.btn_clear_drawing)
        layout.addStretch(1)

        # Conexiones a la Lógica Central
        self.check_drawing.toggled.connect(self.controller.toggle_drawing)
        self.btn_clear_drawing.clicked.connect(self.controller.clear_drawing)