# src/app/features/draw/drawing_label.py

from PySide6.QtWidgets import QLabel, QSizePolicy 
from PySide6.QtGui import QColor, QPen, QPainter, QPixmap
from PySide6.QtCore import Qt, QPoint, Slot # 🟢 Se añade Slot para métodos conectados

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
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
        self.setMinimumSize(320, 240)
        
    # --- Interfaz para MainWindow (SLOTS) ---

    def enable_drawing(self, enabled: bool):
        """Habilita o deshabilita la capacidad de dibujar con el ratón."""
        self.drawing_enabled = enabled
        self.setMouseTracking(enabled)
        # Cambiar el cursor a una cruz solo cuando el dibujo está habilitado
        self.setCursor(Qt.CrossCursor if enabled else Qt.ArrowCursor)

    @Slot(QColor)
    def set_pen_color(self, color: QColor):
        """Actualiza el color de dibujo."""
        self.current_pen_color = color

    @Slot(int)
    def set_pen_thickness(self, thickness: int):
        """🟢 CORRECCIÓN: Método para actualizar el grosor del trazo."""
        self.pen_thickness = thickness
        print(f"Grosor actualizado a: {thickness}")

    @Slot()
    def clear_drawing(self):
        """Limpia todos los trazos temporales de la sesión actual."""
        self.finished_paths = []
        self.update()

    def set_active_paths(self, paths: list):
        """Actualiza los paths que deben ser mostrados (cargados del ServiceManager)."""
        self.active_paths_to_display = paths
        
    def get_finished_paths(self) -> list:
        """Retorna los paths temporales guardados en la sesión."""
        return self.finished_paths

    @Slot()
    def undo_last_path(self):
        """🟢 CORRECCIÓN FATAL: Elimina el último trazo completado (Finished Path)."""
        if self.finished_paths:
            print("Deshaciendo el último trazo.")
            self.finished_paths.pop() # Elimina el último elemento de la lista
            self.update() # Fuerza el repintado
        else:
            print("No hay trazos para deshacer.")

    # --- Eventos de Ratón (Lógica de Dibujo) ---

    def mousePressEvent(self, event):
        if not self.drawing_enabled or event.button() != Qt.LeftButton:
            return

        self.drawing_active = True
        self.last_point = event.position().toPoint()
        self.current_path_points = [ (self.last_point.x(), self.last_point.y()) ] # Inicializa el nuevo trazo

    def mouseMoveEvent(self, event):
        if not self.drawing_active:
            return

        current_point = event.position().toPoint()
        
        # Guardar el punto como tupla (x, y)
        self.current_path_points.append( (current_point.x(), current_point.y()) ) 
        
        # ⚠️ Nota: No es necesario actualizar el last_point para el trazo actual
        # Pero es necesario forzar el repintado
        self.update() 

    def mouseReleaseEvent(self, event):
        if not self.drawing_active or event.button() != Qt.LeftButton:
            return

        # 1. Finalizar el trazo actual y guardar sus datos
        if len(self.current_path_points) > 1:
            # Crear un objeto de path con todos los datos necesarios para el ServiceManager
            path_data = {
                'color': self.current_pen_color.getRgb(),
                'thickness': self.pen_thickness,
                'points': self.current_path_points,
                'is_active': False # No activo hasta que se guarda y se consulta por tiempo
            }
            self.finished_paths.append(path_data)
        
        # 2. Resetear el estado de dibujo
        self.drawing_active = False
        self.current_path_points = []
        self.update()

    # --- Lógica de Pintado ---

    def paintEvent(self, event):
        """Maneja el evento de pintado para dibujar la imagen de fondo y los trazos."""
        
        # 1. Pintar la imagen de fondo (proporcionada por el setPixmap de MainWindow)
        super().paintEvent(event)
        
        # 2. Inicializar el pintor para dibujar *encima* de la imagen
        painter = QPainter(self)
        
        # 3. Dibujar paths persistidos (cargados del ServiceManager)
        self._draw_paths(painter, self.active_paths_to_display)
        
        # 4. Dibujar paths terminados de la sesión actual (no persistidos aún)
        self._draw_paths(painter, self.finished_paths)
        
        # 5. Dibujar el trazo actual (si el ratón está presionado)
        if self.drawing_active and len(self.current_path_points) > 1:
            pen = QPen(self.current_pen_color, self.pen_thickness, Qt.SolidLine)
            painter.setPen(pen)
            
            # Dibujar el trazo actual punto a punto
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
                # Fallback, si los datos del path están corruptos
                print(f"Error al dibujar path: {e}")