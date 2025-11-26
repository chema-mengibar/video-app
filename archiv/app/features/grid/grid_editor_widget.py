from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QGroupBox, QLineEdit, QLabel, QCheckBox, QSpinBox
from PySide6.QtCore import Qt
from features.grid.grid_data import GridData

class GridEditorWidget(QWidget):
    """Sidebar derecha: Editor de las propiedades del Grid activo/seleccionado."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_grid: GridData | None = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.title_label = QLabel("Editor de Grid")
        self.title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.main_form = QFormLayout()
        
        # 1. Rango de Tiempo
        self.time_group = QGroupBox("Rango de Activación (msec)")
        time_layout = QFormLayout(self.time_group)
        self.msec_from_input = QSpinBox(maximum=9999999, minimum=0)
        self.msec_to_input = QSpinBox(maximum=9999999, minimum=0)
        time_layout.addRow("Desde:", self.msec_from_input)
        time_layout.addRow("Hasta:", self.msec_to_input)
        
        self.msec_from_input.valueChanged.connect(lambda v: self._update_grid_data('msec_from', v))
        self.msec_to_input.valueChanged.connect(lambda v: self._update_grid_data('msec_to', v))

        layout.addWidget(self.time_group)
        
        # 2. Nodos (Pines) - Lectura/Actualización por Drag
        self.nodes_group = QGroupBox("Nodos (Coordenadas en Canvas)")
        self.nodes_form = QFormLayout(self.nodes_group)
        self.node_inputs = {}
        
        for name in ["A", "B", "C"]:
            x_input = QLineEdit()
            y_input = QLineEdit()
            x_input.setReadOnly(True) # Los nodos se mueven arrastrando
            y_input.setReadOnly(True)
            self.nodes_form.addRow(f"Pin {name} (X):", x_input)
            self.nodes_form.addRow(f"Pin {name} (Y):", y_input)
            self.node_inputs[name] = (x_input, y_input)

        layout.addWidget(self.nodes_group)

        # 3. Segmentos (Distancias Reales)
        self.segments_group = QGroupBox("Segmentos (Distancia Real en metros)")
        self.segments_form = QFormLayout(self.segments_group)
        self.segment_inputs = {}
        
        for name in ["AB", "BC", "CA", "AC"]:
            distance_input = QLineEdit()
            computed_checkbox = QCheckBox("Calculado")
            
            # Conexión para actualizar la distancia (solo si no es computed)
            distance_input.editingFinished.connect(lambda n=name: self._update_segment_distance(n))
            # Conexión para actualizar el estado de calculado
            computed_checkbox.stateChanged.connect(lambda state, n=name: self._update_segment_computed(n, state == Qt.Checked))
            
            self.segments_form.addRow(f"Segmento {name} (Distancia):", distance_input)
            self.segments_form.addRow(f"Segmento {name} (Calculado):", computed_checkbox)
            self.segment_inputs[name] = (distance_input, computed_checkbox)
        
        layout.addWidget(self.segments_group)

        layout.addStretch()
        self.setDisabled(True) # Deshabilitar hasta que se seleccione un grid

    def set_grid(self, grid: GridData | None):
        """Carga los datos de un grid específico en el editor."""
        self.active_grid = grid
        if grid:
            self.setDisabled(False)
            self._load_grid_data(grid)
        else:
            self.setDisabled(True)

    def _load_grid_data(self, grid: GridData):
        """Carga todos los valores del GridData en los inputs de la UI."""
        
        # Rango de Tiempo
        self.msec_from_input.setValue(grid.msec_from)
        self.msec_to_input.setValue(grid.msec_to)
        
        # Nodos
        for name, (x_input, y_input) in self.node_inputs.items():
            node = grid.nodes[name]
            x_input.setText(str(node.x))
            y_input.setText(str(node.y))
            
        # Segmentos
        for name, (distance_input, computed_checkbox) in self.segment_inputs.items():
            segment = grid.segments[name]
            
            distance_input.setText(f"{segment.distance:.2f}")
            computed_checkbox.setChecked(segment.computed)
            
            # Habilitar/Deshabilitar input de distancia si está calculado
            distance_input.setReadOnly(segment.computed)
            distance_input.setEnabled(not segment.computed)
    
    def update_node_coords(self, node_name: str, x: int, y: int):
        """Actualiza las coordenadas de un nodo movido por el overlay."""
        if not self.active_grid or node_name not in self.node_inputs:
            return
            
        # 1. Actualizar el modelo de datos (GridData)
        node = self.active_grid.nodes[node_name]
        node.x = x
        node.y = y
        
        # 2. Actualizar la UI
        x_input, y_input = self.node_inputs[node_name]
        x_input.setText(str(x))
        y_input.setText(str(y))
        
        # Nota: Aquí se debería recalcular la triangulación/distancias si fuera necesario

    def _update_grid_data(self, attribute: str, value):
        """Actualiza msec_from o msec_to en el modelo."""
        if self.active_grid:
            setattr(self.active_grid, attribute, value)
            # Nota: Esto podría disparar una actualización de la lista de grids si es necesario

    def _update_segment_distance(self, segment_name: str):
        """Actualiza la distancia real del segmento desde el input de texto."""
        if not self.active_grid: return
        
        distance_input, computed_checkbox = self.segment_inputs[segment_name]
        try:
            new_distance = float(distance_input.text())
            self.active_grid.segments[segment_name].distance = new_distance
        except ValueError:
            # Revertir al valor anterior si la entrada no es un número
            distance_input.setText(f"{self.active_grid.segments[segment_name].distance:.2f}")

    def _update_segment_computed(self, segment_name: str, is_computed: bool):
        """Actualiza el estado 'computed' del segmento."""
        if not self.active_grid: return
        
        segment = self.active_grid.segments[segment_name]
        segment.computed = is_computed
        
        distance_input, _ = self.segment_inputs[segment_name]
        
        # Habilitar/Deshabilitar el input de distancia
        distance_input.setReadOnly(is_computed)
        distance_input.setEnabled(not is_computed)
        
        if is_computed:
            # Nota: Si se pone a 'calculado', se debería disparar el cálculo aquí
            pass