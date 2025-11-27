from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot
from features.cut.cut_controls_widget import CutControlsWidget
from services.video_service import VideoService  # Ajusta el import según tu proyecto

class CutModule(QWidget):
    """
    Módulo que encapsula el widget de controles de corte de video
    y maneja la interacción con el servicio de video (VideoService).
    """
    
    def __init__(self, video_service: VideoService, parent=None):
        super().__init__(parent)
        self.video_service = video_service

        self._setup_ui()
        self._connect_signals()

    # --- UI ---
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Instanciar widget de controles
        self.cut_controls = CutControlsWidget(self)
        main_layout.addWidget(self.cut_controls)
        main_layout.addStretch(1)

    # --- Conexión de señales ---
    def _connect_signals(self):
        # Botones "u" del widget
        self.cut_controls.start_use_current_time_request.connect(self._use_current_start_time)
        self.cut_controls.end_use_current_time_request.connect(self._use_current_end_time)
        self.cut_controls.freeze_use_current_time_request.connect(self._use_current_freeze_time)

        # Botón "Guardar Clip"
        self.cut_controls.save_clip_request.connect(self._save_clip)

    # --- Slots internos ---
    @Slot()
    def _use_current_start_time(self):
        """Usa el tiempo actual del video como inicio del rango."""
        current_msec = self.video_service.get_current_time()
        time_str = self._format_msec(current_msec)
        self.cut_controls.set_display_start_time(current_msec, time_str)

    @Slot()
    def _use_current_end_time(self):
        """Usa el tiempo actual del video como fin del rango."""
        current_msec = self.video_service.get_current_time()
        time_str = self._format_msec(current_msec)
        self.cut_controls.set_display_end_time(current_msec, time_str)
        
    @Slot()
    def _use_current_freeze_time(self):
        """Usa el tiempo actual del video como fin del rango."""
        current_msec = self.video_service.get_current_time()
        time_str = self._format_msec(current_msec)
        self.cut_controls.set_display_freeze_time(current_msec, time_str)

    @Slot(int, int)
    def _save_clip(self, start_msec: int, end_msec: int, freeze_msec: int, freeze_duration: int):
      if not self.video_service.is_video_loaded():
        print("No hay video cargado para guardar clip.")
        return

      # Generar nombre por defecto
      output_filename = None  # VideoService lo genera automáticamente
      self.video_service.save_video_clip(start_msec, end_msec, freeze_msec, freeze_duration, output_filename)

    # --- Helper ---
    def _format_msec(self, msec: int) -> str:
        """Formatea milisegundos a HH:MM:SS:MS o MM:SS:MS."""
        milliseconds = msec % 1000
        total_seconds = msec // 1000
        seconds = total_seconds % 60
        minutes = (total_seconds // 60) % 60
        hours = total_seconds // 3600
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
        return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"

    # --- Getter ---
    def get_controls(self) -> CutControlsWidget:
        return self.cut_controls
