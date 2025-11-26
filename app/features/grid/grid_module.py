from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
# Importamos el widget de controles que realmente contiene los botones e inputs
from features.grid.grid_controls_widget import GridControlsWidget 

class GridModule(QWidget):
    """
    Módulo contenedor para la funcionalidad de Cuadrícula (Grid).
    Actúa como wrapper para GridControlsWidget y facilita el acceso a sus controles 
    desde el coordinador (MainWindow).
    
    Este módulo será insertado directamente en el Sidebar.
    """
    
    # Nota: No necesitamos la referencia al color inicial aquí, ya que GridControlsWidget
    # no lo usa, pero mantenemos la firma del constructor para consistencia si es necesario.
    def __init__(self, parent_app, parent=None): 
        # NOTA: Asegúrate que GridModule hereda de QWidget para que pueda tener un layout
        super().__init__(parent)
        self.parent_app = parent_app # Referencia a MainWindow
        
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Configura el layout principal del módulo e inserta el widget de control."""
        
        # 1. Establecer el layout para GridModule (Contenedor)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 2. Instanciar el Widget de Controles
        # Nota importante: GridControlsWidget ya solo acepta 'parent=None'
        self.grid_controls = GridControlsWidget(self) # Le pasamos 'self' como parent
        
        # 3. Añadir el widget de control al layout del módulo contenedor
        main_layout.addWidget(self.grid_controls)
        main_layout.addStretch(1) 

    def _connect_signals(self):
        """Conecta las señales del control de cuadrícula (delegando al coordinador)."""
        # La conexión de las señales de self.grid_controls se realizará en el coordinador 
        # (MainWindow) o en el AppConnector, utilizando el método get_grid_controls().
        pass

    def get_grid_controls(self) -> GridControlsWidget:
        """Getter para permitir a MainWindow acceder a los controles y sus señales."""
        return self.grid_controls