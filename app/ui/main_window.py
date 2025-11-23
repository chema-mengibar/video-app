# src/app/ui/main_window.py

import os 
import cv2
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QColorDialog, 
    QFileDialog, QVBoxLayout
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QPixmap 

# Importaciones de la arquitectura modular
from ui.styles.theme import DarkTheme 

# Importamos las dependencias (Servicios y Componentes)
from services.video_service import VideoService 
from core.service_manager import ServiceManager 
from ui.widgets.video_area_widget import VideoAreaWidget
from ui.widgets.sidebar_widget import SidebarWidget
from ui.widgets.topbar_widget import TopBarWidget 
from features.draw.drawing_label import DrawingVideoLabel 

class MainWindow(QMainWindow): 
    """
    Coordinador de la aplicación. Responsable de:
    1. Componer los widgets (TopBar, VideoArea, Sidebar).
    2. Conectar las señales de los Widgets con las acciones de los Servicios.
    3. Delegar la lógica de negocio al ServiceManager.
    """
    def __init__(self, video_service: VideoService, service_manager: ServiceManager, parent=None):
        
        # Inyección de Dependencias: Asignar argumentos ANTES de llamar a super().__init__
        self.video_service = video_service
        self.service_manager = service_manager
        
        # Llamar al constructor de Qt, pasando SOLO el 'parent'
        super().__init__(parent)
        
        # Estado
        self.duration_msec = 0
        self.current_video_directory = None
        
        self.setWindowTitle("Reproductor de Video Modular (Refactorizado)")
        self.setGeometry(100, 100, 1400, 800) 
        self.setStyleSheet(DarkTheme.GLOBAL_STYLES)
        
        self._setup_components()
        self._connect_all()

    # --- Composición de la UI ---
    
    def _setup_components(self):
        """Instancia y organiza los componentes principales de la UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_v_layout = QVBoxLayout(central_widget)
        
        # 1. Top Bar
        self.top_bar = TopBarWidget() 
        main_v_layout.addWidget(self.top_bar)

        # Contenedor para Video Area + Sidebar
        content_h_layout = QHBoxLayout()
        content_h_layout.setContentsMargins(0, 0, 0, 0) 
        
        # 2. Área de Video (4/5 del espacio horizontal)
        self.video_area = VideoAreaWidget()
        content_h_layout.addWidget(self.video_area, 4)

        # 3. Sidebar (1/5 del espacio horizontal)
        initial_color = self.video_area.get_drawing_label().current_pen_color 
        self.sidebar = SidebarWidget(self.video_service, self, initial_color)
        
        # Estado inicial del Sidebar basado en el TopBar (Drawing por defecto)
        is_visible = self.top_bar.btn_toggle_drawing.isChecked() or self.top_bar.btn_toggle_bookmarks.isChecked()
        self.sidebar.setVisible(is_visible) 
        if self.top_bar.btn_toggle_drawing.isChecked():
             self.sidebar.set_current_tab(1) # Drawing es el índice 1

        content_h_layout.addWidget(self.sidebar, 1)

        main_v_layout.addLayout(content_h_layout, 1) # El contenido toma el espacio restante


    # --- Conexión de Señales y Slots ---

    def _connect_all(self):
        """Conecta todas las señales de los widgets a los slots de la MainWindow y los servicios."""
        
        # 1. Conexiones de Servicios a MainWindow (Visualización)
        self.video_service.frame_ready_signal.connect(self.display_frame)
        self.video_service.time_updated_signal.connect(self.handle_time_update)
        self.service_manager.video_loaded_info.connect(self.handle_video_loaded) 

        # 2. Conexiones de la TOP BAR
        self.top_bar.load_video_request.connect(self._select_video_file)
        self.top_bar.toggle_bookmarks_request.connect(
            lambda checked: self._toggle_sidebar_tab(0, checked) # 0 es el índice de Bookmarks
        )
        self.top_bar.toggle_drawing_request.connect(
            lambda checked: self._toggle_sidebar_tab(1, checked) # 1 es el índice de Drawing
        )
        
        # 3. Conexiones del VideoAreaWidget (Acciones del usuario en el reproductor)
        self.video_area.play_pause_request.connect(self.video_service.toggle_play_pause)
        self.video_area.seek_slider_moved.connect(self.video_service.slider_moved)
        self.video_area.seek_slider_released.connect(self.video_service.seek)
        self.video_area.quality_changed.connect(self.video_service.set_quality)
        self.video_area.btn_add_bookmark.clicked.connect(
            lambda: self.sidebar.get_bookmarks_module().add_current_time_bookmark()
        )
        
        # 4. Conexiones del SidebarWidget (Acciones del usuario en la Feature)
        draw_controls = self.sidebar.get_drawing_controls_widget()
        drawing_label = self.video_area.get_drawing_label()
        bookmarks_module = self.sidebar.get_bookmarks_module()

        # Dibujo
        draw_controls.toggle_drawing_signal.connect(drawing_label.enable_drawing)
        draw_controls.clear_canvas_request.connect(drawing_label.clear_drawing)
        draw_controls.color_changed.connect(drawing_label.set_pen_color)
        draw_controls.save_drawing_request.connect(self.save_current_drawing)
        
        # Bookmarks (Sincronización Feature -> UI)
        bookmarks_module.marks_changed.connect(self.update_ruler_marks)
        
    # --- Slots (Coordinación y Delegación) ---

    def _select_video_file(self):
        """Abre el diálogo y delega la carga al VideoService."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Video File", os.path.expanduser("~"), "Video Files (*.mp4 *.avi *.mov);;All Files (*)"
        )
        if path:
            self.video_service.load_video_file(path)

    @Slot()
    def save_current_drawing(self):
        """Coordina la obtención de datos y delega el guardado al ServiceManager."""
        current_time = self.video_service.get_current_time()
        paths_to_save = self.video_area.get_drawing_label().get_finished_paths()
        duration = self.sidebar.get_drawing_controls_widget().get_duration()

        if paths_to_save:
            self.service_manager.save_drawing_data(current_time, duration, paths_to_save)
            self.video_area.get_drawing_label().update()
            print(f"Dibujo guardado para {VideoService.format_time(current_time)}")

    @Slot(bool)
    def _toggle_sidebar_tab(self, index: int, checked: bool):
        """Alterna la visibilidad del sidebar y selecciona la pestaña correcta."""
        if checked:
            # Mostrar el sidebar y cambiar la pestaña
            self.sidebar.setVisible(True)
            self.sidebar.set_current_tab(index)
        else:
            # Ocultar el sidebar si el otro botón no está activo (TopBar maneja el toggle de botones)
            if not self.top_bar.btn_toggle_bookmarks.isChecked() and not self.top_bar.btn_toggle_drawing.isChecked():
                self.sidebar.setVisible(False)

    @Slot(object)
    def display_frame(self, frame):
        """Muestra el frame en el QLabel, asegurando el aspecto ratio."""
        if frame is None: return

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        video_label = self.video_area.get_drawing_label()
        
        if not video_label.size().isEmpty():
            target_size = video_label.size()
            scaled_pixmap = pixmap.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            video_label.setPixmap(scaled_pixmap)
        else:
            video_label.setPixmap(pixmap)


    @Slot(int)
    def handle_time_update(self, current_msec):
        """Actualiza la UI con el tiempo, incluyendo los dibujos activos."""
        self.video_area.update_time_display(current_msec, self.duration_msec)
        
        # Sincronización del Ruler
        ruler = self.video_area.get_ruler_widget()
        ruler.current_msec = current_msec
        ruler.update()
        
        # LÓGICA DE DIBUJO: Preguntar al ServiceManager qué paths mostrar
        active_paths = self.service_manager.get_active_drawing_paths(current_msec)
        self.video_area.get_drawing_label().set_active_paths(active_paths) 
        self.video_area.get_drawing_label().update()
        
    @Slot(bool, int, str)
    def handle_video_loaded(self, success, duration_msec, video_directory):
        """Sincroniza el estado de la UI tras la carga del video."""
        self.duration_msec = duration_msec
        self.current_video_directory = video_directory

        self.video_area.set_controls_enabled(success)
        self.video_area.get_slider().setRange(0, duration_msec)
        self.video_area.get_ruler_widget().duration_msec = duration_msec
        self.video_area.get_ruler_widget().update()
        
        # Cargar datos de bookmarks después de establecer el directorio
        if success and video_directory:
            bm_path = os.path.join(video_directory, "videomarks.json")
            self.sidebar.get_bookmarks_module().load_data_from_file(bm_path)
            self.update_ruler_marks()
            
        self.video_area.update_time_display(0, duration_msec)
    
    @Slot()
    def update_ruler_marks(self):
        """Actualiza el ruler con las marcas obtenidas del BookmarksModule."""
        mark_times = self.sidebar.get_bookmarks_module().get_mark_times()
        self.video_area.get_ruler_widget().update_bookmarks(mark_times)

    # --- Funciones de Qt ---
    
    def closeEvent(self, event):
        self.video_service.stop_service() 
        event.accept()