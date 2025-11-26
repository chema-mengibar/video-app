from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLineEdit, QLabel, QGroupBox, QComboBox
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal, Slot, Qt

class GridControlsWidget(QWidget):
    """
    Widget de la barra lateral para controlar la funcionalidad de Cuadrícula/Perspectiva.
    
    Esta interfaz permite al usuario definir un rango de tiempo de visualización 
    para la cuadrícula, los puntos de referencia (Nodos A, B, C) y las longitudes 
    conocidas (Segmentos) para el cálculo de la perspectiva.
    """
    
    # Señales para notificar al coordinador (MainWindow)
    
    # Solicitud de usar el msec actual para el tiempo de inicio/fin del display
    start_use_current_time_request = Signal()
    end_use_current_time_request = Signal()
    
    # Señal emitida cuando un valor de Coordenada de Nodo cambia (Node Label, X, Y)
    # Node Label ahora es 'A', 'B', o 'C'
    node_value_changed = Signal(str, str, str) 
    
    # Señal emitida cuando un valor de Segmento cambia (Segment Label, Value)
    # Segment Label es 'AB', 'BC', 'CA', 'Central'
    segment_value_changed = Signal(str, str) 
    
    # Señal para restablecer todos los valores
    reset_request = Signal()
    
    # El constructor ahora solo acepta el padre, que es el comportamiento esperado de QWidget
    def __init__(self, parent=None): 
        super().__init__(parent)
        self.node_labels = ['A', 'B', 'C']
        self.segment_labels = ['AB', 'BC', 'CA', 'Central']
        self._setup_ui()
        self._connect_signals()

    # --- Métodos de Construcción de UI ---
    
    def _create_time_input_row(self, initial_time: str) -> tuple[QHBoxLayout, QLineEdit, QPushButton]:
        """Crea un campo de entrada de tiempo con el botón 'u'."""
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        # Time input (e.g., 00:00:01:200)
        time_edit = QLineEdit(initial_time)
        time_edit.setFixedWidth(100)
        time_edit.setAlignment(Qt.AlignCenter)
        
        # "u" button (Use current msec)
        btn_use = QPushButton("u")
        btn_use.setFixedSize(25, 25)
        btn_use.setObjectName("SmallActionButton")
        
        h_layout.addWidget(time_edit)
        h_layout.addWidget(btn_use)
        h_layout.addStretch(1)
        
        return h_layout, time_edit, btn_use

    def _create_node_inputs(self, node_label: str, initial_val: str = "120") -> tuple[QVBoxLayout, QLineEdit, QLineEdit]:
        """Crea los campos X e Y para un nodo dado (A, B, o C)."""
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(5)
        
        # Etiqueta del nodo (A, B, C)
        node_label_widget = QLabel(node_label)
        node_label_widget.setObjectName("NodeLabel")
        group_layout.addWidget(node_label_widget)
        
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        # X input
        h_layout.addWidget(QLabel("x"))
        x_edit = QLineEdit(initial_val)
        x_edit.setFixedWidth(50)
        x_edit.setObjectName(f"Node{node_label}X")
        h_layout.addWidget(x_edit)
        
        # Y input
        h_layout.addWidget(QLabel("y"))
        y_edit = QLineEdit(initial_val)
        y_edit.setFixedWidth(50)
        y_edit.setObjectName(f"Node{node_label}Y")
        h_layout.addWidget(y_edit)
        
        h_layout.addStretch(1)
        group_layout.addLayout(h_layout)
        return group_layout, x_edit, y_edit

    # Modificado para no incluir el QPushButton (btn_set)
    def _create_segment_row(self, segment_label: str, initial_val: str = "120") -> tuple[QHBoxLayout, QLineEdit]:
        """Crea una fila de entrada de segmento sin el botón de referencia."""
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(5)
        
        # Label (AB, BC, CA, Central)
        segment_label_widget = QLabel(segment_label)
        segment_label_widget.setFixedWidth(50) # Espacio para las etiquetas más largas
        h_layout.addWidget(segment_label_widget)
        
        # Value input
        value_edit = QLineEdit(initial_val)
        value_edit.setFixedWidth(70)
        
        # --- Lógica de solo lectura para el segmento 'Central' ---
        if segment_label == 'Central':
            value_edit.setReadOnly(True)
            # Opcional: Se puede agregar un estilo aquí si es necesario
        # --------------------------------------------------------

        h_layout.addWidget(value_edit)
        
        h_layout.addStretch(1)
        
        # Solo devolvemos el layout y el QLineEdit
        return h_layout, value_edit

    # --- Configuración Principal de la UI ---
    
    def _setup_ui(self):
        """Construye la interfaz de usuario con la estructura de la imagen proporcionada."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        title = QLabel("Grid")
        title.setObjectName("SidebarTitle")
        main_layout.addWidget(title)
        
        # Diccionarios para almacenar las referencias a los widgets
        self.time_inputs = {}
        self.node_inputs = {}
        self.segment_inputs = {}
        
        # --- 1. Display (Time Range) ---
        display_group = QGroupBox("Display")
        display_layout = QVBoxLayout(display_group)
        
        # Start Time
        time_layout_start, self.time_start_edit, self.btn_start_u = self._create_time_input_row("00:00:01:200")
        display_layout.addLayout(time_layout_start)
        self.time_inputs['start'] = self.time_start_edit
        
        # End Time
        time_layout_end, self.time_end_edit, self.btn_end_u = self._create_time_input_row("00:00:01:200")
        display_layout.addLayout(time_layout_end)
        self.time_inputs['end'] = self.time_end_edit
        
        main_layout.addWidget(display_group)
        
        # --- 2. Nodes (A, B, C) ---
        nodes_group = QGroupBox("Nodes (A, B, C)")
        nodes_layout = QVBoxLayout(nodes_group)
        nodes_layout.setSpacing(10)
        
        for label in self.node_labels:
            node_layout, x_edit, y_edit = self._create_node_inputs(label, "120")
            nodes_layout.addLayout(node_layout)
            self.node_inputs[label] = {'x': x_edit, 'y': y_edit}
            
        main_layout.addWidget(nodes_group)

        # --- 3. Segments (AB, BC, CA, Central) ---
        segments_group = QGroupBox("Segments (Known Lengths)")
        segments_layout = QVBoxLayout(segments_group)
        
        # Unit Selector
        unit_layout = QHBoxLayout()
        unit_layout.addWidget(QLabel("Unit"))
        self.combo_unit = QComboBox()
        self.combo_unit.addItems(["meters", "feet", "pixels"])
        self.combo_unit.setCurrentText("meters")
        unit_layout.addWidget(self.combo_unit)
        unit_layout.addStretch(1)
        segments_layout.addLayout(unit_layout)
        
        # Segment Rows 
        for label in self.segment_labels:
            # Recibimos solo el layout y el QLineEdit
            segment_layout, value_edit = self._create_segment_row(label, "120")
            segments_layout.addLayout(segment_layout)
            # Almacenamos la referencia solo al QLineEdit
            self.segment_inputs[label] = {'value': value_edit}
            
        main_layout.addWidget(segments_group)
        
        # --- 4. Reset Button ---
        self.btn_reset = QPushButton("r")
        self.btn_reset.setFixedSize(30, 30)
        self.btn_reset.setObjectName("SmallActionButton")
        main_layout.addWidget(self.btn_reset, alignment=Qt.AlignLeft)
        
        main_layout.addStretch(1)

    # --- Conexión de Señales ---
    def _connect_signals(self):
        """Conecta los botones 'u' y 'r' a las señales de salida del widget."""
        
        # Conexiones de botones 'u' (Use current msec)
        # ESTO EMITE LA SOLICITUD AL COORDINADOR
        self.btn_start_u.clicked.connect(self.start_use_current_time_request.emit)
        self.btn_end_u.clicked.connect(self.end_use_current_time_request.emit)
        
        # Conexión del botón 'r' (Reset)
        self.btn_reset.clicked.connect(self.reset_request.emit)
        
        # Conexiones de Nodos (emiten al cambiar el texto)
        for label in self.node_labels:
            x_edit = self.node_inputs[label]['x']
            y_edit = self.node_inputs[label]['y']
            
            # Usamos una lambda para capturar el valor de 'label' en el momento de la conexión
            x_edit.textChanged.connect(lambda text, label=label: self._emit_node_change(label, 'x', text))
            y_edit.textChanged.connect(lambda text, label=label: self._emit_node_change(label, 'y', text))

        # Conexiones de Segmentos (emiten al cambiar el texto)
        for label in self.segment_labels:
            value_edit = self.segment_inputs[label]['value']
            
            # Solo conectar si el campo no es de solo lectura (es decir, no es 'Central')
            if not value_edit.isReadOnly():
                # Usamos una lambda para capturar el valor de 'label'
                value_edit.textChanged.connect(lambda text, label=label: self.segment_value_changed.emit(label, text))
            
            # El botón '/' ha sido eliminado, así que no hay conexión que hacer aquí.

    @Slot(str, str, str)
    def _emit_node_change(self, node_label: str, axis: str, text: str):
        """Emite la señal node_value_changed con los valores actuales de X e Y del nodo."""
        
        # Obtenemos los valores cruzados para asegurar que se emiten ambos
        x_val = self.node_inputs[node_label]['x'].text()
        y_val = self.node_inputs[node_label]['y'].text()
        
        # La señal ahora emite el label ('A', 'B', 'C'), y sus coordenadas
        self.node_value_changed.emit(node_label, x_val, y_val)
            
    # --- Métodos públicos para el coordinador ---

    # Corregido el decorador Slot: ahora espera un int (msec) y un str (time_str)
    @Slot(int, str)
    def set_display_start_time(self, msec: int, time_str: str):
        """Actualiza el campo de inicio de tiempo con el msec actual del video."""
        # ESTO ACTUALIZA EL INPUT
        self.time_start_edit.setText(time_str)

    # Corregido el decorador Slot: ahora espera un int (msec) y un str (time_str)
    @Slot(int, str)
    def set_display_end_time(self, msec: int, time_str: str):
        """Actualiza el campo de fin de tiempo con el msec actual del video."""
        # ESTO ACTUALIZA EL INPUT
        self.time_end_edit.setText(time_str)