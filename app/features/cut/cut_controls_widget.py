from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLineEdit, QLabel, QGroupBox
)
from PySide6.QtGui import QIcon 
from PySide6.QtCore import Signal, Slot, Qt, QSize

class CutControlsWidget(QWidget):
    """
    Widget de la barra lateral para controlar la funcionalidad de cortar clips de video.
    
    Permite al usuario definir un rango de tiempo de inicio y fin para guardar clips.
    """
    
    # Señales para notificar al módulo superior (CutModule)
    start_use_current_time_request = Signal()
    end_use_current_time_request = Signal()
    save_clip_request = Signal(int, int)  # Emite start_msec y end_msec
    
    def __init__(self, parent=None): 
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    # --- Construcción de UI ---
    def _create_time_input_row(self, initial_time: str) -> tuple[QHBoxLayout, QLineEdit, QPushButton]:
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        time_edit = QLineEdit(initial_time)
        time_edit.setFixedWidth(100)
        time_edit.setAlignment(Qt.AlignCenter)

        btn_use = QPushButton()
        btn_use.setIcon(QIcon("assets/icons/chrono.svg"))
        btn_use.setIconSize(QSize(12, 12))
        btn_use.setToolTip("Use current time")
        btn_use.setFixedSize(25, 25)
        btn_use.setObjectName("SmallActionButton")
       
        h_layout.addWidget(time_edit)
        h_layout.addWidget(btn_use)
        h_layout.addStretch(1)
        
        return h_layout, time_edit, btn_use

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        title = QLabel("Corte de Video")
        title.setObjectName("SidebarTitle")
        main_layout.addWidget(title)

        

        self.time_inputs = {}

        # --- Display group ---
        display_group = QGroupBox("Rango de Tiempo")
        display_layout = QVBoxLayout(display_group)

        # Start time
        time_layout_start, self.time_start_edit, self.btn_start_u = self._create_time_input_row("00:00:00:000")
        display_layout.addLayout(time_layout_start)
        self.time_inputs['start'] = self.time_start_edit

        # End time
        time_layout_end, self.time_end_edit, self.btn_end_u = self._create_time_input_row("00:00:00:000")
        display_layout.addLayout(time_layout_end)
        self.time_inputs['end'] = self.time_end_edit

        # Botón de guardar clip
        self.btn_save_clip = QPushButton("Guardar Clip")
        self.btn_save_clip.setFixedHeight(30)
        display_layout.addWidget(self.btn_save_clip)

        main_layout.addWidget(display_group)
        main_layout.addStretch(1)

    # --- Conexión de señales ---
    def _connect_signals(self):
        self.btn_start_u.clicked.connect(self.start_use_current_time_request.emit)
        self.btn_end_u.clicked.connect(self.end_use_current_time_request.emit)
        self.btn_save_clip.clicked.connect(self._emit_save_clip_request)

    # --- Slots públicos para actualizar los inputs ---
    @Slot(int, str)
    def set_display_start_time(self, msec: int, time_str: str):
        self.time_start_edit.setText(time_str)

    @Slot(int, str)
    def set_display_end_time(self, msec: int, time_str: str):
        self.time_end_edit.setText(time_str)

    # --- Emitir señal de guardar clip ---
    def _emit_save_clip_request(self):
        try:
            start_text = self.time_start_edit.text()
            end_text = self.time_end_edit.text()
            start_msec = self._time_str_to_msec(start_text)
            end_msec = self._time_str_to_msec(end_text)
            self.save_clip_request.emit(start_msec, end_msec)
        except Exception as e:
            print(f"Error al emitir save_clip_request: {e}")

    # --- Conversión de tiempo ---
    def _time_str_to_msec(self, time_str: str) -> int:
        """
        Convierte 'HH:MM:SS:MS' o 'MM:SS:MS' a milisegundos.
        """
        parts = time_str.split(":")
        parts = [int(p) for p in parts]
        if len(parts) == 3:
            hours = 0
            minutes, seconds, milliseconds = parts
        elif len(parts) == 4:
            hours, minutes, seconds, milliseconds = parts
        else:
            raise ValueError(f"Formato de tiempo inválido: {time_str}")
        return ((hours*3600 + minutes*60 + seconds)*1000 + milliseconds)
