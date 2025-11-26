from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem, QLabel
from PySide6.QtCore import Signal
from features.grid.grids_manager import GridsManager
from features.grid.grid_data import GridData

class GridsListWidget(QWidget):
    """Sidebar izquierda: Muestra la lista de grids disponibles."""
    
    # Signal: (grid_id: str)
    grid_selected = Signal(str)
    # Signal: (new_grid: GridData)
    grid_added = Signal(GridData)

    def __init__(self, grids_manager: GridsManager, parent=None):
        super().__init__(parent)
        self.grids_manager = grids_manager
        self.current_grid_id: str | None = None
        self.setup_ui()
        self.load_grids()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel("Gestión de Grids")
        self.title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.add_button = QPushButton("➕ Añadir Nuevo Grid")
        self.add_button.clicked.connect(self._add_new_grid)
        layout.addWidget(self.add_button)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)
        
        layout.addStretch()

    def load_grids(self):
        """Carga los grids existentes en la lista."""
        self.list_widget.clear()
        for grid in self.grids_manager.all().values():
            item = QListWidgetItem(f"{grid.name} ({grid.msec_from}ms - {grid.msec_to}ms)")
            item.setData(Qt.UserRole, grid.id)
            self.list_widget.addItem(item)
            
        if self.list_widget.count() > 0 and self.current_grid_id is None:
            self.list_widget.setCurrentRow(0)
            self._on_item_clicked(self.list_widget.item(0))

    def _add_new_grid(self):
        """Crea un nuevo GridData y lo añade al manager y a la lista."""
        # Crea un grid con un rango de tiempo inicial (ej: 0ms a 10000ms)
        new_grid = GridData(msec_from=0, msec_to=10000) 
        self.grids_manager.add_grid(new_grid)
        self.grid_added.emit(new_grid)
        self.load_grids() # Recarga la lista para mostrar el nuevo grid
        
        # Selecciona el nuevo grid
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) == new_grid.id:
                self.list_widget.setCurrentItem(item)
                self._on_item_clicked(item)
                break

    def _on_item_clicked(self, item: QListWidgetItem):
        """Emite la señal de selección de grid."""
        grid_id = item.data(Qt.UserRole)
        self.current_grid_id = grid_id
        self.grid_selected.emit(grid_id)