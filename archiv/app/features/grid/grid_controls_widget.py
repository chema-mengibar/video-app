# src/app/features/grid/grid_controls_widget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLineEdit, QLabel, QGroupBox, QComboBox, QFormLayout # Se añade QFormLayout
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal, Slot, Qt

# Importación necesaria para type hints (Asegúrate de que existe esta ruta)
from features.grid.grid_data import GridData 

class GridControlsWidget(QWidget):
    # Señales para notificar al coordinador (MainWindow)
    start_use_current_time_request = Signal()
    end_use_current_time_request = Signal()
    update_request = Signal() # 🟢 Nueva Señal: Para guardar cambios en el grid activo
    delete_request = Signal() # 🟢 Nueva Señal: Para eliminar el grid activo
    edit_mode_toggled = Signal(bool) # 🟢 Nueva Señal: Para cambiar el modo de edición en el overlay
    
    # ... (Otras señales como node_value_changed, segment_value_changed) ...

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_grid: GridData | None = None  # 🟢 Guarda el objeto de datos activo
        self._setup_ui()
        self._connect_signals()
        self.setEnabled(False) # Iniciar deshabilitado

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # 1. Rango de Tiempo (usamos QLineEdit para simplificar el ejemplo)
        time_group = QGroupBox("Rango (msec)")
        time_layout = QFormLayout(time_group)
        self.time_start_edit = QLineEdit("0")
        self.time_end_edit = QLineEdit("0")
        
        btn_start = QPushButton("Usar Actual")
        btn_end = QPushButton("Usar Actual")
        
        time_h_layout_start = QHBoxLayout()
        time_h_layout_start.addWidget(self.time_start_edit)
        time_h_layout_start.addWidget(btn_start)
        
        time_h_layout_end = QHBoxLayout()
        time_h_layout_end.addWidget(self.time_end_edit)
        time_h_layout_end.addWidget(btn_end)
        
        time_layout.addRow("Desde:", time_h_layout_start)
        time_layout.addRow("Hasta:", time_h_layout_end)
        layout.addWidget(time_group)
        
        # 🟢 Creamos un diccionario para almacenar los inputs de nodos
        self.node_inputs = {} 
        self._create_node_inputs(layout)

        # 🟢 Botones de Acción
        action_layout = QHBoxLayout()
        self.btn_update = QPushButton("Guardar Cambios")
        self.btn_delete = QPushButton("Eliminar Grid")
        self.btn_edit_mode = QPushButton("Activar Edición (Video)")
        self.btn_edit_mode.setCheckable(True)
        
        action_layout.addWidget(self.btn_update)
        action_layout.addWidget(self.btn_delete)
        layout.addLayout(action_layout)
        layout.addWidget(self.btn_edit_mode)

        layout.addStretch(1)
        
        # Conexiones adicionales que usan las nuevas señales
        btn_start.clicked.connect(self.start_use_current_time_request.emit)
        btn_end.clicked.connect(self.end_use_current_time_request.emit)
        self.btn_update.clicked.connect(self.update_request.emit)
        self.btn_delete.clicked.connect(self.delete_request.emit)
        self.btn_edit_mode.toggled.connect(self.edit_mode_toggled.emit)


    def _create_node_inputs(self, parent_layout: QVBoxLayout):
        """Helper para crear la sección de inputs de Nodos A, B, C."""
        node_group = QGroupBox("Coordenadas de Nodos (X, Y)")
        node_layout = QFormLayout(node_group)
        
        for label in ['A', 'B', 'C']:
            x_input = QLineEdit("0")
            y_input = QLineEdit("0")
            
            h_layout = QHBoxLayout()
            h_layout.addWidget(QLabel("X:"))
            h_layout.addWidget(x_input)
            h_layout.addWidget(QLabel("Y:"))
            h_layout.addWidget(y_input)
            
            node_layout.addRow(f"Nodo {label}:", h_layout)
            self.node_inputs[label] = {'x': x_input, 'y': y_input} # Almacenamos para fácil acceso
            
        parent_layout.addWidget(node_group)

    def _connect_signals(self):
        # Aquí irían las conexiones de QLineEdit.textChanged a los slots de tu GridManager, 
        # pero por ahora, solo necesitamos los métodos públicos.
        pass
        
    # --- MÉTODOS PÚBLICOS (INTERFAZ CON GRIDMODULE Y MAINWINDOW) ---

    @Slot(GridData) 
    def load_grid_data(self, grid_data: GridData):
        """
        🟢 MÉTODO CRÍTICO: Recibe el objeto GridData del GridModule 
        y actualiza todos los campos de la UI. (Sustituye a load_grid_by_id).
        """
        self.active_grid = grid_data 
        if grid_data:
            self.time_start_edit.setText(str(grid_data.msec_from))
            self.time_end_edit.setText(str(grid_data.msec_to))
            
            # Actualizar Nodos (A, B, C)
            for node_label, node in grid_data.nodes.items():
                if node_label in self.node_inputs:
                    self.node_inputs[node_label]['x'].setText(str(node.x))
                    self.node_inputs[node_label]['y'].setText(str(node.y))
                    
            self.setEnabled(True)
        else:
            self.setEnabled(False) 

    @Slot(int)
    def set_start_time(self, msec: int):
        """Método llamado por MainWindow para actualizar el 'msec_from'."""
        self.time_start_edit.setText(str(msec))

    @Slot(int)
    def set_end_time(self, msec: int):
        """Método llamado por MainWindow para actualizar el 'msec_to'."""
        self.time_end_edit.setText(str(msec))

    @Slot(GridData) 
    def update_controls_from_manager(self, grid_data: GridData):
        """
        Método llamado por MainWindow/Overlay para actualizar los inputs 
        (típicamente después de arrastrar un nodo).
        """
        if grid_data:
            for node_label, node in grid_data.nodes.items():
                if node_label in self.node_inputs:
                    self.node_inputs[node_label]['x'].setText(str(node.x))
                    self.node_inputs[node_label]['y'].setText(str(node.y))