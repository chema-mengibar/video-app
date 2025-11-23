# src/app/ui/widgets/drawing_controls_widget.py

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QGridLayout, QColorDialog
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Slot, Signal, QObject

class DrawingControlsWidget(QWidget):
    """
    Componente UI para controlar la herramienta de dibujo (color, toggle, duración).
    """
    
    # Señales para notificar al coordinador (MainWindow) de las acciones del usuario
    toggle_drawing_signal = Signal(bool)
    save_drawing_request = Signal()
    clear_canvas_request = Signal()
    color_changed = Signal(QColor)

    def __init__(self, initial_color: QColor, parent=None):
        super().__init__(parent)
        self.current_pen_color = initial_color
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Construye la interfaz de usuario para los controles."""
        layout = QGridLayout(self)
        
        layout.addWidget(QLabel("Enable Drawing:"), 0, 0)
        self.btn_draw_toggle = QPushButton("Toggle")
        self.btn_draw_toggle.setCheckable(True)
        layout.addWidget(self.btn_draw_toggle, 0, 1)
        
        layout.addWidget(QLabel("Pen Color:"), 1, 0)
        self.btn_color_pick = QPushButton("Pick Color")
        self._update_color_button_style(self.current_pen_color)
        layout.addWidget(self.btn_color_pick, 1, 1)
        
        layout.addWidget(QLabel("Duration (ms):"), 2, 0)
        self.drawing_duration_input = QLineEdit("2000")
        layout.addWidget(self.drawing_duration_input, 2, 1)
        
        self.btn_save_drawing = QPushButton("💾 Save Current Draw")
        layout.addWidget(self.btn_save_drawing, 3, 0, 1, 2)
        
        self.btn_clear_canvas = QPushButton("🗑️ Clear Canvas")
        layout.addWidget(self.btn_clear_canvas, 4, 0, 1, 2)

        layout.setRowStretch(5, 1)

    def _connect_signals(self):
        """Conecta los widgets a las señales de salida del componente."""
        self.btn_draw_toggle.toggled.connect(self.toggle_drawing_signal)
        self.btn_color_pick.clicked.connect(self._select_drawing_color)
        self.btn_save_drawing.clicked.connect(self.save_drawing_request)
        self.btn_clear_canvas.clicked.connect(self.clear_canvas_request)

    @Slot()
    def _select_drawing_color(self):
        """Abre el diálogo de color y emite la señal del nuevo color."""
        color = QColorDialog.getColor(self.current_pen_color, self, "Select Pen Color")
        if color.isValid():
            self.current_pen_color = color
            self._update_color_button_style(color)
            self.color_changed.emit(color) # Notificar al coordinador
            
    def _update_color_button_style(self, color: QColor):
        """Actualiza el estilo del botón de color."""
        hex_color = color.name()
        self.btn_color_pick.setStyleSheet(f"background-color: {hex_color}; color: white; padding: 6px 10px; border-radius: 4px;")

    def get_duration(self) -> int:
        """Devuelve la duración actual del campo de entrada, con un fallback."""
        try:
            duration = int(self.drawing_duration_input.text())
            return max(100, duration) # Duración mínima de 100ms
        except ValueError:
            return 2000