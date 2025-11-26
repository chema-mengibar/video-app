from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon 
from ui.styles.theme import DarkTheme

class TopBarWidget(QFrame):
    """
    Barra superior que contiene los controles principales de la aplicación:
    - Botón Load Video (izquierda)
    - Botones para la selección de vista de Sidebar (derecha)

    NOTA: Este widget NO maneja la lógica de exclusividad; simplemente emite
    una señal con el identificador de la vista solicitada. El estado visual
    activo se gestiona mediante la propiedad 'active-view' y CSS.
    """

    # Señales emitidas a la MainWindow
    load_video_request = Signal()
    # Nueva señal que emite la clave de la vista que se desea activar
    view_change_request = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Asignar objectName para aplicar CSS
        self.setObjectName("topbar_widget")
        self.setStyleSheet(DarkTheme.TOOLBAR_STYLES)

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Botón Load Video (izquierda)
        self.btn_load_video = QPushButton("Load Video")

        self.btn_load_video.setIcon(QIcon("assets/icons/photo-camera.svg"))
        self.btn_load_video.setIconSize(QSize(12, 12))
        self.btn_load_video.setToolTip("Open Video file")

        layout.addWidget(self.btn_load_video)

        # Botones de selección de vista (derecha)
        # self.btn_toggle_videomarks = QPushButton("Marks")
        self.btn_toggle_drawing = QPushButton("Draw")
        self.btn_toggle_grids = QPushButton("Grid")
        self.btn_toggle_cut = QPushButton("Cut")

        # Configuración de botones como botones normales.
        # El estado activo visual se gestiona EXCLUSIVAMENTE mediante setProperty('active-view').
        # self.btn_toggle_videomarks.setProperty('is-active', True)
        self.btn_toggle_drawing.setProperty('is-active', False)
        self.btn_toggle_grids.setProperty('is-active', False)
        self.btn_toggle_cut.setProperty('is-active', False)

        layout.addStretch(1)  # Empuja los toggles hacia la derecha

        # layout.addWidget(self.btn_toggle_videomarks)
        layout.addWidget(self.btn_toggle_drawing)
        layout.addWidget(self.btn_toggle_grids)
        layout.addWidget(self.btn_toggle_cut)

    def connect_signals(self):
        # Conexión principal del botón de cargar video
        self.btn_load_video.clicked.connect(self.load_video_request.emit)
        
        # Conexiones que emiten la clave de la vista solicitada cuando se hace CLICK
        # Usamos la señal .clicked para la acción de cambio de vista.
        # self.btn_toggle_videomarks.clicked.connect(
        #     lambda: self.view_change_request.emit('videomarks')
        # )
        self.btn_toggle_drawing.clicked.connect(
            lambda: self.view_change_request.emit('drawing')
        )
        self.btn_toggle_grids.clicked.connect(
            lambda: self.view_change_request.emit('grids')
        )
        self.btn_toggle_cut.clicked.connect(
            lambda: self.view_change_request.emit('cut')
        )
        
    # Método público para que MainWindow pueda actualizar el estado checkeado de los botones
    @Slot(str)
    def set_active_view(self, key: str):
        """
        Establece el estado visual 'activo' de los botones mediante la propiedad 'active-view'.
        Esto permite que MainWindow controle la exclusividad visual.
        """
        all_buttons = {
            # 'videomarks': self.btn_toggle_videomarks,
            'drawing': self.btn_toggle_drawing,
            'grids': self.btn_toggle_grids,
            'cut': self.btn_toggle_cut
        }
        
        for name, button in all_buttons.items():
            is_active = (name == key)
            
            # Bloqueamos las señales antes de actualizar la propiedad para evitar
            # que cualquier cambio de estado no deseado active recursiones.
            button.blockSignals(True)
            
            # 1. Actualiza la propiedad personalizada
            button.setProperty('is-active', is_active)
            
            # 2. Fuerza al sistema de estilos a reevaluar y aplicar el nuevo estilo CSS
            button.style().polish(button)

            button.blockSignals(False)