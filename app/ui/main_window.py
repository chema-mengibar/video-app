import os 
import cv2
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QColorDialog, 
    QFileDialog, QVBoxLayout, QStackedWidget 
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QPixmap 
from ui.styles.theme import DarkTheme 
from services.video_service import VideoService 
from core.service_manager import ServiceManager 
from ui.widgets.video_area_widget import VideoAreaWidget
from ui.widgets.sidebar_widget import SidebarWidget
from ui.widgets.topbar_widget import TopBarWidget 
from features.draw.drawing_label import DrawingVideoLabel 
from features.timeline.videomarks_module import BookmarksModule 


class MainWindow(QMainWindow): 
    """
    Coordinador de la aplicación. Responsable de:
    1. Componer los widgets (TopBar, VideoArea, Sidebar IZQUIERDO y DERECHO).
    2. Conectar las señales de los Widgets con las acciones de los Servicios.
    3. Delegar la lógica de negocio al ServiceManager.
    4. Gestionar el estado central de la UI (active_views).
    """
    
    # Mapeo de vistas del Sidebar a los índices del QStackedWidget interno del Sidebar
    SIDEBAR_VIEW_MAP = {
        'bookmarks': 0,
        'drawing': 1,
        'grids': 2
    }
    
    def __init__(self, video_service: VideoService, service_manager: ServiceManager, parent=None):
        
        # Inyección de Dependencias: 
        self.video_service = video_service
        self.service_manager = service_manager
        
        super().__init__(parent)
        
        # Estado
        self.duration_msec = 0
        self.current_video_directory = None
        
        # 1. ESTADO CENTRAL DE VISTAS 
        self.active_views = {
            'left': 'bookmarks',  # Vista inicial para el sidebar izquierdo
            'right': 'grids',  # Vista inicial para el sidebar derecho
            'center': 'player'
        }
        
        self.setWindowTitle("Reproductor de Video Modular (Refactorizado)")
        self.setGeometry(100, 100, 1400, 800) 

        self._setup_components()
        self._connect_all()
        self.setStyleSheet(DarkTheme.GLOBAL_STYLES)
        
        # Inicializa la UI según el estado central
        self.sidebar_left.setVisible(self.active_views['left'] is not None)
        self.sidebar_right.setVisible(self.active_views['right'] is not None)
        
        # Aseguramos la inicialización del contenido para ambos sidebars si están activos
        if self.active_views['left']:
            self._update_sidebar_content('left', self.active_views['left'])
            
        if self.active_views['right']:
            self._update_sidebar_content('right', self.active_views['right'])
        

    # --- Composición de la UI ---
    
    def _setup_components(self):
        """Instancia y organiza los componentes principales de la UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_v_layout = QVBoxLayout(central_widget)
        main_v_layout.setContentsMargins(0, 0, 0, 0)
        main_v_layout.setSpacing(0)
        
        # 1. Top Bar
        self.top_bar = TopBarWidget() 
        main_v_layout.addWidget(self.top_bar)

        # Contenedor para Sidebar Izquierdo + Video Area + Sidebar Derecho
        content_h_layout = QHBoxLayout()
        content_h_layout.setContentsMargins(0, 0, 0, 0) 
        
        # Inicializamos el video_area primero para obtener el drawing_label y color
        self.video_area = VideoAreaWidget() 
        drawing_label = self.video_area.get_drawing_label()
        initial_color = drawing_label.current_pen_color 

        # Creamos la instancia ÚNICA del BookmarksModule
        self.bookmarks_module = BookmarksModule(
            self.video_service, 
            self
        )


        # 2. Sidebar Izquierdo (1/5 del espacio horizontal)
        self.sidebar_left = SidebarWidget(
            self.video_service, 
            self, # parent_app
            initial_color, 
            'left', # Ubicación
            self.bookmarks_module, # <-- Inyección del widget/lógica real
            self
        )
        content_h_layout.addWidget(self.sidebar_left, 1)
        
        # 3. Área de Video (4/5 del espacio horizontal)
        content_h_layout.addWidget(self.video_area, 4)

        # 4. Sidebar Derecho (1/5 del espacio horizontal)
        self.sidebar_right = SidebarWidget(
            self.video_service, 
            self, # parent_app
            initial_color, 
            'right', # Ubicación
            self.bookmarks_module, # <-- Inyección de la lógica para sincronización
            self
        )
        
        content_h_layout.addWidget(self.sidebar_right, 1)

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
        
        # CONEXIÓN CENTRALIZADA para el sidebar DERECHO
        # Conectamos la señal a un nuevo manejador que acepta la vista y asume el lado 'right'
        self_location = 'right' # Localización de la vista que se cambia desde TopBar
        self.top_bar.view_change_request.connect(lambda view_key: self._handle_sidebar_change(self_location, view_key))
        
        # 3. Conexiones del VideoAreaWidget (Acciones del usuario en el reproductor)
        drawing_label = self.video_area.get_drawing_label() 
        
        self.video_area.play_pause_request.connect(self.video_service.toggle_play_pause)
        self.video_area.seek_slider_moved.connect(self.video_service.slider_moved)
        self.video_area.seek_slider_released.connect(self.video_service.seek)
        self.video_area.quality_changed.connect(self.video_service.set_quality)
        
        # CORRECCIÓN BUG: Usar self.bookmarks_module (la instancia), NO llamarla como función ()
        self.video_area.btn_add_bookmark.clicked.connect(
            lambda: self.bookmarks_module.add_current_time_bookmark()
        )

        self.video_area.btn_screenshot.clicked.connect(self.video_service.save_screenshot)
        
        # 4. Conexiones de los SidebarWidgets (Acciones del usuario en las Features)
        
        # Conexiones de Dibujo (Usando get_drawing_module del SidebarWidget)
        # Conectamos las señales del módulo de dibujo DERECHO
        draw_module_right = self.sidebar_right.get_drawing_module()
        draw_module_right.clear_canvas_request.connect(drawing_label.clear_drawing)
        draw_module_right.color_changed.connect(drawing_label.set_pen_color)
        draw_module_right.save_drawing_request.connect(self.save_current_drawing)
        
        # Conectamos las señales del módulo de dibujo IZQUIERDO
        draw_module_left = self.sidebar_left.get_drawing_module()
        draw_module_left.clear_canvas_request.connect(drawing_label.clear_drawing)
        draw_module_left.color_changed.connect(drawing_label.set_pen_color)
        draw_module_left.save_drawing_request.connect(self.save_current_drawing)
        
        # Bookmarks (Sincronización Feature -> UI)
        # CORRECCIÓN BUG: Usar la instancia self.bookmarks_module directamente
        self.bookmarks_module.marks_changed.connect(self.update_ruler_marks)
        
        
    # --- Slots (Coordinación y Delegación) ---

    def _get_active_sidebar_for_drawing(self):
        """Determina qué sidebar está activo y tiene la pestaña de dibujo abierta."""
        if self.active_views['right'] == 'drawing':
            return self.sidebar_right
        if self.active_views['left'] == 'drawing':
            return self.sidebar_left
        return None 

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
        active_sidebar = self._get_active_sidebar_for_drawing()
        
        if not active_sidebar:
            print("No hay un módulo de dibujo activo para guardar.")
            return

        current_time = self.video_service.get_current_time()
        paths_to_save = self.video_area.get_drawing_label().get_finished_paths()
        # Se usa get_drawing_module del sidebar activo
        duration = active_sidebar.get_drawing_module().get_duration() 

        if paths_to_save:
            self.service_manager.save_drawing_data(current_time, duration, paths_to_save)
            self.video_area.get_drawing_label().update()
            print(f"Dibujo guardado para {VideoService.format_time(current_time)}")

    def _update_sidebar_content(self, side: str, view_key: str):
        """
        Cambia la pestaña visible dentro de un sidebar específico.
        Asume que view_key es un valor válido en SIDEBAR_VIEW_MAP.
        """
        sidebar = self.sidebar_left if side == 'left' else self.sidebar_right
        index = self.SIDEBAR_VIEW_MAP[view_key]
        sidebar.set_current_tab(index)


    @Slot(str, str)
    def _handle_sidebar_change(self, side: str, new_view_key: str):
        """
        Maneja el evento de cambio de vista para un sidebar dado.
        1. Actualiza el estado central de la aplicación.
        2. Actualiza la UI (visibilidad, contenido del sidebar).
        3. Habilita/Deshabilita el dibujo globalmente.
        """
        drawing_label = self.video_area.get_drawing_label()
        
        current_view = self.active_views[side]
        
        # 1. Determinar el nuevo estado (Toggle: si se presiona el mismo botón, se oculta)
        if current_view == new_view_key:
            new_view_key = None
        
        # 2. Solo actualiza si la vista realmente cambia
        if current_view == new_view_key:
            return

        print(f"Toggle de vista {side} solicitado: {current_view} -> {new_view_key}")

        # 3. Actualiza el estado central
        self.active_views[side] = new_view_key
        
        # 4. Actualiza el estado visual de los botones del TopBar (Solo aplica al lado derecho actualmente)
        if side == 'right':
             self.top_bar.set_active_view(new_view_key)
        
        # 5. Actualiza el contenido del Sidebar (visibilidad y pestaña)
        sidebar = self.sidebar_left if side == 'left' else self.sidebar_right
        
        if new_view_key:
            # Solo actualiza si la vista es una clave conocida
            if new_view_key in self.SIDEBAR_VIEW_MAP:
                self._update_sidebar_content(side, new_view_key)
                sidebar.setVisible(True)
            else:
                print(f"Advertencia: Vista de sidebar desconocida: {new_view_key}")
                sidebar.setVisible(False)
                self.active_views[side] = None # Reset state if key is unknown
        else:
            sidebar.setVisible(False)


        # 6. Control de la funcionalidad de dibujo (Global)
        # El dibujo está habilitado si la vista 'drawing' está activa en CUALQUIER sidebar.
        is_drawing_active = (self.active_views['right'] == 'drawing' or 
                             self.active_views['left'] == 'drawing')
        drawing_label.enable_drawing(is_drawing_active)

    
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
            # Bookmarks 
            bm_path = os.path.join(video_directory, "videomarks.json")
            # Usamos self.bookmarks_module directamente
            self.bookmarks_module.load_data_from_file(bm_path) 
            self.update_ruler_marks()
            
        self.video_area.update_time_display(0, duration_msec)
    
    @Slot()
    def update_ruler_marks(self):
        """Actualiza el ruler con las marcas obtenidas del BookmarksModule."""
        # CORRECCIÓN BUG: Usamos self.bookmarks_module (la instancia)
        mark_times = self.bookmarks_module.get_mark_times()
        self.video_area.get_ruler_widget().update_bookmarks(mark_times)

    # --- Funciones de Qt ---
    
    def closeEvent(self, event):
        self.video_service.stop_service() 
        event.accept()