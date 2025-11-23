# src/app/ui/main_window.py

import sys
import cv2 
import os 
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, 
    QVBoxLayout, QHBoxLayout, QSizePolicy, QSlider, QComboBox, 
    QMainWindow, QToolBar, QStackedWidget, QGridLayout, QFileDialog, QLineEdit, QColorDialog
)
from PySide6.QtCore import Qt, QSize, Slot, QTimer
from PySide6.QtGui import QImage, QPixmap , QColor, QIcon

# Importaciones de la nueva arquitectura (solo servicios y componentes UI)
from ui.styles.theme import DarkTheme 
from ui.components.timeline_ruler import TimelineRuler 

# Importamos las dependencias (Servicios y Features)
from services.video_service import VideoService 
from services.draw_service import DrawService
from features.draw.drawing_label import DrawingVideoLabel
from features.timeline.videomarks_module import BookmarksModule

class MainWindow(QMainWindow): 
    """
    Ventana principal de la aplicación. Responsable solo de la UI y el flujo de control,
    no de la lógica de negocio.
    """
    def __init__(self, video_service: VideoService, draw_service: DrawService, parent=None):
        super().__init__(parent)
        
        # Inyección de Dependencias (Servicios)
        self.video_service = video_service
        self.draw_service = draw_service
        
        # Helpers de estado
        self.is_video_loaded = False
        self.duration_msec = 0
        self.current_video_directory = None
        self.current_pen_color = QColor(255, 0, 0) # Color inicial (rojo)

        self.setWindowTitle("Reproductor de Video Modular")
        self.setGeometry(100, 100, 1400, 800) 
        
        self.setup_ui()
        self.connect_ui_to_services()

    # --- Métodos de Ayuda (Delegación) ---
    @staticmethod
    def format_time(msec):
        """Delegación al helper estático del servicio de video."""
        return VideoService.format_time(msec)

    # --- Lógica UI y Eventos ---

    def _select_video_file(self):
        """Abre el diálogo y delega la carga al servicio."""
        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Video File", 
            os.path.expanduser("~"), 
            "Video Files (*.mp4 *.avi *.mov);;All Files (*)"
        )
        if path:
            self.video_service.load_video_file(path)
            
    # 🟢 MÉTODO FALTANTE AÑADIDO
    @Slot()
    def select_drawing_color(self):
        """Abre el diálogo de color y actualiza el estado de la UI y el DrawingLabel."""
        color = QColorDialog.getColor(self.current_pen_color, self, "Select Pen Color")
        if color.isValid():
            self.current_pen_color = color
            hex_color = color.name()
            # Actualizar el estilo del botón para reflejar el nuevo color
            self.btn_color_pick.setStyleSheet(f"background-color: {hex_color}; color: white; padding: 6px 10px; border-radius: 4px;")
            # Actualizar el color en el widget de dibujo
            self.video_label.set_pen_color(color)

    @Slot()
    def save_current_drawing(self):
        """Guarda el dibujo actual del canvas delegando al DrawService."""
        if not self.is_video_loaded: 
            print("No video loaded to save drawing time against.")
            return

        try:
            duration = int(self.drawing_duration_input.text()) 
            if duration <= 0: duration = 2000 
        except (AttributeError, ValueError):
            duration = 2000 
            
        current_time = self.video_service.get_current_time()
        paths_to_save = self.video_label.get_finished_paths()
        
        if paths_to_save:
            # Delegación al DrawService
            self.draw_service.save_drawing(current_time, duration, paths_to_save)
            self.video_label.update()
            print(f"Dibujo guardado para {self.format_time(current_time)}")

    # --- Slots (Receptores de Señales del Servicio) ---
    
    @Slot(object)
    def display_frame(self, frame):
        """Muestra el frame en el QLabel, asegurando el aspecto ratio."""
        if frame is None: return

        # Conversión de cv2 (BGR) a QImage (RGB)
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        # Escalar para encajar en el QLabel manteniendo el aspect ratio
        if not self.video_label.size().isEmpty():
            target_size = self.video_label.size()
            scaled_pixmap = pixmap.scaled(
                target_size, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.video_label.setPixmap(scaled_pixmap)
        else:
            self.video_label.setPixmap(pixmap)


    @Slot(int)
    def handle_time_update(self, current_msec):
        """Actualiza la UI con el tiempo, incluyendo los dibujos activos."""
        self.time_label.setText(self.format_time(current_msec) + " / " + self.format_time(self.duration_msec))
        
        # Sincronización del Slider
        if not self.timeline_slider.isSliderDown():
            self.timeline_slider.setValue(current_msec)
            
        # Sincronización del Ruler
        self.ruler_widget.current_msec = current_msec
        self.ruler_widget.update()
        
        # LÓGICA DE DIBUJO: Preguntar al DrawService qué paths mostrar
        active_paths = self.draw_service.get_paths_at_time(current_msec)
        self.video_label.set_active_paths(active_paths) 
        self.video_label.update()
        

    @Slot(bool, int, str)
    def handle_video_loaded(self, success, duration_msec, video_directory):
        """Sincroniza el estado de la UI tras la carga del video."""
        self.is_video_loaded = success
        self.duration_msec = duration_msec
        self.current_video_directory = video_directory

        # Configurar y habilitar controles
        self.timeline_slider.setRange(0, int(duration_msec))
        self.timeline_slider.setValue(0)
        self.timeline_slider.setEnabled(success)
        self.ruler_widget.duration_msec = duration_msec
        self.ruler_widget.update()
        
        self.btn_play.setEnabled(success); self.btn_pause.setEnabled(success) 
        self.btn_screenshot.setEnabled(success); self.btn_add_bookmark.setEnabled(success)
        
        self.time_label.setText(self.format_time(0) + " / " + self.format_time(duration_msec))
        
        # Intentar cargar datos de features asociados al directorio del video
        self.load_associated_data()
    
    @Slot()
    def update_ruler_marks(self):
        """Actualiza el ruler con las marcas obtenidas del BookmarksModule."""
        mark_times = self.bookmarks_module.get_mark_times()
        self.ruler_widget.update_bookmarks(mark_times)

    # --- Configuración de UI ---
    
    def setup_ui(self):
        """Construye todos los elementos de la interfaz de usuario."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.setStyleSheet(DarkTheme.GLOBAL_STYLES)
        main_h_layout = QHBoxLayout(central_widget)
        
        # --- Área de Video ---
        video_area_container = QWidget()
        video_v_layout = QVBoxLayout(video_area_container)
        
        # Video Label (nuestro widget de dibujo)
        self.video_label = DrawingVideoLabel() 
        self.video_label.setObjectName("video_label")
        # Asegurar que el color inicial se configure en el label
        self.video_label.set_pen_color(self.current_pen_color) 
        video_v_layout.addWidget(self.video_label)
        
        # Ruler y Slider
        self.ruler_widget = TimelineRuler()
        video_v_layout.addWidget(self.ruler_widget)
        
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 1)
        self.timeline_slider.setSingleStep(100)
        self.timeline_slider.setEnabled(False)
        video_v_layout.addWidget(self.timeline_slider)
        
        # Barra de Controles
        control_bar = QWidget()
        control_h_layout = QHBoxLayout(control_bar)
        control_h_layout.setContentsMargins(0, 0, 0, 0)

        # Botones
        self.btn_load = QPushButton("📂 Load")
        self.btn_play = QPushButton("▶️ Play")
        self.btn_pause = QPushButton("⏸️ Pause")
        self.btn_screenshot = QPushButton("📷 Screenshot")
        self.btn_add_bookmark = QPushButton("🔖 Mark")
        self.time_label = QLabel(self.format_time(0) + " / " + self.format_time(0))
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItem("High (1x)", 1.0)
        self.quality_combo.addItem("Medium (0.5x)", 0.5)
        self.quality_combo.addItem("Low (0.1x)", 0.1)
        
        control_h_layout.addWidget(self.btn_load)
        control_h_layout.addWidget(self.btn_play)
        control_h_layout.addWidget(self.btn_pause)
        control_h_layout.addWidget(self.time_label)
        control_h_layout.addStretch()
        control_h_layout.addWidget(self.quality_combo)
        control_h_layout.addWidget(self.btn_screenshot)
        control_h_layout.addWidget(self.btn_add_bookmark)
        
        video_v_layout.addWidget(control_bar)
        
        main_h_layout.addWidget(video_area_container, 4)

        # --- Sidebar ---
        sidebar = QWidget()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet(DarkTheme.SIDEBAR_CONTAINER)
        sidebar_v_layout = QVBoxLayout(sidebar)
        
        # Pestañas de Features
        tab_bar = QWidget()
        tab_h_layout = QHBoxLayout(tab_bar)
        tab_h_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_tab_bookmarks = QPushButton("Bookmarks")
        self.btn_tab_draw = QPushButton("Drawing Controls")
        
        tab_h_layout.addWidget(self.btn_tab_bookmarks)
        tab_h_layout.addWidget(self.btn_tab_draw)
        sidebar_v_layout.addWidget(tab_bar)
        
        # Stacked Widget para el contenido de las pestañas
        self.sidebar_body_stack = QStackedWidget()
        
        # 1. Bookmarks Module
        self.bookmarks_module = BookmarksModule(self.video_service, self) 
        self.sidebar_body_stack.addWidget(self.bookmarks_module) 
        
        # 2. Drawing Controls
        draw_controls_widget = self._create_drawing_controls()
        self.sidebar_body_stack.addWidget(draw_controls_widget)
        
        sidebar_v_layout.addWidget(self.sidebar_body_stack)
        main_h_layout.addWidget(sidebar, 1)

    def _create_drawing_controls(self):
        """Crea el widget de controles de dibujo."""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        layout.addWidget(QLabel("Enable Drawing:"), 0, 0)
        self.btn_draw_toggle = QPushButton("Toggle")
        self.btn_draw_toggle.setCheckable(True)
        layout.addWidget(self.btn_draw_toggle, 0, 1)
        
        layout.addWidget(QLabel("Pen Color:"), 1, 0)
        self.btn_color_pick = QPushButton("Pick Color")
        # Inicializar el color del botón
        hex_color = self.current_pen_color.name()
        self.btn_color_pick.setStyleSheet(f"background-color: {hex_color}; color: white; padding: 6px 10px; border-radius: 4px;")
        layout.addWidget(self.btn_color_pick, 1, 1)
        
        layout.addWidget(QLabel("Duration (ms):"), 2, 0)
        self.drawing_duration_input = QLineEdit("2000")
        layout.addWidget(self.drawing_duration_input, 2, 1)
        
        self.btn_save_drawing = QPushButton("💾 Save Current Draw")
        layout.addWidget(self.btn_save_drawing, 3, 0, 1, 2)
        
        self.btn_clear_canvas = QPushButton("🗑️ Clear Canvas")
        layout.addWidget(self.btn_clear_canvas, 4, 0, 1, 2)

        layout.setRowStretch(5, 1)
        return widget
        
    def connect_ui_to_services(self):
        
        # 1. Conexiones del Servicio de Video
        self.video_service.frame_ready_signal.connect(self.display_frame)
        self.video_service.time_updated_signal.connect(self.handle_time_update)
        self.video_service.video_loaded_signal.connect(self.handle_video_loaded)

        # 2. Conexiones de Controles (Invocación al Servicio)
        self.btn_load.clicked.connect(self._select_video_file)
        self.btn_play.clicked.connect(lambda: self.video_service.toggle_play_pause(True))
        self.btn_pause.clicked.connect(lambda: self.video_service.toggle_play_pause(False))
        self.timeline_slider.sliderMoved.connect(self.video_service.slider_moved)
        self.timeline_slider.sliderReleased.connect(self.video_service.slider_released)
        self.quality_combo.currentIndexChanged.connect(lambda index: self.video_service.set_quality(self.quality_combo.itemData(index)))
        
        # Monkey patch para la rueda del slider (seek)
        def monkey_patch_slider_wheel(event):
            if not self.timeline_slider.isEnabled(): return
            delta = event.angleDelta().y()
            step = 100 
            new_value = self.timeline_slider.value() + (step if delta > 0 else -step)
            new_value = max(self.timeline_slider.minimum(), min(self.timeline_slider.maximum(), new_value))
            self.timeline_slider.setValue(new_value)
            self.video_service.seek(new_value) # Invocación al servicio
            event.accept()
        self.timeline_slider.wheelEvent = monkey_patch_slider_wheel

        # 3. Conexiones de Pestañas
        self.btn_tab_bookmarks.clicked.connect(lambda: self.sidebar_body_stack.setCurrentIndex(0))
        self.btn_tab_draw.clicked.connect(lambda: self.sidebar_body_stack.setCurrentIndex(1))

        # 4. Conexiones de Features
        self.btn_add_bookmark.clicked.connect(lambda: self.bookmarks_module.add_current_time_bookmark())
        self.bookmarks_module.marks_changed.connect(self.update_ruler_marks) # Sincronización Feature -> UI
        
        # Dibujo
        self.btn_draw_toggle.clicked.connect(self.video_label.enable_drawing)
        # 🟢 CONEXIÓN CORREGIDA
        self.btn_color_pick.clicked.connect(self.select_drawing_color) 
        self.btn_save_drawing.clicked.connect(self.save_current_drawing) 
        self.btn_clear_canvas.clicked.connect(self.video_label.clear_drawing)


    # --- Persistencia de Datos Asociados ---
    def load_associated_data(self):
        """Intenta cargar los datos de dibujo y bookmarks automáticamente."""
        if self.current_video_directory:
            draw_path = os.path.join(self.current_video_directory, "drawings.json")
            bm_path = os.path.join(self.current_video_directory, "videomarks.json")
            
            # Cargar DrawService
            self.draw_service.load_data(draw_path)
            
            # Cargar BookmarksModule
            self.bookmarks_module.load_data_from_file(bm_path)
            
            # Forzar actualización del ruler después de cargar bookmarks
            self.update_ruler_marks() 

    def closeEvent(self, event):
        # Asegurar que el servicio de video se detenga limpiamente
        self.video_service.stop_service() 
        event.accept()