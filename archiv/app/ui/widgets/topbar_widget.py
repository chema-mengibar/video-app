from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon 
from ui.styles.theme import DarkTheme

class TopBarWidget(QFrame):
    """
    Barra superior que contiene los controles principales de la aplicación:
    - Botón Load Video (izquierda)
    - Botones para la selección de vista de Sidebar (derecha)
    """

    # Señales emitidas a la MainWindow
    load_video_request = Signal()
    # Nueva señal que emite la clave de la vista que se desea activar
    view_change_request = Signal(str)

    def __init__(self, 
                 parent=None):
        
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
        # CORRECCIÓN: Renombrado a self.load_video_button para MainWindow
        self.load_video_button = QPushButton("Load Video")

        self.load_video_button.setIcon(QIcon("assets/icons/photo-camera.svg"))
        self.load_video_button.setIconSize(QSize(12, 12))
        self.load_video_button.setToolTip("Open Video file")

        layout.addWidget(self.load_video_button)

        # Botones de selección de vista (derecha)
        # self.btn_toggle_bookmarks = QPushButton("Marks")
        self.btn_toggle_drawing = QPushButton("Draw")
        self.btn_toggle_grids = QPushButton("Grid")

        # Configuración de botones como botones normales.
        # El estado activo visual se gestiona EXCLUSIVAMENTE mediante setProperty('active-view').
        # self.btn_toggle_bookmarks.setProperty('is-active', True)
        self.btn_toggle_drawing.setProperty('is-active', False)
        self.btn_toggle_grids.setProperty('is-active', False)

        layout.addStretch(1)  # Empuja los toggles hacia la derecha

        # layout.addWidget(self.btn_toggle_bookmarks)
        layout.addWidget(self.btn_toggle_drawing)
        layout.addWidget(self.btn_toggle_grids)

    def connect_signals(self):
        # Conexión principal del botón de cargar video
        # CORRECCIÓN: Usamos el nuevo nombre de atributo
        self.load_video_button.clicked.connect(self.load_video_request.emit)
        
        # Conexiones que emiten la clave de la vista solicitada cuando se hace CLICK
        # Usamos la señal .clicked para la acción de cambio de vista.
        # self.btn_toggle_bookmarks.clicked.connect(
        #     lambda: self.view_change_request.emit('bookmarks')
        # )
        self.btn_toggle_drawing.clicked.connect(
            lambda: self.view_change_request.emit('drawing')
        )
        self.btn_toggle_grids.clicked.connect(
            lambda: self.view_change_request.emit('grids')
        )
        
    # Método público para que MainWindow pueda actualizar el estado checkeado de los botones
    @Slot(str)
    def set_active_view(self, key: str):
        """
        Establece el estado visual 'activo' de los botones mediante la propiedad 'active-view'.
        Esto permite que MainWindow controle la exclusividad visual.
        """
        all_buttons = {
            # 'bookmarks': self.btn_toggle_bookmarks,
            'drawing': self.btn_toggle_drawing,
            'grids': self.btn_toggle_grids
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