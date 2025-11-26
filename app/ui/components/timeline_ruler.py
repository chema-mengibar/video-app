# src/app/ui/components/timeline_ruler.py

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtCore import Qt, QSize
from ui.styles.theme import DarkTheme 

class TimelineRuler(QWidget):
    # ... (El código completo de TimelineRuler de la revisión anterior va aquí)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(15) 
        self.duration_msec = 0
        self.current_msec = 0
        # Ahora espera una lista simple de msec desde el service (simplificado)
        self.videomarks_msec = [] 

        self.setStyleSheet(DarkTheme.TIMELINE_RULER)
        
    def minimumSizeHint(self):
        return QSize(100, 15)

    def sizeHint(self):
        return QSize(500, 15)

    def update_videomarks(self, marks_msec: list):
        """Actualiza la lista de msec para los videomarks y fuerza el redibujo."""
        self.videomarks_msec = marks_msec
        self.update() # Forzar el redibujo

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        width = rect.width()
        height = rect.height()
        
        if self.duration_msec == 0:
            return

        pixels_per_msec = width / self.duration_msec
        
        # 2. Líneas de Tiempo (Lógica de escalado de marcas)
        step_msec = 1000 
        if pixels_per_msec * step_msec < 30: 
            step_msec = 5000 # 5 segundos
            if pixels_per_msec * step_msec < 30:
                step_msec = 10000 # 10 segundos
                if pixels_per_msec * step_msec < 30:
                    step_msec = 60000 # 🟢 1 minuto
                    if pixels_per_msec * step_msec < 30:
                        step_msec = 300000 # 🟢 5 minutos
                        if pixels_per_msec * step_msec < 30:
                            step_msec = 600000 # 🟢 10 minutos
                     
        painter.setPen(QColor("#555555")) 
        font = QFont("Arial", 6) 
        painter.setFont(font)
        
        for msec in range(0, int(self.duration_msec) + step_msec, step_msec):
            x = int(msec * pixels_per_msec)
            painter.drawLine(x, 0, x, height) 
            
            if pixels_per_msec * step_msec > 40: 
                total_seconds = int(msec / 1000)
                seconds = total_seconds % 60
                minutes = (total_seconds // 60) % 60
                time_str = f"{minutes:02d}:{seconds:02d}"
                painter.drawText(x + 2, height - 2, time_str) 

        # 3. Dibujar Videomarks
        VM_COLOR = QColor(DarkTheme.WOW_COLOR) 
        painter.setPen(Qt.NoPen) 
        painter.setBrush(VM_COLOR) 
        
        vm_rect_height = 12 
        vm_rect_width = 3 
        
        for msec in self.videomarks_msec: # Usar la lista simple de msec
            x = int(msec * pixels_per_msec)
            painter.drawRect(x - (vm_rect_width // 2), height - vm_rect_height, vm_rect_width, vm_rect_height)

        # 4. Marcador de Posición Actual
        current_x = int(self.current_msec * pixels_per_msec)
        painter.setPen(QPen(QColor(DarkTheme.WOW_COLOR), 2)) 
        painter.drawLine(current_x, 0, current_x, height) 

        painter.end()