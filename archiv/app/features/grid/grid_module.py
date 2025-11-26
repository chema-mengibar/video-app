# src/app/features/grid/grid_module.py

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal, Slot
from features.grid.grids_manager import GridsManager 
from features.grid.grid_data import GridData 
from features.grid.grids_list_widget import GridsListWidget 
from features.grid.grid_controls_widget import GridControlsWidget 


class GridModule(QWidget):
    """
    Módulo contenedor (fachada) para la funcionalidad de Cuadrícula (Grid).
    Define y rutea todas las señales que MainWindow espera.
    """

    # 🟢 SEÑALES REQUERIDAS POR MAINWINDOW
    add_grid_request = Signal() 
    update_grid_request = Signal()
    delete_grid_request = Signal()
    edit_mode_toggled = Signal(bool) 
    
    # 🟢 CORRECCIÓN FATAL: Señales faltantes para la sincronización de tiempo
    use_current_time_start_request = Signal() 
    use_current_time_end_request = Signal()

    def __init__(self, grids_manager: GridsManager, parent_app, parent=None): 
        super().__init__(parent)
        self.parent_app = parent_app
        self.grids_manager = grids_manager

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.grids_list = GridsListWidget(self.grids_manager, self)
        main_layout.addWidget(self.grids_list)
        
        self.grid_controls = GridControlsWidget(self) 
        main_layout.addWidget(self.grid_controls)
        
        main_layout.addStretch(1) 

    def _connect_signals(self):
        
        # Conexión 1: ADD GRID
        self.grids_list.grid_added.connect(self._handle_grid_added_and_select)
        
        # Conexión 2: Selección de Grid
        self.grids_list.grid_selected.connect(self._handle_grid_selection) 
        
        # Conexión 3: Acciones del Editor (Proxy de las señales para MainWindow)
        self.grid_controls.update_request.connect(self.update_grid_request)
        self.grid_controls.delete_request.connect(self.delete_grid_request)
        self.grid_controls.btn_edit_mode.toggled.connect(self.edit_mode_toggled)

        # 🟢 CORRECCIÓN FATAL: Proxy de las señales de tiempo
        # La señal es emitida por GridControlsWidget (donde está el botón "Usar Actual")
        # y re-emitida por GridModule (el nombre que espera MainWindow).
        self.grid_controls.start_use_current_time_request.connect(self.use_current_time_start_request.emit)
        self.grid_controls.end_use_current_time_request.connect(self.use_current_time_end_request.emit)

    @Slot(str) 
    def _handle_grid_selection(self, grid_id: str):
        grid_data = self.grids_manager.get(grid_id) 
        
        if grid_data:
            self.grid_controls.load_grid_data(grid_data) 
            self.grids_manager.set_active_grid_id(grid_id) 

    @Slot(GridData) 
    def _handle_grid_added_and_select(self, new_grid: GridData):
        self.add_grid_request.emit() 
        self.grid_controls.load_grid_data(new_grid) 
        self.grids_manager.set_active_grid_id(new_grid.id)
        
    # --- SLOTS REQUERIDOS POR MAINWINDOW (Delegación) ---
    
    @Slot(int)
    def set_start_time(self, msec: int):
        self.grid_controls.set_start_time(msec) 
        
    @Slot(int)
    def set_end_time(self, msec: int):
        self.grid_controls.set_end_time(msec)

    @Slot(object) 
    def update_controls_from_manager(self, grid_data):
        self.grid_controls.update_controls_from_manager(grid_data)
        
    # --- Interfaz para MainWindow (Accessors) ---
    
    def get_grid_controls(self) -> GridControlsWidget:
        return self.grid_controls
    
    def get_grid_list(self) -> GridsListWidget:
        return self.grids_list