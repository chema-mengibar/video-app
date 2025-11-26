# src/app/ui/components/timeline_ruler.py

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtCore import Qt, QSize
from ui.styles.theme import DarkTheme 

class TimelineRuler(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(15) 
        self.duration_msec = 0
        self.current_msec = 0
        self.bookmarks_msec = [] 
        
        # ATRIBUTOS FALTANTES PARA LA PREVISUALIZACIÓN DEL SLIDER
        self.preview_msec = None      # Msec para la línea de previsualización (cuando se arrastra)
        self.is_previewing = False    # Bandera para saber si se está arrastrando el slider

        self.setStyleSheet(DarkTheme.TIMELINE_RULER)
        
    def minimumSizeHint(self):
        return QSize(100, 15)

    def sizeHint(self):
        return QSize(500, 15)

    def set_marks(self, marks_msec: list):
        """Método renombrado (update_bookmarks) para ser más genérico."""
        self.bookmarks_msec = marks_msec
        self.update() 

    # --- MÉTODOS AÑADIDOS PARA RESOLVER EL ERROR DE ATRIBUTO ---
    
    def set_preview_msec(self, msec: int):
        """Establece el tiempo de previsualización (msec) y fuerza el repintado."""
        self.preview_msec = msec
        if self.is_previewing:
            self.update()

    def start_preview(self):
        """Habilita el dibujo de la línea de previsualización."""
        self.is_previewing = True
        self.update()
        
    def end_preview(self):
        """Deshabilita el dibujo de la línea de previsualización y la resetea."""
        self.is_previewing = False
        self.preview_msec = None
        self.update()
        
    # -----------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        width = rect.width()
        height = rect.height()
        
        if self.duration_msec == 0:
            return

        pixels_per_msec = width / self.duration_msec
        
        # 1. Dibujar el fondo (implícito por el estilo de la hoja)

        # 2. Líneas de Tiempo (Lógica de escalado de marcas)
        step_msec = 1000 
        if pixels_per_msec * step_msec < 30: 
            step_msec = 5000 
            if pixels_per_msec * step_msec < 30:
                step_msec = 10000 
                if pixels_per_msec * step_msec < 30:
                    step_msec = 60000 
                    if pixels_per_msec * step_msec < 30:
                        step_msec = 300000 
                        if pixels_per_msec * step_msec < 30:
                            step_msec = 600000 
                            
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
        
        for msec in self.bookmarks_msec:
            x = int(msec * pixels_per_msec)
            painter.drawRect(x - (vm_rect_width // 2), height - vm_rect_height, vm_rect_width, vm_rect_height)

        # 4. Marcador de Posición de Previsualización (NUEVO: Dibujado debajo de la marca actual)
        if self.is_previewing and self.preview_msec is not None:
            preview_x = int(self.preview_msec * pixels_per_msec)
            # Usar un color diferente y punteado para la previsualización (ej: Naranja punteado)
            preview_pen = QPen(QColor(255, 150, 0), 1) 
            preview_pen.setStyle(Qt.DotLine)
            painter.setPen(preview_pen) 
            painter.drawLine(preview_x, 0, preview_x, height) 

        # 5. Marcador de Posición Actual (Aseguramos que esta línea esté siempre encima)
        current_x = int(self.current_msec * pixels_per_msec)
        painter.setPen(QPen(QColor(DarkTheme.WOW_COLOR), 2)) 
        painter.drawLine(current_x, 0, current_x, height) 

        painter.end()