from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QGridLayout, QColorDialog, QSpinBox # QSpinBox es necesario para el grosor
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Slot, Signal, QObject, Qt

class DrawingModule(QWidget):
    """
    Componente UI para controlar la herramienta de dibujo (color, duración, guardado).
    """
    
    # Señales para notificar al coordinador (MainWindow) de las acciones del usuario
    save_drawing_request = Signal()
    clear_canvas_request = Signal()
    color_changed = Signal(QColor)
    # 🟢 Deshacer y Grosor: Nombres de señales esperados por MainWindow
    undo_request = Signal() 
    thickness_changed = Signal(int) 

    def __init__(self, initial_color: QColor, parent=None):
        super().__init__(parent)
        self.current_pen_color = initial_color
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Construye la interfaz de usuario para los controles."""
        layout = QGridLayout(self)

        layout.addWidget(QLabel("Pen Color:"), 0, 0)
        self.btn_color_pick = QPushButton("Pick Color")
        self._update_color_button_style(self.current_pen_color)
        layout.addWidget(self.btn_color_pick, 0, 1)

        # 🟢 Grosor de Línea (usa QSpinBox)
        layout.addWidget(QLabel("Grosor:"), 1, 0)
        self.thickness_input = QSpinBox(minimum=1, maximum=20, value=3)
        layout.addWidget(self.thickness_input, 1, 1)
        
        # Rango de tiempo de la marca (Duración del dibujo)
        layout.addWidget(QLabel("Duración (msec):"), 2, 0)
        self.duration_input = QLineEdit("5000") # 5 segundos por defecto
        layout.addWidget(self.duration_input, 2, 1)

        # 🟢 Botón de Deshacer
        self.btn_undo = QPushButton("⬅️ Deshacer Último Trazo")
        layout.addWidget(self.btn_undo, 3, 0, 1, 2)
        
        self.btn_clear_canvas = QPushButton("🗑️ Clear Canvas")
        layout.addWidget(self.btn_clear_canvas, 4, 0, 1, 2)

        self.btn_save_drawing = QPushButton("💾 Guardar Dibujo")
        layout.addWidget(self.btn_save_drawing, 5, 0, 1, 2)

        layout.setRowStretch(6, 1) 
        self.setLayout(layout)

    def _connect_signals(self):
        """Conecta los widgets a las señales de salida del componente."""
        self.btn_color_pick.clicked.connect(self._select_drawing_color)
        self.btn_save_drawing.clicked.connect(self.save_drawing_request)
        self.btn_clear_canvas.clicked.connect(self.clear_canvas_request)
        
        # 🟢 Conexión de las señales 'undo_request' y 'thickness_changed'
        self.btn_undo.clicked.connect(self.undo_request.emit) 
        self.thickness_input.valueChanged.connect(self.thickness_changed.emit)

    @Slot()
    def _select_drawing_color(self):
        """Abre el diálogo de color y emite la señal del nuevo color."""
        color = QColorDialog.getColor(self.current_pen_color, self, "Select Pen Color")
        if color.isValid():
            self.current_pen_color = color
            self._update_color_button_style(color)
            self.color_changed.emit(color)
            
    def _update_color_button_style(self, color: QColor):
        """Actualiza el estilo del botón de color."""
        hex_color = color.name()
        self.btn_color_pick.setStyleSheet(f"background-color: {hex_color}; color: white; padding: 6px 10px; border-radius: 4px;")

    def get_duration(self) -> int:
        """Retorna la duración de la marca de dibujo desde el input."""
        try:
            return int(self.duration_input.text())
        except ValueError:
            return 5000