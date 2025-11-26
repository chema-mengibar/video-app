# src/app/features/draw/drawing_label.py

from PySide6.QtWidgets import QLabel, QSizePolicy # 🟢 CORRECCIÓN: Se añade QSizePolicy
from PySide6.QtGui import QColor, QPen, QPainter, QPixmap
from PySide6.QtCore import Qt, QPoint

class DrawingVideoLabel(QLabel):
    """
    QLabel especializado que actúa como canvas de dibujo y visor de video.
    Maneja eventos de ratón para dibujar y muestra paths activos persistidos.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # ATRIBUTOS REQUERIDOS POR MAINWINDOW
        self.current_pen_color = QColor(255, 0, 0) # Rojo por defecto
        self.pen_thickness = 3
        
        # Estado de dibujo
        self.drawing_enabled = False
        self.drawing_active = False
        self.last_point = QPoint()
        self.current_path_points = []
        self.finished_paths = [] # Paths temporales de la sesión de dibujo actual
        self.active_paths_to_display = [] # Paths cargados del DrawService

        self.setMouseTracking(True)
        # 🟢 CORRECCIÓN: Se usa QSizePolicy.Expanding en lugar de QLabel.Expanding
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
        self.setMinimumSize(320, 240)
        
    # --- Interfaz para el Coordinador (MainWindow) ---

    def enable_drawing(self, enable: bool):
        """Habilita o deshabilita la capacidad de dibujar."""
        self.drawing_enabled = enable
        self.setCursor(Qt.CrossCursor if enable else Qt.ArrowCursor)

    def set_pen_color(self, color: QColor):
        """Establece el color del lápiz."""
        self.current_pen_color = color
        
    def clear_drawing(self):
        """Limpia solo los paths temporales (no persistidos)."""
        self.finished_paths = []
        self.update() # Forzar redibujo

    def get_finished_paths(self) -> list:
        """Retorna los paths temporales listos para ser persistidos."""
        # Se retorna una copia para que el Manager pueda procesarlos
        return self.finished_paths

    def set_active_paths(self, paths_data: list):
        """Establece los paths persistidos que deben dibujarse en el frame actual."""
        self.active_paths_to_display = paths_data
        
    # --- Eventos de Ratón (Lógica de Dibujo) ---

    def mousePressEvent(self, event):
        if self.drawing_enabled and event.button() == Qt.LeftButton:
            self.drawing_active = True
            self.last_point = event.pos()
            self.current_path_points = [self.last_point.toTuple()] # Inicializar nuevo path
            
    def mouseMoveEvent(self, event):
        if self.drawing_enabled and self.drawing_active:
            new_point = event.pos()
            
            # Almacenar puntos solo si se ha movido lo suficiente (opcional, para optimización)
            if (new_point - self.last_point).manhattanLength() > 2:
                self.current_path_points.append(new_point.toTuple())
                self.last_point = new_point
                self.update() # Solicitar redibujo
                
    def mouseReleaseEvent(self, event):
        if self.drawing_enabled and event.button() == Qt.LeftButton and self.drawing_active:
            self.drawing_active = False
            
            if len(self.current_path_points) > 1:
                # Almacenar el path temporal, incluyendo color y grosor
                self.finished_paths.append({
                    'color': self.current_pen_color.getRgb(),
                    'thickness': self.pen_thickness,
                    'points': self.current_path_points
                })
            self.current_path_points = []
            
    # --- Evento de Pintado ---

    def paintEvent(self, event):
        """Se llama para redibujar el widget (frame de video + dibujos)."""
        # 1. Dibujar el contenido base (el frame de video)
        super().paintEvent(event) 
        
        # 2. Inicializar el pintor
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # 3. Dibujar Paths Persistidos (del DrawService)
        self._draw_paths(painter, self.active_paths_to_display)

        # 4. Dibujar Paths Temporales (de la sesión de dibujo actual)
        self._draw_paths(painter, self.finished_paths)
        
        # 5. Dibujar el trazo actual (si el ratón está presionado)
        if self.drawing_active and len(self.current_path_points) > 1:
            pen = QPen(self.current_pen_color, self.pen_thickness, Qt.SolidLine)
            painter.setPen(pen)
            
            p1 = QPoint(*self.current_path_points[0])
            for i in range(1, len(self.current_path_points)):
                p2 = QPoint(*self.current_path_points[i])
                painter.drawLine(p1, p2)
                p1 = p2
        
        painter.end()

    def _draw_paths(self, painter: QPainter, paths: list):
        """Lógica genérica para dibujar una lista de paths (sean persistidos o temporales)."""
        for path_data in paths:
            try:
                r, g, b, a = path_data.get('color', (255, 0, 0, 255))
                thickness = path_data.get('thickness', 3)
                points = path_data.get('points', [])
                
                pen = QPen(QColor(r, g, b, a), thickness, Qt.SolidLine)
                painter.setPen(pen)
                
                if len(points) > 1:
                    p1 = QPoint(*points[0])
                    for i in range(1, len(points)):
                        p2 = QPoint(*points[i])
                        painter.drawLine(p1, p2)
                        p1 = p2
            except Exception as e:
                print(f"Error drawing path: {e}")
                continue