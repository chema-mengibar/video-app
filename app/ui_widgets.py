# ui_widgets.py

from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QMouseEvent

class TimelineRuler(QWidget):
    """Widget para dibujar marcas de tiempo y el cursor de reproducción."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.duration_msec = 0
        self.current_msec = 0
        self.mark_times = []
        self.setFixedHeight(10) 

    def paintEvent(self, event):
        painter = QPainter(self)
        width = self.width()
        height = self.height()
        painter.fillRect(self.rect(), QColor(30, 30, 30))

        # 1. DIBUJAR MARCAS
        if self.duration_msec > 0:
            mark_pen = QPen(Qt.white, 2)
            painter.setPen(mark_pen)
            mark_height = height - 2 
            y_start = height - mark_height
            for mark_msec in self.mark_times:
                x_pos = int((mark_msec / self.duration_msec) * width)
                painter.drawLine(x_pos, y_start, x_pos, height)

        # 2. DIBUJAR CURSOR
        if self.duration_msec > 0:
            cursor_x = int((self.current_msec / self.duration_msec) * width)
            cursor_pen = QPen(QColor(255, 0, 0), 2)
            painter.setPen(cursor_pen)
            painter.drawLine(cursor_x, 0, cursor_x, height)
            
        painter.end()


class DrawingVideoLabel(QLabel):
    """QLabel modificado que permite dibujar sobre el QPixmap, mostrando dibujos temporales."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drawing_enabled = False
        self.current_path = []
        self.finished_paths = []    # Rutas dibujadas por el usuario (listas de QPoint)
        self.active_paths = []      # Rutas inyectadas por DrawManager (listas de QPoint)
        self.last_point = QPoint()

    def enable_drawing(self, enable):
        self.drawing_enabled = enable
        self.setCursor(Qt.CrossCursor if enable else Qt.ArrowCursor)

    def clear_drawing(self):
        """Limpia el dibujo local (el que el usuario está creando)."""
        self.finished_paths = []
        self.current_path = []
        self.update()

    # MÉTODOS PARA EL GESTOR DE DIBUJO
    def set_active_paths(self, paths):
        """Establece las rutas que vienen del DrawManager (visibles en el tiempo actual)."""
        self.active_paths = paths

    def get_finished_paths(self):
        """Devuelve las rutas terminadas por el usuario para ser guardadas."""
        paths = self.finished_paths[:]
        self.finished_paths = [] # Limpia las rutas locales después de la extracción
        return paths
    
    # MÉTODOS DE INTERACCIÓN DEL MOUSE
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.drawing_enabled:
            # Convierte las coordenadas del evento al tamaño original del pixmap
            self.current_path = [event.pos()]
            self.last_point = event.pos()
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton and self.drawing_enabled:
            self.current_path.append(event.pos())
            self.last_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.drawing_enabled:
            if self.current_path:
                self.finished_paths.append(self.current_path)
            self.current_path = []
            self.update()
    
    # MÉTODO DE PINTADO
    def paintEvent(self, event):
        super().paintEvent(event) 
        
        painter = QPainter(self)

        # 1. Dibujar Finished Paths (del usuario - si no se han guardado)
        pen_finished = QPen(QColor(255, 0, 0), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen_finished)
        for path in self.finished_paths:
            if len(path) > 1:
                for i in range(len(path) - 1):
                    painter.drawLine(path[i], path[i+1])

        # 2. Dibujar Active Paths (Dibujos temporales guardados)
        pen_active = QPen(QColor(255, 255, 0), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin) 
        painter.setPen(pen_active)
        for path in self.active_paths:
            if len(path) > 1:
                for i in range(len(path) - 1):
                    painter.drawLine(path[i], path[i+1])


        # 3. Dibujar Current Path (el que se está dibujando actualmente)
        pen_current = QPen(QColor(255, 0, 0), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen_current)
        if self.current_path:
             if len(self.current_path) > 1:
                for i in range(len(self.current_path) - 1):
                    painter.drawLine(self.current_path[i], self.current_path[i+1])
                    
        painter.end()