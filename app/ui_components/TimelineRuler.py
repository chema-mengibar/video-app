# ui_components/TimelineRuler.py

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtCore import Qt, QSize, QRect

class TimelineRuler(QWidget):
    """
    Widget que actúa como una regla de tiempo debajo del slider, 
    mostrando marcas de tiempo y videomarks.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(15) # Altura más pequeña para el ruler
        self.duration_msec = 0
        self.current_msec = 0
        self.bookmarks = {} # {key: {msec: X, label: Y}}
        
    def minimumSizeHint(self):
        return QSize(100, 15)

    def sizeHint(self):
        return QSize(500, 15)

    def update_bookmarks(self, bookmarks_dict):
        """Actualiza el diccionario de videomarks y fuerza el redibujo."""
        self.bookmarks = bookmarks_dict
        self.update() # Forzar el redibujo

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        width = rect.width()
        height = rect.height()
        
        # 1. Fondo (Asegurar un fondo visible)
        painter.fillRect(rect, QColor("#336699")) # Fondo oscuro visible
        
        if self.duration_msec == 0:
            return

        # 2. Líneas de Tiempo 
        pixels_per_msec = width / self.duration_msec
        
        step_msec = 1000 
        
        # Ajuste inteligente del espaciado de marcas 
        if pixels_per_msec * step_msec < 30: 
            step_msec = 5000 
            if pixels_per_msec * step_msec < 30:
                 step_msec = 10000 
                 
        painter.setPen(QColor("#555555")) 
        font = QFont("Arial", 6) 
        painter.setFont(font)
        
        for msec in range(0, int(self.duration_msec) + step_msec, step_msec):
            x = int(msec * pixels_per_msec)
            
            # Línea vertical del ruler
            painter.drawLine(x, 0, x, height) 
            
            # Etiqueta de tiempo (si hay espacio)
            if pixels_per_msec * step_msec > 40: 
                total_seconds = int(msec / 1000)
                seconds = total_seconds % 60
                minutes = (total_seconds // 60) % 60
                time_str = f"{minutes:02d}:{seconds:02d}"
                painter.drawText(x + 2, height - 2, time_str) 


        # 3. Dibujar Videomarks como pequeños rectángulos
        VM_COLOR = QColor("#ff0000") # Color de acento
        painter.setPen(Qt.NoPen) 
        painter.setBrush(VM_COLOR) 
        
        vm_rect_height = 12 # Aumentado para visibilidad
        vm_rect_width = 3  # Aumentado para visibilidad
        
        for data in self.bookmarks.values():
            msec = data["msec"] 
            x = int(msec * pixels_per_msec)
            
            # Dibujar un pequeño rectángulo en la parte inferior del ruler
            painter.drawRect(x - (vm_rect_width // 2), height - vm_rect_height, vm_rect_width, vm_rect_height)


        # 4. Marcador de Posición Actual (Current Position) - Línea vertical roja
        current_x = int(self.current_msec * pixels_per_msec)
        
        painter.setPen(QPen(QColor(255, 0, 0), 2)) 
        painter.drawLine(current_x, 0, current_x, height) 

        painter.end()