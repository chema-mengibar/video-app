# src/app/ui/widgets/video_area_widget.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QComboBox, 
    QFileDialog, QApplication, QStyle
)
from PySide6.QtGui import QIcon 
from PySide6.QtCore import Qt, Signal, Slot, QSize

# Importaciones de los componentes internos y features
from ui.components.timeline_ruler import TimelineRuler
from features.draw.drawing_label import DrawingVideoLabel
from services.video_service import VideoService # Para el helper format_time

class VideoAreaWidget(QWidget):
    """
    Componente UI principal que contiene la vista de video, la regla de tiempo y los controles.
    Emite señales para que el coordinador (MainWindow) interactúe con los Servicios.
    """
    
    # Señales para las acciones del usuario que requieren el VideoService
    load_video_request = Signal()
    play_pause_request = Signal(bool) # True for play, False for pause
    seek_slider_moved = Signal(int)
    seek_slider_released = Signal(int)
    quality_changed = Signal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Construye la UI del área de video."""
        video_v_layout = QVBoxLayout(self)
        
        # Video Label (Canvas de Dibujo)
        self.video_label = DrawingVideoLabel() 
        video_v_layout.addWidget(self.video_label)
        
        # Ruler
        self.ruler_widget = TimelineRuler()
        video_v_layout.addWidget(self.ruler_widget)
        
        # Slider
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 1)
        self.timeline_slider.setSingleStep(100)
        self.timeline_slider.setEnabled(False)
        video_v_layout.addWidget(self.timeline_slider)
        
        # Barra de Controles
        control_bar = QWidget()
        control_h_layout = QHBoxLayout(control_bar)
        control_h_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_play = QPushButton()
        self.btn_play.setIcon(QApplication.style().standardIcon(QStyle.SP_MediaPlay))
        self.btn_play.setIconSize(QSize(12, 12))

        self.btn_pause = QPushButton()
        self.btn_pause.setIcon(QApplication.style().standardIcon(QStyle.SP_MediaPause))
        self.btn_pause.setIconSize(QSize(12, 12))
        self.btn_pause.setToolTip("Pause")


        self.btn_screenshot = QPushButton()
        self.btn_screenshot.setIcon(QIcon("assets/icons/photo-camera.svg"))
        self.btn_screenshot.setIconSize(QSize(12, 12))
        self.btn_screenshot.setToolTip("Screenshot")


        self.btn_add_bookmark = QPushButton()
        self.btn_add_bookmark.setIcon(QIcon("assets/icons/bookmark-plus.svg"))
        self.btn_add_bookmark.setIconSize(QSize(12, 12))
        self.btn_add_bookmark.setToolTip("Mark")


        self.time_label = QLabel(VideoService.format_time(0) + " / " + VideoService.format_time(0))
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItem("High (1x)", 1.0)
        self.quality_combo.addItem("Medium (0.5x)", 0.5)
        self.quality_combo.addItem("Low (0.1x)", 0.1)
        

        control_h_layout.addWidget(self.btn_play)
        control_h_layout.addWidget(self.btn_pause)
        control_h_layout.addWidget(self.time_label)
        control_h_layout.addStretch()
        control_h_layout.addWidget(self.quality_combo)
        control_h_layout.addWidget(self.btn_screenshot)
        control_h_layout.addWidget(self.btn_add_bookmark)
        
        video_v_layout.addWidget(control_bar)

    def _connect_signals(self):
        """Conecta los widgets a las señales de salida del componente."""
        self.btn_play.clicked.connect(lambda: self.play_pause_request.emit(True))
        self.btn_pause.clicked.connect(lambda: self.play_pause_request.emit(False))
        self.timeline_slider.sliderMoved.connect(self.seek_slider_moved)
        self.timeline_slider.sliderReleased.connect(lambda: self.seek_slider_released.emit(self.timeline_slider.value()))
        self.quality_combo.currentIndexChanged.connect(lambda index: self.quality_changed.emit(self.quality_combo.itemData(index)))
        
        # Monkey patch para la rueda del slider (seek)
        def monkey_patch_slider_wheel(event):
            if not self.timeline_slider.isEnabled(): return
            delta = event.angleDelta().y()
            step = 100 
            new_value = self.timeline_slider.value() + (step if delta > 0 else -step)
            new_value = max(self.timeline_slider.minimum(), min(self.timeline_slider.maximum(), new_value))
            self.timeline_slider.setValue(new_value)
            self.seek_slider_released.emit(new_value) # Actúa como seek
            event.accept()
        self.timeline_slider.wheelEvent = monkey_patch_slider_wheel

    # Acceso a widgets internos para que MainWindow pueda inyectar datos o conectar señales
    def get_drawing_label(self) -> DrawingVideoLabel:
        return self.video_label

    def get_ruler_widget(self) -> TimelineRuler:
        return self.ruler_widget

    def get_slider(self) -> QSlider:
        return self.timeline_slider
        
    def get_time_label(self) -> QLabel:
        return self.time_label
        
    def get_add_bookmark_button(self) -> QPushButton:
        """[CORRECCIÓN] Getter añadido para el botón de Bookmark."""
        return self.btn_add_bookmark
        
    def set_controls_enabled(self, enabled: bool):
        """Habilita/deshabilita los controles de reproducción."""
        self.timeline_slider.setEnabled(enabled)
        self.btn_play.setEnabled(enabled)
        self.btn_pause.setEnabled(enabled) 
        self.btn_screenshot.setEnabled(enabled)
        self.btn_add_bookmark.setEnabled(enabled)

    @Slot(int, int)
    def update_time_display(self, current_msec: int, duration_msec: int):
        """Actualiza la etiqueta y el slider de tiempo (para llamadas externas)."""
        self.time_label.setText(VideoService.format_time(current_msec) + " / " + VideoService.format_time(duration_msec))
        if not self.timeline_slider.isSliderDown():
            self.timeline_slider.setValue(current_msec)