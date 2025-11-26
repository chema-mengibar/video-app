import os 
import cv2
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QColorDialog, 
    QFileDialog, QVBoxLayout, QStackedWidget, QSpinBox
)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QImage, QPixmap, QColor 
from ui.styles.theme import DarkTheme 
from services.video_service import VideoService 
from core.service_manager import ServiceManager 
from ui.widgets.video_area_widget import VideoAreaWidget
from ui.widgets.sidebar_widget import SidebarWidget
from ui.widgets.topbar_widget import TopBarWidget 
from features.draw.drawing_label import DrawingVideoLabel 
from features.timeline.videomarks_module import BookmarksModule 
from features.grid.grids_manager import GridsManager 
from features.grid.grid_overlay_widget import GridOverlayWidget 
from features.draw.drawing_module import DrawingModule # Se necesita para inicializarlo


class MainWindow(QMainWindow): 
    """
    Coordinador de la aplicación.
    Conecta las señales de los Widgets con las acciones de los Servicios.
    """
    
    # Mapeo de vistas del Sidebar a los índices del QStackedWidget interno del Sidebar
    SIDEBAR_VIEW_MAP = {
        'Bookmarks': 0,
        'Drawing': 1,
        'Grids': 2,
    }
    
    # Señales internas
    # Esta señal se utiliza para forzar la actualización de la duración en DrawService
    duration_changed = Signal(int)

    def __init__(self, service_manager: ServiceManager, parent=None):
        super().__init__(parent)
        self.service_manager = service_manager
        self.video_service = self.service_manager.video() # Acceso directo para conveniencia
        
        # Propiedades de estado de la aplicación
        self.duration_msec = 0
        self.current_video_directory = None

        self._setup_modules()
        self._setup_ui()
        self._connect_all()
        
        # Aplicar tema oscuro
        DarkTheme.apply_theme(self)

    def _setup_modules(self):
        """Inicializa los módulos de lógica y UI de las funcionalidades secundarias."""
        
        # 1. Bookmarks Module
        # 🛑 CORRECCIÓN CRÍTICA: Se añade el argumento posicional 'parent_app=self'
        self.bookmarks_module = BookmarksModule(self.video_service,parent_app=self) 

        # 2. Drawing Module (Controles de dibujo)
        initial_color = QColor(255, 0, 0)
        self.drawing_module = DrawingModule(initial_color=initial_color)
        
        # 3. Grids Module (Controles de cuadrícula)
        self.grids_manager = self.service_manager.grids() # Obtenido del ServiceManager
        # El GridModule también necesita parent_app, pero asumiré que su constructor es correcto
        # o que usaremos 'self' si fuera necesario (por ahora no lo tocamos).
        # self.grids_module = GridModule(self.grids_manager, parent_app=self) 

        # 4. Grid Overlay Widget (capa de dibujo sobre el video)
        # Se necesita la instancia del manager
        self.grid_overlay = GridOverlayWidget(grids_manager=self.grids_manager)
        
    def _setup_ui(self):
        """Construye la estructura principal de la UI."""
        self.setWindowTitle("Video Analysis Tool")
        
        # 1. Widgets principales
        self.video_area = VideoAreaWidget()
        self.top_bar = TopBarWidget()
        
        # 2. Sidebar Derecho (Controles)
        # ⚠️ Nota: Asumo que DrawModule, GridModule, y BookmarksModule son QWidgets o heredan de QWidget
        
        initial_color = QColor(255, 0, 0)

        self.sidebar_right = SidebarWidget(
            self.video_service,
            self,
            initial_color,
            'right',
            self.bookmarks_module,
            self.grids_manager,
            self
        )

        # 3. Estructura de la ventana
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.top_bar)
        
        content_layout = QHBoxLayout()
        content_layout.addWidget(self.video_area)
        content_layout.addWidget(self.sidebar_right)
        
        main_layout.addLayout(content_layout)
        self.setCentralWidget(central_widget)

        # 4. Integrar el Grid Overlay sobre el VideoArea
        # Esta es la parte crucial: El GridOverlay debe ser hijo del VideoAreaWidget 
        # y colocarse en el mismo StackedWidget que el DrawingVideoLabel, o bien
        # colocarse como un widget flotante sobre el video_label.
        
        # Método 1: Usar un StackedWidget para el VideoLabel y el Overlay (Más limpio)
        video_label = self.video_area.get_drawing_label()
        
        # Hacemos que el DrawingVideoLabel sea el padre del GridOverlay
        self.grid_overlay.setParent(video_label)
        self.grid_overlay.setGeometry(video_label.geometry())
        
        # Asegurarse de que el GridOverlay redimensione con el video_label
        video_label.installEventFilter(self) # Necesitamos el eventFilter para capturar resizeEvent
        
        self.resize(1200, 800) # Tamaño inicial
        
    def _connect_all(self):
        """Conecta todas las señales de la UI con los slots de los servicios."""
        
        # --- 1. CONEXIONES DEL VIDEOSERVICE (Desde VideoAreaWidget) ---
        
        # Carga/Reproducción
        self.video_area.load_video_request.connect(self._handle_load_video)
        self.video_area.play_pause_request.connect(self.video_service.set_playback_state)
        
        # Control de tiempo (Slider)
        self.video_area.seek_slider_moved.connect(self.video_service.seek)
        self.video_area.seek_slider_released.connect(self.video_service.seek)
        
        # VideoService -> UI (Actualizaciones de Frame y Tiempo)
        self.video_service.frame_ready_signal.connect(self._update_video_frame)
        
        # El VideoService emite el tiempo actual, que se usa para actualizar la UI y el dibujo
        self.video_service.time_updated_signal.connect(self.video_area.update_time_display)
        self.video_service.time_updated_signal.connect(self._handle_time_update)

        # El Manager notifica a MainWindow cuando se carga un video (con duración y directorio)
        # Esto dispara la carga de datos asociados (Bookmarks, Drawings)
        self.service_manager.video_loaded_info.connect(self.handle_video_loaded)
        
        # --- 2. CONEXIONES DEL DRAWING MODULE ---
        
        drawing_label = self.video_area.get_drawing_label()
        
        # UI -> Logic
        self.drawing_module.color_changed.connect(drawing_label.set_pen_color)
        self.drawing_module.save_drawing_request.connect(self._save_drawing_data)
        self.drawing_module.clear_canvas_request.connect(drawing_label.clear_session_paths)
        
        # --- 3. CONEXIONES DEL BOOKMARKS MODULE ---
        
        self.video_area.btn_add_bookmark.clicked.connect(self._add_bookmark_from_ui)
        self.bookmarks_module.data_changed.connect(self.update_ruler_marks) # Notifica a la UI si los bookmarks cambian
        
        # --- 4. CONEXIONES DEL GRID MODULE (GridOverlay) ---
        
        # Tiempo -> Grid Overlay
        self.video_service.time_updated_signal.connect(self.grid_overlay.set_current_time)
        
        # Grid Overlay -> Grid Manager (para guardar la posición arrastrada)
        # La señal de GridOverlay debe ser mapeada a un Slot en GridsManager para persistir las coordenadas
        # self.grid_overlay.node_moved.connect(self.grids_manager.update_grid_from_nodes) # Esta señal necesita ser implementada

        # --- 5. CONEXIONES DE TOPBAR ---
        self.top_bar.load_video_request.connect(self._handle_load_video)
        self.top_bar.view_changed.connect(self._handle_view_change)
        
        # Screenshot
        self.video_area.btn_screenshot.clicked.connect(self._handle_screenshot)
        
    def eventFilter(self, obj, event):
        """Maneja el evento de redimensionamiento del video_label para el GridOverlay."""
        if obj == self.video_area.get_drawing_label() and event.type() == event.Resize:
            self.grid_overlay.setGeometry(obj.geometry())
            self.grid_overlay.update()
        return super().eventFilter(obj, event)

    @Slot()
    def _handle_load_video(self):
        """Abre el diálogo de archivo y delega la carga al VideoService."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Video", 
            "", 
            "Video Files (*.mp4 *.avi *.mov);;All Files (*)"
        )
        if filepath:
            self.video_service.load_video(filepath)

    @Slot(object)
    def _update_video_frame(self, frame_data: QImage):
        """Recibe el frame del VideoService y lo muestra en el DrawingVideoLabel."""
        if frame_data.isNull():
            return
            
        # 1. Convertir QImage a QPixmap
        pixmap = QPixmap.fromImage(frame_data)
        
        # 2. Establecer la imagen en el QLabel
        label = self.video_area.get_drawing_label()
        label.setPixmap(pixmap.scaled(
            label.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        ))
        
        # 3. Forzar el repintado de los overlays (dibujo y grid)
        label.update()
        
    @Slot(int)
    def _handle_time_update(self, current_msec: int):
        """Actualiza la lógica de dibujo con el nuevo tiempo."""
        paths = self.service_manager.get_active_drawing_paths(current_msec)
        self.video_area.get_drawing_label().set_active_paths(paths)
        self.video_area.get_drawing_label().update()
        
        # LÓGICA DE GRID: El GridOverlay se actualiza a través de la conexión en _connect_all
        
        
    @Slot(bool, int, str)
    def handle_video_loaded(self, success, duration_msec, video_directory):
        """Sincroniza el estado de la UI tras la carga del video."""
        self.duration_msec = duration_msec
        self.current_video_directory = video_directory

        self.video_area.set_controls_enabled(success)
        self.video_area.get_slider().setRange(0, duration_msec)
        self.video_area.get_ruler_widget().duration_msec = duration_msec
        self.video_area.get_ruler_widget().update()
        
        # Notificar a DrawService sobre la nueva duración
        self.duration_changed.emit(duration_msec)
        self.drawing_module.set_duration(duration_msec) 
        
        # Cargar datos de bookmarks después de establecer el directorio
        if success and video_directory:
            # Bookmarks 
            bm_path = os.path.join(video_directory, "videomarks.json")
            self.bookmarks_module.load_data_from_file(bm_path) 
            self.update_ruler_marks()
            
        self.video_area.update_time_display(0, duration_msec)
    
    @Slot()
    def update_ruler_marks(self):
        """Actualiza el ruler con las marcas obtenidas del BookmarksModule."""
        mark_times = self.bookmarks_module.get_all_times()
        self.video_area.get_ruler_widget().set_marks(mark_times)
        self.video_area.get_ruler_widget().update()
        
    @Slot()
    def _add_bookmark_from_ui(self):
        """Añade un nuevo bookmark en el tiempo actual."""
        msec = self.video_service.current_time_msec
        if self.video_service.video_path:
            self.bookmarks_module.add_bookmark(msec)
            self.update_ruler_marks()
            
    @Slot(str)
    def _handle_view_change(self, view_name: str):
        """Cambia la vista activa de la barra lateral."""
        if view_name in self.SIDEBAR_VIEW_MAP:
            index = self.SIDEBAR_VIEW_MAP[view_name]
            self.sidebar_right.set_current_tab(index)
            
            # Lógica para habilitar/deshabilitar el dibujo
            is_drawing_view = (view_name == 'Drawing')
            self.video_area.get_drawing_label().set_drawing_enabled(is_drawing_view)

    @Slot()
    def _save_drawing_data(self):
        """Guarda los paths temporales del DrawingVideoLabel al DrawService."""
        if not self.current_video_directory:
            print("ERROR: No hay video cargado para guardar los datos de dibujo.")
            return

        drawing_label = self.video_area.get_drawing_label()
        paths_to_save = drawing_label.get_finished_paths()
        
        if paths_to_save:
            # 1. Guardar los paths en el servicio
            self.service_manager.save_drawing_data(
                current_time=self.video_service.current_time_msec,
                duration=self.duration_msec,
                paths_to_save=paths_to_save
            )
            # 2. Persistir los datos del servicio a disco
            draw_path = os.path.join(self.current_video_directory, "drawings.json")
            self.service_manager.draw_service.save_data(draw_path)
            
            # 3. Limpiar los paths temporales de la sesión después de guardar
            drawing_label.clear_session_paths()
            
            print(f"Dibujos guardados y persistidos en {draw_path}")

    @Slot()
    def _handle_screenshot(self):
        """Delega la captura de pantalla al VideoService."""
        current_frame = self.video_service.processor.current_frame
        current_time = self.video_service.current_time_msec
        
        if current_frame is not None and self.video_service.video_path:
            self.video_service.take_screenshot(current_frame, current_time)
        else:
            print("ERROR: No se puede tomar captura. Asegúrese de que hay un video en reproducción.")