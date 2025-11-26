# src/app/features/grid/grids_manager.py

import uuid
import json
import os
from PySide6.QtCore import QObject, Signal, Slot

# Asegúrate de importar tus clases de datos
# ⚠️ ADVERTENCIA: Debes tener estas clases definidas en tu proyecto
from features.grid.grid_data import GridData, GridNode 

class GridsManager(QObject):
    """
    Gestor de la lógica de negocio para las cuadrículas (Grids).
    Mantiene el estado de todos los grids, gestiona el grid activo 
    y maneja la persistencia.
    """
    
    # Señales para notificar cambios importantes a la UI (p. ej., GridOverlay)
    active_grid_changed = Signal(object) # Emite el GridData activo (o None)
    all_grids_changed = Signal()         # Emite cuando la lista de grids cambia

    def __init__(self, parent=None):
        super().__init__(parent)
        # Diccionario que almacena todos los grids por su ID
        self.grids: dict[str, GridData] = {} 
        self.active_grid_id: str | None = None
        
    # --- MÉTODOS ESPERADOS POR LA UI (CRÍTICOS PARA EL INICIO) ---

    def set_active_grid_id(self, grid_id: str | None):
        """Establece el ID del grid actualmente seleccionado/editado."""
        if self.active_grid_id != grid_id:
            self.active_grid_id = grid_id
            self.active_grid_changed.emit(self.get(grid_id))

    def get_active_grid(self) -> GridData | None:
        """Retorna el objeto GridData activo."""
        if self.active_grid_id and self.active_grid_id in self.grids:
            return self.grids[self.active_grid_id]
        return None
        
    def get(self, grid_id: str) -> GridData | None:
        """Retorna un objeto GridData por su ID."""
        return self.grids.get(grid_id)

    def all(self) -> dict[str, GridData]:
        """
        🟢 CORRECCIÓN FATAL: Retorna todos los grids. 
        Este método es el que GridsListWidget espera para poblar su lista.
        """
        return self.grids


    @Slot(object) # Recibe un diccionario o un objeto complejo del Overlay
    def update_grid_from_nodes_dict(self, data: dict):
        """
        Método llamado por GridOverlayWidget cuando se arrastra un nodo,
        recibiendo un diccionario con 'label' y 'node'.
        """
        grid = self.get_active_grid()
        if not grid:
            return None
            
        node_label = data.get('label')
        node_obj = data.get('node') # Esto es el GridNode arrastrado

        if node_label and node_label in grid.nodes:
            # Aseguramos que la instancia en el manager se actualice directamente
            # Ya que el objeto GridNode del Overlay es el mismo que el del Manager,
            # solo necesitamos notificar el cambio.
            
            # ⚠️ Nota: El GridNode dentro del GridOverlayWidget tiene coordenadas ENTERAS.
            # Si planeas usar coordenadas normalizadas (0.0 a 1.0) para el manager,
            # necesitarás reescalar la posición aquí o en el Overlay.
            
            # Para evitar el error de AttributeError, simplemente notificamos:
            self.active_grid_changed.emit(grid) 
            
        return grid # Retornar el objeto actualizado para que MainWindow lo propague

    # --- SLOTS CONECTADOS DESDE MAINWINDOW ---

    @Slot(object) # 🟢 Acepta un objeto GridData (el 'new_grid' que le pasa GridsListWidget)
    def add_grid(self, new_grid: GridData):
        """
        Añade un objeto GridData ya creado (por GridsListWidget) a la colección 
        y lo establece como activo. Este es el método que usa GridsListWidget.
        """
        if new_grid.id not in self.grids:
            self.grids[new_grid.id] = new_grid
            self.set_active_grid_id(new_grid.id)
            print(f"GridsManager: Grid '{new_grid.name}' añadido y activo.")
            self.all_grids_changed.emit()
        else:
            # Esto podría ser una recarga de datos, solo actualizamos el ID activo
            self.set_active_grid_id(new_grid.id)

    @Slot()
    def update_active_grid(self):
        """
        Guarda los cambios del GridControlsWidget en el GridData activo.
        """
        grid = self.get_active_grid()
        if grid:
            print(f"GridsManager: Actualizando grid {grid.name}...")
            # Aquí iría la lógica para tomar los valores de UI y actualizar
            self.active_grid_changed.emit(grid)
            self.all_grids_changed.emit() 


    @Slot()
    def delete_active_grid(self):
        """Elimina el grid actualmente activo."""
        if self.active_grid_id and self.active_grid_id in self.grids:
            deleted_id = self.active_grid_id
            del self.grids[deleted_id]
            
            # Resetear estado activo
            self.set_active_grid_id(None)
            print(f"GridsManager: Grid {deleted_id} eliminado.")
            
            self.all_grids_changed.emit()

    @Slot(object, object)
    def update_grid_from_nodes(self, node_label: str, new_pos: tuple[float, float]):
        """
        Método llamado por GridOverlayWidget cuando se arrastra un nodo.
        """
        grid = self.get_active_grid()
        if grid and node_label in grid.nodes:
            # Asumo que new_pos es (x_norm, y_norm)
            grid.nodes[node_label].x = new_pos[0]
            grid.nodes[node_label].y = new_pos[1]
            
            self.active_grid_changed.emit(grid)
            return grid 
        return None