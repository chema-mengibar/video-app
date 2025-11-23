# ui_components.py
# Contiene widgets de interfaz (UI) personalizados.

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor 
from PySide6.QtCore import Qt

class TimelineRuler(QWidget):
    """
    Widget de regla personalizado para dibujar marcas de tiempo sobre el timeline.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(50) 
        self.total_duration_msec = 0

    def _format_time(self, msec):
        """Convierte milisegundos a formato MM:SS (sin ms para mantener el espacio de la regla)."""
        seconds = int(msec / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def set_duration(self, msec):
        """Establece la duración total del video para dibujar la regla."""
        self.total_duration_msec = msec
        self.update() 

    def paintEvent(self, event):
        """Método de pintado para dibujar las marcas y etiquetas de tiempo."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.total_duration_msec == 0:
            return

        pen = QPen(QColor(150, 150, 150))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(QColor(0, 0, 0))
        
        width = self.width()
        
        margin = 10 
        draw_width = width - (margin * 2) 
        
        # Dibuja 11 marcas (0%, 10%, ..., 100%)
        for i in range(0, 11): 
            
            percentage = i / 10.0 
            x_pos = int(draw_width * percentage) + margin

            if i == 10:
                x_pos = width - margin

            # Dibuja la línea de la marca
            painter.drawLine(x_pos, 0, x_pos, 10) 
            
            # Calcula y dibuja el texto de tiempo
            time_msec = int(self.total_duration_msec * percentage)
            time_str = self._format_time(time_msec)
            
            text_rect = painter.fontMetrics().boundingRect(time_str)
            text_x = x_pos - text_rect.width() // 2
            text_y = 10 + 5 + text_rect.height()

            # Ajustes para los extremos (0% y 100%)
            if i == 0: 
                text_x = margin
            elif i == 10:
                text_x = width - margin - text_rect.width()
            
            painter.drawText(text_x, text_y, time_str)
            
        painter.end()