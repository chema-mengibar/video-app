# features/videomarks.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QListWidget, QListWidgetItem, QInputDialog, 
    QLabel, QLineEdit, QMenu, QWidgetAction # <--- Importaciones corregidas
)
from PySide6.QtCore import Slot, Qt, QObject, QThread, Signal
import json

class BookmarkEntry(QObject):
    """Estructura de datos para un solo Videomark."""
    
    # Señal para pedir al controlador que salte a este punto
    request_seek = Signal(int) 

    def __init__(self, time_msec, label="Videomark"):
        super().__init__()
        self.time_msec = time_msec
        self.label = label
        
    def to_dict(self):
        return {"time_msec": self.time_msec, "label": self.label}

# ----------------------------------------------------------------------
# MÓDULO DE INTERFAZ Y LÓGICA DE VIDEOMARKS
# ----------------------------------------------------------------------

class BookmarksModule(QWidget):
    """
    Gestiona la lista de Videomarks, la UI del sidebar y la interacción.
    """
    # Señal para notificar a la regla del tiempo (TimelineRuler) que se actualice
    marks_changed = Signal() 

    def __init__(self, parent_app):
        super().__init__()
        
        self.parent_app = parent_app 
        self.bookmarks = []
        
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Lista de Videomarks
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background-color: #2D2D2D; border: 1px solid #444444;")
        
        # Habilitar menú contextual (clic derecho)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu) 
        
        self.main_layout.addWidget(self.list_widget)

    def connect_signals(self):
        # Acceder a la señal a través de self.parent_app.controller
        self.parent_app.controller.time_updated_signal.connect(self.update_list_ui)
        self.list_widget.itemDoubleClicked.connect(self.seek_to_bookmark)
        
        # 🟢 CONEXIÓN DE MENÚ CONTEXTUAL PARA BORRAR
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        
        # La señal marks_changed debe conectarse en main.py para actualizar la regla

    # --- Gestión de Datos y Borrado ---

    def add_current_time_bookmark(self, label="Videomark"):
        """Añade un bookmark en el tiempo actual del video."""
        
        if not self.parent_app.is_video_loaded:
            return

        current_time = self.parent_app.get_current_time()
        
        # Abrir diálogo para la etiqueta (QLineEdit ahora está definido)
        label, ok = QInputDialog.getText(
            self, 
            "Add Videomark", 
            "Enter label:", 
            QLineEdit.Normal, # <--- QLineEdit ahora es accesible
            f"{label} @ {self.parent_app._format_time(current_time)}"
        )
        
        if ok and label:
            new_bookmark = BookmarkEntry(current_time, label)
            
            # Conectar la señal request_seek al slot seek del controlador
            new_bookmark.request_seek.connect(self.parent_app.controller.seek)
            
            self.bookmarks.append(new_bookmark)
            self.bookmarks.sort(key=lambda b: b.time_msec)
            self.refresh_list_ui(current_time)
            self.marks_changed.emit() # 🟢 Notificar a la regla de tiempo y otros

    @Slot(QListWidgetItem)
    def seek_to_bookmark(self, item):
        """Salta a la posición del video del bookmark seleccionado."""
        bookmark_index = self.list_widget.row(item)
        if 0 <= bookmark_index < len(self.bookmarks):
            bookmark = self.bookmarks[bookmark_index]
            bookmark.request_seek.emit(bookmark.time_msec)

    def show_context_menu(self, pos):
        """Muestra el menú contextual al hacer clic derecho."""
        item = self.list_widget.itemAt(pos)
        if item:
            menu = QMenu(self)
            
            # Acción de Borrar
            delete_action = menu.addAction("Delete Videomark")
            delete_action.triggered.connect(lambda: self.delete_bookmark(item))
            
            # Muestra el menú en la posición global del cursor
            menu.exec(self.list_widget.mapToGlobal(pos))
            
    def delete_bookmark(self, item):
        """Elimina el bookmark seleccionado de la lista de datos y actualiza la UI."""
        index = self.list_widget.row(item)
        
        if 0 <= index < len(self.bookmarks):
            # 1. Eliminar de la lista de datos
            self.bookmarks.pop(index) 
            
            # 2. Actualizar UI
            self.refresh_list_ui(self.parent_app.get_current_time())
            
            # 3. Notificar a la regla del tiempo para que se actualice
            self.marks_changed.emit()

    def get_mark_times(self):
        """Retorna las marcas de tiempo para la regla del tiempo."""
        return [b.time_msec for b in self.bookmarks]

    # --- Gestión de UI ---
    
    @Slot(int)
    def update_list_ui(self, current_msec):
        """Actualiza la lista y resalta el bookmark activo."""
        self.refresh_list_ui(current_msec)


    def refresh_list_ui(self, current_msec=None):
        """Reconstruye la lista de la UI."""
        self.list_widget.clear()
        
        for bookmark in self.bookmarks:
            time_str = self.parent_app._format_time(bookmark.time_msec)
            item_text = f"[{time_str}] {bookmark.label}"
            item = QListWidgetItem(item_text)
            
            # Resaltar si está cerca del tiempo actual (opcional)
            if current_msec is not None and abs(bookmark.time_msec - current_msec) < 500:
                 item.setBackground(Qt.darkYellow)
                 
            self.list_widget.addItem(item)
            
    # --- Persistencia ---
    
    def save_data_to_file(self, path):
        """Guarda la lista de bookmarks en un archivo JSON."""
        data = [b.to_dict() for b in self.bookmarks]
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Bookmarks guardados en: {path}")
        except Exception as e:
            print(f"Error al guardar bookmarks: {e}")

    def load_data_from_file(self, path):
        """Carga la lista de bookmarks desde un archivo JSON."""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            self.bookmarks = []
            for item in data:
                bookmark = BookmarkEntry(item['time_msec'], item['label'])
                
                # Reconectar la señal request_seek después de cargar
                bookmark.request_seek.connect(self.parent_app.controller.seek)
                
                self.bookmarks.append(bookmark)
            
            self.bookmarks.sort(key=lambda b: b.time_msec)
            self.refresh_list_ui(self.parent_app.get_current_time())
            self.marks_changed.emit() # Notificar la actualización de marcas después de cargar
            print(f"Bookmarks cargados desde: {path}")

        except FileNotFoundError:
            print("Archivo de bookmarks no encontrado.")
        except json.JSONDecodeError:
            print("Error al decodificar el archivo JSON.")
        except Exception as e:
            print(f"Error al cargar bookmarks: {e}")