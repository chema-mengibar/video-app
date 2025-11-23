# features/exporting.py

from PySide6.QtWidgets import QFileDialog, QLabel
from PySide6.QtGui import QPixmap

class ExportingModule:
    def __init__(self, parent_controller):
        # El parent_controller es la instancia de VideoPlayerController
        self.controller = parent_controller

    def take_screenshot(self):
        """Guarda el pixmap actual de la etiqueta de video como imagen."""
        
        # Acceder al widget desde el controlador
        video_label: QLabel = self.controller.video_label
        current_pixmap: QPixmap = video_label.pixmap()
        
        if current_pixmap is None:
            print("No hay video cargado para tomar screenshot.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self.controller, # Usar el controlador como padre del diálogo
            "Guardar Screenshot", 
            "screenshot.png", 
            "PNG (*.png);;JPEG (*.jpg)"
        )

        if file_path:
            # Asegurar que guardamos la imagen escalada que está visible
            current_pixmap.save(file_path)
            print(f"Screenshot guardado en: {file_path}")
            
    # Aquí podríamos añadir métodos como export_metadata() en el futuro.