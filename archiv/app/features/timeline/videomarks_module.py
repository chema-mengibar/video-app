# src/app/features/timeline/videomarks_module.py

import json
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QListWidget, QListWidgetItem, QInputDialog, 
    QLabel, QLineEdit, QMenu, QMessageBox, QFileDialog
)
from PySide6.QtCore import Slot, Qt, QObject, Signal, QPoint 
from services.video_service import VideoService 
from ui.styles.theme import DarkTheme 
from PySide6.QtGui import QAction, QColor, QBrush

class BookmarkEntry(QObject):
    """
    Representa un solo punto de interés (videomark).
    Emite una señal para solicitar al servicio de video que se mueva a su tiempo.
    """
    request_seek = Signal(int) 

    def __init__(self, time_msec: int, label: str = "Videomark", parent=None):
        super().__init__(parent)
        self.time_msec = time_msec
        self.label = label
        
    def to_dict(self):
        """Serializa la entrada a un diccionario para JSON."""
        return {"time_msec": self.time_msec, "label": self.label}

class BookmarksModule(QWidget):
    """
    Gestiona la lista de Videomarks, la UI del sidebar y la interacción.
    """
    
    marks_changed = Signal() 

    def __init__(self, video_service, parent_app, parent=None): 
        super().__init__(parent)
        
        self.video_service = video_service 
        # parent_app (MainWindow) ya no se usa para format_time, pero se mantiene por si es necesaria
        # para diálogos o el path del video.
        self.parent_app = parent_app 
        self.bookmarks: list[BookmarkEntry] = []
        
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Configura la interfaz de usuario para el módulo de bookmarks."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("Videomarks")
        header.setStyleSheet(DarkTheme.SIDEBAR_HEADER)
        
        self.btn_save = QPushButton("Save Marks")
        self.btn_load = QPushButton("Load Marks")

        self.btn_save.setProperty('button_type', 'secondary')
        self.btn_load.setProperty('button_type', 'secondary')
        
        # Lista de Widgets para los bookmarks
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu) # Habilitar menú contextual

        # Layout de botones de control
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.btn_save)
        control_layout.addWidget(self.btn_load)
        
        main_layout.addWidget(header)

        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.list_widget)
        
        self.format_time = VideoService.format_time 

    def connect_signals(self):
        """Conecta las acciones de la UI a los métodos internos y al servicio."""
        self.btn_save.clicked.connect(self.open_save_dialog)
        self.btn_load.clicked.connect(self.open_load_dialog)
        
        self.list_widget.itemDoubleClicked.connect(self.seek_to_bookmark)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        
    # --- Lógica de Negocio ---

    @Slot()
    def add_current_time_bookmark(self, label: str = "Videomark"):
        """Añade un bookmark en el tiempo actual del video."""
        if not self.video_service.is_video_loaded():
            QMessageBox.warning(self, "Warning", "Please load a video first.")
            return

        current_time = self.video_service.get_current_time() 
        
        # Diálogo para pedir la etiqueta
        label, ok = QInputDialog.getText(
            self, 
            "Add Videomark", 
            "Enter label:", 
            QLineEdit.Normal, 
            f"{label} @ {self.format_time(current_time)}" 
        )
        
        if ok and label:
            new_bookmark = BookmarkEntry(current_time, label)
            
            new_bookmark.request_seek.connect(self.video_service.seek) 
            
            self.bookmarks.append(new_bookmark)
            self.bookmarks.sort(key=lambda b: b.time_msec)
            self.refresh_list_ui(current_time)
            self.marks_changed.emit() 

    @Slot(QListWidgetItem)
    def seek_to_bookmark(self, item: QListWidgetItem):
        """Busca la entrada de bookmark y pide al servicio que haga el seek."""
        bookmark_index = self.list_widget.row(item)
        if 0 <= bookmark_index < len(self.bookmarks):
            bookmark = self.bookmarks[bookmark_index]
            bookmark.request_seek.emit(bookmark.time_msec)
            
    def remove_bookmark(self, item: QListWidgetItem):
        """Elimina un bookmark seleccionado."""
        row = self.list_widget.row(item)
        if 0 <= row < len(self.bookmarks):
            self.bookmarks.pop(row)
            self.list_widget.takeItem(row)
            self.marks_changed.emit()
            
    def get_mark_times(self) -> list[int]:
        """Retorna las marcas de tiempo para que la regla del tiempo las dibuje."""
        return [b.time_msec for b in self.bookmarks]
        
    # --- Manejo de UI de la lista ---

    @Slot(int)
    def update_list_ui(self, current_msec: int):
        pass

    def refresh_list_ui(self, current_msec: int = 0):
        """Recarga completamente la lista de QListWidget con los datos de self.bookmarks."""
        self.list_widget.clear()
        
        for bookmark in self.bookmarks:
            time_str = self.format_time(bookmark.time_msec)
            item_text = f"[{time_str}] {bookmark.label}"
            
            item = QListWidgetItem(item_text)
            if bookmark.time_msec == current_msec:
                item.setBackground(QBrush(QColor(DarkTheme.WOW_COLOR)))
            
            self.list_widget.addItem(item)
            
    @Slot(QPoint) 
    def show_context_menu(self, pos: QPoint):
        """Muestra el menú contextual para operaciones de la lista."""
        item = self.list_widget.itemAt(pos)
        if item:
            menu = QMenu(self)
            seek_action = QAction("Go To Mark", self)
            seek_action.triggered.connect(lambda: self.seek_to_bookmark(item))
            menu.addAction(seek_action)
            
            remove_action = QAction("Remove Mark", self)
            remove_action.triggered.connect(lambda: self.remove_bookmark(item))
            menu.addAction(remove_action)
            
            menu.exec(self.list_widget.mapToGlobal(pos))


    # --- Persistencia ---

    def open_save_dialog(self):
        """Abre el diálogo de guardar y delega el guardado."""
        if not self.bookmarks:
            QMessageBox.information(self, "Info", "No marks to save.")
            return

        # Intentar obtener el directorio del video cargado para el path por defecto
        default_dir = self.parent_app.current_video_directory or os.path.expanduser("~") 
        default_path = os.path.join(default_dir, "videomarks.json")
        
        path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Videomarks", 
            default_path, 
            "JSON Files (*.json)"
        )
        if path:
            self.save_data_to_file(path)

    def open_load_dialog(self):
        """Abre el diálogo de cargar y delega la carga."""
        default_dir = self.parent_app.current_video_directory or os.path.expanduser("~")
        default_path = os.path.join(default_dir, "videomarks.json")

        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Load Videomarks", 
            default_path, 
            "JSON Files (*.json)"
        )
        if path:
            self.load_data_from_file(path)


    def save_data_to_file(self, path: str):
        """Guarda la lista de bookmarks en un archivo JSON."""
        data_to_save = [b.to_dict() for b in self.bookmarks]
        try:
            with open(path, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            print(f"Bookmarks guardados en: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error Saving", f"Failed to save bookmarks: {e}")

    def load_data_from_file(self, path: str):
        """Carga la lista de bookmarks desde un archivo JSON con validación."""
        if not os.path.exists(path):
            return

        try:
            with open(path, 'r') as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("JSON content is not a list (expected marks array).")

            loaded_bookmarks = []
            required_keys = ['time_msec', 'label']
            
            for item in data:
                if all(k in item for k in required_keys) and isinstance(item['time_msec'], int):
                    new_mark = BookmarkEntry(item['time_msec'], item['label'])
                    new_mark.request_seek.connect(self.video_service.seek) 
                    loaded_bookmarks.append(new_mark)
                else:
                    print(f"Advertencia: Bookmark con formato inválido ignorado: {item}")

            self.bookmarks = loaded_bookmarks
            self.bookmarks.sort(key=lambda b: b.time_msec)
            self.refresh_list_ui()
            self.marks_changed.emit() 
            print(f"Bookmarks cargados ({len(loaded_bookmarks)} entradas) desde: {path}")

        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error Loading", "Error decoding JSON file. File corrupted or invalid.")
        except Exception as e:
            QMessageBox.critical(self, "Error Loading", f"Unknown error loading bookmarks: {e}")