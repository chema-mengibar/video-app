# src/app/features/draw/drawing_label.py

from PySide6.QtWidgets import QLabel, QSizePolicy
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, QPoint, QSize, Signal

class DrawingVideoLabel(QLabel):
    # ... (El código completo de DrawingVideoLabel de la revisión anterior va aquí)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: black; color: white;")
        
        self.current_path = [] # Trazos activos actualmente
        self.finished_paths = [] # Trazos que se han terminado pero no guardado
        self.active_paths = [] # Trazos persistentes cargados desde DrawManager
        
        self.drawing_enabled = False
        self.drawing = False
        self.pen_color = QColor(255, 0, 0)
        self.pen_thickness = 5

    def set_pen_color(self, color):
        self.pen_color = color
        
    def enable_drawing(self, enable: bool):
        self.drawing_enabled = enable
        if enable:
            self.setCursor(Qt.CrossCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def set_active_paths(self, paths: list):
        """Recibe los paths persistentes activos desde DrawManager."""
        self.active_paths = paths
        
    def get_finished_paths(self) -> list:
        """Devuelve los paths terminados para ser guardados."""
        paths = self.finished_paths[:]
        self.finished_paths = [] # Limpiar después de obtener
        return paths

    def clear_drawing(self):
        """Limpia el canvas y los paths terminados, pero no los activos."""
        self.current_path = []
        self.finished_paths = []
        self.update()

    # --- Eventos de Ratón (Lógica de dibujo) ---
    def mousePressEvent(self, event):
        if self.drawing_enabled and event.button() == Qt.LeftButton:
            self.drawing = True
            # Iniciar nuevo path con color y grosor actuales
            self.current_path = [{'color': self.pen_color.getRgb(), 'thickness': self.pen_thickness, 'points': [event.pos()]}]
            self.update()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.drawing:
            # Agregar punto al path actual
            self.current_path[0]['points'].append(event.pos()) 
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            if self.current_path:
                # Mover el path actual a paths terminados, listo para ser guardado
                self.finished_paths.extend(self.current_path)
            self.current_path = []
            
    # --- Evento de Pintura ---
    def paintEvent(self, event):
        # 1. Pintar el QLabel original (Pixmap del video)
        super().paintEvent(event)
        
        if self.pixmap() is None or self.pixmap().isNull():
            return
            
        painter = QPainter(self)
        
        # 2. Calcular offset de la imagen centrada
        pixmap_size = self.pixmap().size()
        widget_rect = self.rect()
        offset_x = (widget_rect.width() - pixmap_size.width()) // 2
        offset_y = (widget_rect.height() - pixmap_size.height()) // 2
        
        painter.translate(offset_x, offset_y) # Aplicar el offset
        
        # 3. Dibujar Paths Persistentes (Activos)
        self._draw_paths(painter, self.active_paths)
            
        # 4. Dibujar Paths Terminados (Pendientes de guardar)
        self._draw_paths(painter, self.finished_paths)
            
        # 5. Dibujar Path Actual (En progreso)
        self._draw_paths(painter, self.current_path)
        
        painter.end()
        
    def _draw_paths(self, painter, paths):
        """Helper para dibujar paths."""
        for path_data in paths:
            points = path_data['points']
            if len(points) < 2:
                continue
            
            # Recrear QPen a partir de los datos guardados
            color = QColor(*path_data['color'][:3]) 
            pen = QPen(color, path_data['thickness'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            
            # Dibujar las líneas
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i+1])