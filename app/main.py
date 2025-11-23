# main.py (Contiene la clase VideoPlayerApp y la lógica de arranque)

import sys
import cv2 
import os # <-- ¡Debe estar aquí!
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, 
    QVBoxLayout, QHBoxLayout, QSizePolicy, QSlider, QComboBox, 
    QMainWindow, QToolBar, QStackedWidget, QGridLayout, QFileDialog, QLineEdit 
)
# Asegurar la importación de Qt
from PySide6.QtCore import Qt, QSize, Slot 
from PySide6.QtGui import QImage, QPixmap , QColor

# Modulos de Lógica
from video_logic import VideoPlayerController
from theme import DarkTheme 

# Modulos de Features (features/ tiene que existir)
from features.videomarks import BookmarksModule 
# Asumiendo que ahora es features/drawing.py o ui_widgets.py
from features.draw_manager import DrawManager 
from features.drawing import DrawingVideoLabel # Usamos el nombre del último archivo
from ui_widgets import TimelineRuler # Asumiendo TimelineRuler está aquí


# ----------------------------------------------------------------------
# APLICACIÓN PRINCIPAL
# ----------------------------------------------------------------------

class VideoPlayerApp(QMainWindow): 
    def __init__(self):
        
        super().__init__()
        
        self.controller = VideoPlayerController()
        self.worker = self.controller.worker
        self.worker_thread = self.controller.worker_thread
        
        # Sincronizamos las variables de estado desde el controlador
        self.is_video_loaded = self.controller.is_video_loaded
        self.duration_msec = self.controller.duration_msec
        self.scale_factor = self.controller.scale_factor

        # Inicializa módulos de features
        self.draw_manager = DrawManager()
        
        self.setWindowTitle("Reproductor de Video Modular")
        self.setGeometry(100, 100, 1400, 800) 
        
        self.setup_ui()
        self.initialize_logic()
        self.connect_ui_to_logic()

    def select_drawing_color(self):
        """Abre un QColorDialog y actualiza el color del pincel y el botón."""
        from PySide6.QtWidgets import QColorDialog
        
        color = QColorDialog.getColor(self.current_pen_color)
        
        if color.isValid():
            self.current_pen_color = color
            
            # 1. Actualizar el color del botón (estética)
            hex_color = color.name()
            self.btn_color_pick.setStyleSheet(f"background-color: {hex_color}; color: white; padding: 6px 10px; border-radius: 4px;")
            
            # 2. Informar al DrawingVideoLabel
            self.video_label.set_pen_color(color)
        
    def initialize_logic(self):
        self.worker_thread.started.connect(self.worker.run)
        
        self.controller.frame_ready_signal.connect(self._display_frame) 
        self.controller.video_loaded_signal.connect(self._handle_video_loaded)
        self.controller.time_updated_signal.connect(self._handle_time_update)
        
        self.worker_thread.start()

    # --- Métodos que llaman al Controller ---
    
    def load_video_file(self):
        self.controller.load_video_file()
        
    def toggle_play_pause(self, play: bool):
        self.controller.toggle_play_pause(play)
        
    @Slot(int) # Necesario si se conecta a signals con int
    def slider_moved(self, value):
        self.controller.slider_moved(value)
        
    def slider_released(self):
        self.controller.slider_released()
        
    def quality_changed(self, index):
        self.controller.quality_changed(index)
        self.scale_factor = self.controller.scale_factor 

    def get_current_time(self):
        return self.controller.get_current_time()
        
    def _format_time(self, msec):
        return self.controller._format_time(msec)
        
    # --- Otros Slots y métodos de UI ---
    def _display_frame(self, frame):
        """Muestra el frame en el QLabel, usando self.scale_factor."""
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        
        # El escalado inicial basado en self.scale_factor sigue siendo útil para rendimiento
        w_scaled = int(w * self.scale_factor) 
        h_scaled = int(h * self.scale_factor)
        
        if self.scale_factor != 1.0:
            rgb_image = cv2.resize(rgb_image, (w_scaled, h_scaled), interpolation=cv2.INTER_LINEAR)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w

        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        # 🟢 CORRECCIÓN CLAVE: Escalar el Pixmap al tamaño del Label, manteniendo el Aspect Ratio.
        if not self.video_label.size().isEmpty():
            # 1. Obtener el tamaño actual del widget donde se mostrará.
            target_size = self.video_label.size()
            
            # 2. Escalar el Pixmap al tamaño objetivo, MANTENIENDO EL ASPECTO.
            scaled_pixmap = pixmap.scaled(
                target_size, 
                Qt.KeepAspectRatio, # <--- ¡Esto es lo que evita la deformación!
                Qt.SmoothTransformation
            )
            
            # 3. Establecer el Pixmap escalado.
            self.video_label.setPixmap(scaled_pixmap)
            
            # 4. Ajustar el tamaño del label para que coincida con el Pixmap (opcional, pero ayuda a centrar)
            # Como el label ya es expanding, solo necesitamos asegurarnos de que la imagen se centre.
            # Al no tener setScaledContents(True), el pixmap se centrará automáticamente.
        
        else:
            # Caso fallback si el label no tiene tamaño (al inicio)
            self.video_label.setPixmap(pixmap)

    def take_screenshot(self):
        """Toma una captura de pantalla del frame actual mostrado y lo guarda."""
        if not self.is_video_loaded:
            print("Cannot take screenshot: No video loaded.")
            return

        pixmap = self.video_label.pixmap() 
        
        if pixmap is None or pixmap.isNull():
            print("Cannot take screenshot: No frame displayed.")
            return

        default_filename = f"screenshot_{self.get_current_time()}.png"
        path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Screenshot", 
            default_filename, 
            "PNG Files (*.png);;All Files (*)"
        )

        if path:
            pixmap.save(path, "png")
            print(f"Screenshot saved to: {path}")

    def save_current_drawing(self):
        """Guarda el dibujo actual del canvas con la duración especificada."""
        
        if not self.is_video_loaded: 
            print("No video loaded to save drawing time against.")
            return

        try:
            duration = int(self.drawing_duration_input.text())
            if duration <= 0: duration = 2000 
        except ValueError:
            duration = 2000 
            
        current_time = self.get_current_time()
        paths_to_save = self.video_label.get_finished_paths()
        
        if paths_to_save:
            self.draw_manager.add_drawing_entry(current_time, duration, paths_to_save)
            self.video_label.update()
    
    # -----------------------------------------------------------------
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.setStyleSheet(DarkTheme.GLOBAL_STYLES)
        main_h_layout = QHBoxLayout(central_widget)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.setSpacing(5)

        # 🟢 CORRECCIÓN: Definición de video_v_layout (Faltaba en la versión anterior)
        # A. CONTENEDOR DE VIDEO Y CONTROLES
        video_area_container = QWidget()
        video_area_container.setMaximumWidth(800)
        video_v_layout = QVBoxLayout(video_area_container) 
        video_v_layout.setContentsMargins(10, 10, 10, 10)
        video_v_layout.setSpacing(5)
        # ----------------------------------------------------------

        # 1. TOOLBAR SUPERIOR
        toolbar = QToolBar()
        toolbar.setStyleSheet(DarkTheme.TOOLBAR_STYLES)
        
        self.btn_load = QPushButton("Load Video")
        self.tab_bookmarks = QPushButton("Videomarks") 
        self.tab_draw = QPushButton("Draw")
        
        self.tab_bookmarks.setCheckable(True)
        self.tab_draw.setCheckable(True)
        self.tab_bookmarks.setChecked(True) 
        
        toolbar.addWidget(self.btn_load)
        toolbar.addWidget(self.tab_bookmarks)
        toolbar.addWidget(self.tab_draw)
        
        video_v_layout.addWidget(toolbar)
        
        # 2. Video Label
        self.video_label = DrawingVideoLabel() 
        self.video_label.setText("Cargar Video Aquí")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; color: white;")
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.video_label.setScaledContents(True) 

        

        
        video_v_layout.addWidget(self.video_label)

        # 3. Timeline Slider y Ruler
        timeline_widget = QWidget()
        timeline_layout = QGridLayout(timeline_widget)
        timeline_layout.setContentsMargins(0, 0, 0, 0)
        timeline_layout.setHorizontalSpacing(0)
        timeline_layout.setVerticalSpacing(0)
        
        self.time_label = QLabel("00:00:000 / 00:00:000") 
        self.time_label.setStyleSheet("color: #AAAAAA; font-size: 8pt; background-color: transparent;") 
        timeline_layout.addWidget(self.time_label, 0, 0, alignment=Qt.AlignLeft) 
        
        self.quality_combo = QComboBox() 
        self.quality_combo.addItem("High Quality", 1.0) 
        self.quality_combo.addItem("Medium (50%)", 0.5) 
        self.quality_combo.addItem("Low (25%)", 0.25) 
        timeline_layout.addWidget(self.quality_combo, 0, 2, alignment=Qt.AlignRight) 
        
        self.timeline_slider = QSlider(Qt.Horizontal) 
        self.timeline_slider.setRange(0, 0)
        self.timeline_slider.setEnabled(False)
        self.timeline_slider.setFixedHeight(12) 
        timeline_layout.addWidget(self.timeline_slider, 1, 0, 1, 3) 
        
        self.ruler_widget = TimelineRuler()
        self.ruler_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.ruler_widget.setFixedHeight(10) 
        timeline_layout.addWidget(self.ruler_widget, 2, 0, 1, 3) 
        
        video_v_layout.addWidget(timeline_widget) 

        # 4. Botones de Control
        control_h_layout = QHBoxLayout()
        self.btn_play = QPushButton("Play")
        self.btn_pause = QPushButton("Pause") 
        self.btn_screenshot = QPushButton("Screenshot") 
        self.btn_add_bookmark = QPushButton("Videomark") 
        
        self.btn_play.setEnabled(False); self.btn_pause.setEnabled(False) 
        self.btn_screenshot.setEnabled(False); self.btn_add_bookmark.setEnabled(False)

        control_h_layout.addWidget(self.btn_play)
        control_h_layout.addWidget(self.btn_pause)
        control_h_layout.addStretch(1) 
        control_h_layout.addWidget(self.btn_screenshot)
        control_h_layout.addWidget(self.btn_add_bookmark)
        
        video_v_layout.addLayout(control_h_layout)
        main_h_layout.addWidget(video_area_container, 3) 

        # B. PANEL LATERAL (SIDEBAR)
        self.sidebar = QWidget()
        self.sidebar_v_layout = QVBoxLayout(self.sidebar)
        self.sidebar_v_layout.setContentsMargins(5, 5, 5, 5) 
        self.sidebar_v_layout.setSpacing(5) 
        
        self.sidebar.setMinimumWidth(30)
        self.sidebar.setMaximumWidth(800)
        self.sidebar.setStyleSheet(DarkTheme.SIDEBAR_CONTAINER) 
        
        self.sidebar_header = QWidget()
        header_v_layout = QVBoxLayout(self.sidebar_header)
        header_v_layout.setContentsMargins(0, 0, 0, 0) 
        header_v_layout.setSpacing(2) 
        
        self.sidebar_label = QLabel("Videomarks")
        self.sidebar_label.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 0 0 2px 0;")
        
        header_v_layout.addWidget(self.sidebar_label, alignment=Qt.AlignTop) 
        
        self.sidebar_controls_stack = QStackedWidget()
        
        # Controles de VIDEOMARKS
        self.bookmarks_controls = QWidget()
        bm_controls_layout = QHBoxLayout(self.bookmarks_controls)
        bm_controls_layout.setContentsMargins(0, 0, 0, 0) 
        bm_controls_layout.setSpacing(5)
        
        self.btn_save_bookmarks = QPushButton("Save")
        self.btn_load_bookmarks = QPushButton("Load")
        self.btn_save_bookmarks.setStyleSheet(DarkTheme.SIDEBAR_ACTION_BUTTON)
        self.btn_load_bookmarks.setStyleSheet(DarkTheme.SIDEBAR_ACTION_BUTTON)
        
        bm_controls_layout.addWidget(self.btn_save_bookmarks)
        bm_controls_layout.addWidget(self.btn_load_bookmarks)
        bm_controls_layout.addStretch(1)
        
        self.btn_close_sidebar = QPushButton("X")
        self.btn_close_sidebar.setFixedSize(QSize(20, 20))
        self.btn_close_sidebar.setStyleSheet(DarkTheme.CLOSE_BUTTON)
        bm_controls_layout.addWidget(self.btn_close_sidebar)
        
        # Controles de DRAW
        self.draw_controls = QWidget()
        draw_controls_layout = QHBoxLayout(self.draw_controls)
        draw_controls_layout.setContentsMargins(0, 0, 0, 0)
        draw_controls_layout.setSpacing(5)
        
        self.btn_toggle_draw = QPushButton("Enable Drawing")
        self.btn_clear_draw = QPushButton("Clear Canvas")
        self.btn_save_drawing = QPushButton("Save Drawing") 
        self.drawing_duration_input = QLineEdit("2000") 
        
        self.btn_color_pick = QPushButton("Color")
        self.btn_color_pick.setStyleSheet("background-color: red; color: white; padding: 6px 10px; border-radius: 4px;")
        self.current_pen_color = QColor(255, 0, 0) # Inicialmente rojo


        self.drawing_duration_input.setPlaceholderText("Duration (ms)")
        self.drawing_duration_input.setFixedWidth(60)

        self.btn_toggle_draw.setStyleSheet(DarkTheme.SIDEBAR_ACTION_BUTTON)
        self.btn_clear_draw.setStyleSheet(DarkTheme.SIDEBAR_ACTION_BUTTON_SMALL)
        self.btn_save_drawing.setStyleSheet(DarkTheme.SIDEBAR_ACTION_BUTTON)
        
        draw_controls_layout.addWidget(self.btn_toggle_draw)
        draw_controls_layout.addWidget(self.btn_clear_draw)
        draw_controls_layout.addWidget(self.drawing_duration_input)
        draw_controls_layout.addWidget(self.btn_save_drawing)
        draw_controls_layout.addWidget(self.btn_color_pick)
        
        draw_controls_layout.addStretch(1)

        self.btn_close_sidebar_draw = QPushButton("X")
        self.btn_close_sidebar_draw.setFixedSize(QSize(20, 20))
        self.btn_close_sidebar_draw.setStyleSheet(DarkTheme.CLOSE_BUTTON)
        draw_controls_layout.addWidget(self.btn_close_sidebar_draw)


        self.sidebar_controls_stack.addWidget(self.bookmarks_controls) 
        self.sidebar_controls_stack.addWidget(self.draw_controls) 

        header_v_layout.addWidget(self.sidebar_controls_stack, alignment=Qt.AlignTop)
        header_v_layout.addStretch(1) 
        
        self.sidebar_v_layout.addWidget(self.sidebar_header)

        self.sidebar_body_stack = QStackedWidget()
        
        # El módulo de bookmarks necesita una referencia a la aplicación principal (self)
        self.bookmarks_module = BookmarksModule(self) 
        self.draw_list_placeholder = QLabel("Drawings will be listed here.")
        
        self.sidebar_body_stack.addWidget(self.bookmarks_module) 
        self.sidebar_body_stack.addWidget(self.draw_list_placeholder)

        self.sidebar_v_layout.addWidget(self.sidebar_body_stack, 1) 
        
        main_h_layout.addWidget(self.sidebar, 1)

    def connect_ui_to_logic(self):
        
        # --- Conexiones Funcionales (Usando self.controller) ---
        self.btn_load.clicked.connect(self.load_video_file)
        self.btn_play.clicked.connect(lambda checked: self.toggle_play_pause(True))
        self.btn_pause.clicked.connect(lambda checked: self.toggle_play_pause(False))
        self.btn_screenshot.clicked.connect(self.take_screenshot) 
        self.btn_add_bookmark.clicked.connect(lambda: self.bookmarks_module.add_current_time_bookmark(label="Videomark"))
        
        # Conexiones de Timeline
        self.timeline_slider.sliderMoved.connect(self.slider_moved)
        self.timeline_slider.sliderReleased.connect(self.slider_released)
        self.quality_combo.currentIndexChanged.connect(self.quality_changed)
        
        # 🟢 FUNCIÓN LOCAL: Sobrescribir el wheelEvent del slider
        def monkey_patch_slider_wheel(event):
            
            if not self.timeline_slider.isEnabled():
                return
                
            delta = event.angleDelta().y()
            step = 100 # Saltaremos 100 milisegundos
            
            current_value = self.timeline_slider.value()
            
            if delta > 0:
                new_value = current_value + step
            else:
                new_value = current_value - step
                
            new_value = max(self.timeline_slider.minimum(), min(self.timeline_slider.maximum(), new_value))
            
            # 1. Actualizar visualmente el slider
            self.timeline_slider.setValue(new_value)
            
            # 2. Llamar directamente al método seek del controlador
            self.controller.seek(new_value)
            
            event.accept()

        # Inyectar la función como el manejador de eventos de rueda del slider
        self.timeline_slider.wheelEvent = monkey_patch_slider_wheel
        
        # 🟢 CONEXIÓN DE MARKS (Para actualizar los rectángulos de la regla)
        self.bookmarks_module.marks_changed.connect(self.update_ruler_marks) 
        
        # Conexiones de Dibujo
        self.btn_toggle_draw.clicked.connect(self._toggle_drawing_ui)
        self.btn_clear_draw.clicked.connect(self.video_label.clear_drawing)
        self.btn_save_drawing.clicked.connect(self.save_current_drawing) 
        self.btn_color_pick.clicked.connect(self.select_drawing_color)

        # CONEXIONES: Save/Load Videomarks
        self.btn_save_bookmarks.clicked.connect(
            lambda: self.open_save_dialog(self.bookmarks_module, "Videomarks")
        )
        self.btn_load_bookmarks.clicked.connect(
            lambda: self.open_load_dialog(self.bookmarks_module, "Videomarks")
        )
        
        # --- LÓGICA DE PESTAÑAS Y SIDEBAR ---
        def show_view(index, title, tab_to_check, tab_to_uncheck):
            if not self.sidebar.isVisible():
                 self.sidebar.show() 
            
            self.sidebar_body_stack.setCurrentIndex(index)
            self.sidebar_controls_stack.setCurrentIndex(index)
            self.sidebar_label.setText(title)
            
            tab_to_check.setChecked(True)
            tab_to_uncheck.setChecked(False)
            
            if index == 1: 
                is_enabled = self.video_label.drawing_enabled
                self.btn_toggle_draw.setText("Disable Drawing (Active)" if is_enabled else "Enable Drawing")
                self.btn_toggle_draw.setStyleSheet("background-color: #AA0000; color: white; padding: 6px 10px; border-radius: 4px;" if is_enabled else DarkTheme.SIDEBAR_ACTION_BUTTON)
            else:
                 self.video_label.enable_drawing(False)
                 
        self.tab_bookmarks.clicked.connect(lambda: show_view(
            0, "Videomarks", self.tab_bookmarks, self.tab_draw
        ))

        self.tab_draw.clicked.connect(lambda: show_view(
            1, "Draw Tool", self.tab_draw, self.tab_bookmarks
        ))
        
        self.btn_close_sidebar.clicked.connect(self.sidebar.hide)
        self.btn_close_sidebar_draw.clicked.connect(self.sidebar.hide)
        self.tab_bookmarks.toggled.connect(lambda checked: self.sidebar.setVisible(checked or self.tab_draw.isChecked()))
        self.tab_draw.toggled.connect(lambda checked: self.sidebar.setVisible(checked or self.tab_bookmarks.isChecked()))
        
    def _toggle_drawing_ui(self):
        is_enabled = not self.video_label.drawing_enabled
        self.video_label.enable_drawing(is_enabled)
        
        if is_enabled:
            self.btn_toggle_draw.setText("Disable Drawing (Active)")
            self.btn_toggle_draw.setStyleSheet("background-color: #AA0000; color: white; padding: 6px 10px; border-radius: 4px;")
        else:
            self.btn_toggle_draw.setText("Enable Drawing")
            self.btn_toggle_draw.setStyleSheet(DarkTheme.SIDEBAR_ACTION_BUTTON)

    @Slot()
    def update_ruler_marks(self):
        self.ruler_widget.mark_times = self.bookmarks_module.get_mark_times()
        self.ruler_widget.update()
        
    @Slot(bool, int)
    def _handle_video_loaded(self, success, duration_msec):
        # Sincronizar el estado local con el controlador
        self.is_video_loaded = success
        self.duration_msec = duration_msec
        
        if success:
            self.timeline_slider.setRange(0, int(duration_msec))
            self.timeline_slider.setValue(0)
            self.timeline_slider.setEnabled(True)
            
            self.ruler_widget.duration_msec = duration_msec
            self.update_ruler_marks()
            
            self.btn_play.setEnabled(True)
            self.btn_pause.setEnabled(True)
            self.btn_screenshot.setEnabled(True)
            self.btn_add_bookmark.setEnabled(True)
            
            self.time_label.setText(self._format_time(0) + " / " + self._format_time(duration_msec))
            self.bookmarks_module.update_list_ui(0) 
        else:
            self.timeline_slider.setRange(0, 0)
            self.timeline_slider.setEnabled(False)
            self.ruler_widget.duration_msec = 0
            self.ruler_widget.update()
            
            self.btn_play.setEnabled(False)
            self.btn_pause.setEnabled(False)
            self.btn_screenshot.setEnabled(False)
            self.btn_add_bookmark.setEnabled(False)
            self.time_label.setText("00:00:000 / 00:00:000")
            
    def open_save_dialog(self, module, name):
        
        # 🟢 Lógica de ruta por defecto
        default_dir = ""
        if self.controller.video_directory:
            default_dir = self.controller.video_directory
        
        default_filename = os.path.join(default_dir, f"{name.lower()}.json")

        file_dialog = QFileDialog(self, f"Save {name} Data", default_filename, "JSON Files (*.json)")
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        
        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            if not selected_file.lower().endswith('.json'):
                selected_file += '.json'
            
            if hasattr(module, 'save_data_to_file'):
                module.save_data_to_file(selected_file)

    def open_load_dialog(self, module, name):
        
        # 🟢 Lógica de ruta por defecto
        default_dir = ""
        if self.controller.video_directory:
            default_dir = self.controller.video_directory
        
        default_filename = os.path.join(default_dir, f"{name.lower()}.json")

        file_dialog = QFileDialog(self, f"Load {name} Data", default_filename, "JSON Files (*.json)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        
        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            if hasattr(module, 'load_data_from_file'):
                module.load_data_from_file(selected_file)

    def closeEvent(self, event):
        
        self.controller.stop_thread() 
        
        self.worker_thread.quit()
        
        if not self.worker_thread.wait(5000): 
            self.worker_thread.terminate()
            
        event.accept()

    def _handle_time_update(self, current_msec):
        """Actualiza la UI con el tiempo, incluyendo los dibujos activos."""
        
        # Sincronizar duración local
        self.duration_msec = self.controller.duration_msec 
        
        self.time_label.setText(self._format_time(current_msec) + " / " + self._format_time(self.duration_msec))
        
        # NOTA: Solo actualizamos el slider si no está siendo arrastrado (para evitar saltos)
        # Esto incluye el arrastre manual y la búsqueda con la rueda del ratón.
        if not self.timeline_slider.isSliderDown():
            self.timeline_slider.setValue(current_msec)
            
        self.ruler_widget.current_msec = current_msec
        self.ruler_widget.update()
        
        self.bookmarks_module.update_list_ui(current_msec)
        
        # LÓGICA DE DIBUJO TEMPORAL
        active_paths = self.draw_manager.get_active_drawing_paths(current_msec)
        self.video_label.set_active_paths(active_paths) 
        self.video_label.update()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayerApp()
    window.show()
    sys.exit(app.exec())