# features/drawing.py

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QMouseEvent
from PySide6.QtCore import Qt, QPoint, QSize, QRect

class DrawingVideoLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.drawing_enabled = False
        
        # --- Variables de Dibujo Temporal y Persistente ---
        # 1. Almacena el dibujo actual que se va a guardar (una lista de caminos)
        self.finished_paths = [] 
        # 2. Almacena el camino que se está dibujando actualmente
        self.current_path = [] 
        # 3. Almacena los caminos que deben mostrarse para el frame actual (cargados por DrawManager)
        self.active_paths = [] 
        
        self.last_point = QPoint()
        
        # Configuración del pincel
        self.pen_color = QColor(255, 0, 0) # Rojo inicial
        self.pen_width = 3
        
        # Guardar el tamaño del widget al momento de dibujar para escalado
        self.original_size = QSize(0, 0) 
        

    # --- Métodos de Interfaz (Llamados desde main.py) ---
    
    def enable_drawing(self, enable):
        """Habilita o deshabilita la captura de eventos de ratón."""
        self.drawing_enabled = enable

    def clear_drawing(self):
        """Limpia el dibujo actual (lo que se va a guardar)."""
        self.finished_paths = []
        self.current_path = []
        self.update()

    def get_finished_paths(self):
        """Retorna los paths guardados y limpia el canvas actual para un nuevo dibujo."""
        paths_to_save = self.finished_paths.copy()
        self.finished_paths = [] # Limpia el canvas para el siguiente dibujo
        
        # Necesitamos saber el tamaño en el que se dibujó para el escalado
        paths_to_return = {
            # Guardamos el tamaño de referencia del widget en tupla
            'size': self.original_size.toTuple(),
            'paths': paths_to_save
        }
        return paths_to_return

    def set_active_paths(self, paths):
        """Establece los paths temporales que deben mostrarse para el frame actual."""
        self.active_paths = paths
        
    def set_pen_color(self, color: QColor):
        """Actualiza el color del pincel (NUEVA FUNCIONALIDAD)."""
        self.pen_color = color


    # --- Lógica de Escalado y Puntos ---
    
    def scale_point(self, point_dict, original_size):
        """Escala un punto (x, y) de las coordenadas originales al tamaño actual del widget."""
        
        current_width = self.width()
        current_height = self.height()
        
        original_width = original_size[0]
        original_height = original_size[1]
        
        # Evitar división por cero
        if original_width == 0 or original_height == 0:
            return QPoint(point_dict['x'], point_dict['y'])
        
        scaled_x = int(point_dict['x'] * current_width / original_width)
        scaled_y = int(point_dict['y'] * current_height / original_height)
        
        return QPoint(scaled_x, scaled_y)


    # --- Eventos de Ratón para Dibujar ---
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing_enabled:
            self.last_point = event.pos()
            # Guardamos el punto en coordenadas locales (del widget)
            self.current_path = [{'x': self.last_point.x(), 'y': self.last_point.y()}]
            
            # Guardar el tamaño del widget para usarlo como referencia al guardar/cargar
            self.original_size = self.size() 

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.drawing_enabled:
            current_pos = event.pos()
            
            # 1. Actualizar el path en curso
            self.current_path.append({'x': current_pos.x(), 'y': current_pos.y()})
            self.last_point = current_pos
            
            self.update() # Llama a paintEvent para redibujar

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing_enabled and len(self.current_path) > 0:
            # 2. Finalizar el camino y moverlo a la lista de caminos terminados
            self.finished_paths.append(self.current_path)
            self.current_path = []
            self.update()

    # --- Evento de Pintado Combinado ---
    def paintEvent(self, event):
        # 1. Pintar el Pixmap del video (lo que viene del controlador)
        super().paintEvent(event) 
        
        # 💡 Usar 'with' asegura que painter.end() se llame automáticamente.
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.Antialiasing, True)
            
            # El pincel ahora usa el color actualizado por set_pen_color
            pen = QPen(self.pen_color, self.pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)

            # 2. Dibujar Paths ACTIVOS (Dibujos temporales cargados de DrawManager)
            # Nota: Estos paths usan el color en el que fueron dibujados (si la lógica se extiende)
            # Por ahora, usamos el color actual del pincel para todos los dibujos.
            
            for entry in self.active_paths:
                path_data = entry.get('paths', {}).get('paths', [])
                original_size = entry.get('paths', {}).get('size', (self.width(), self.height()))
                
                for path in path_data:
                    if len(path) > 1:
                        
                        # Dibuja el camino con escalado de coordenadas
                        start_point_dict = path[0]
                        start_point = self.scale_point(start_point_dict, original_size)
                        
                        for point_dict in path[1:]:
                            end_point = self.scale_point(point_dict, original_size)
                            painter.drawLine(start_point, end_point)
                            start_point = end_point 
            
            # 3. Dibujar Paths ACTUALES (Dibujo del usuario en este momento)
            
            # 3a. Dibujar Paths Terminados (finished_paths - Ya en coordenadas locales)
            for path in self.finished_paths:
                 if len(path) > 1:
                    start_point = QPoint(path[0]['x'], path[0]['y'])
                    for point_dict in path[1:]:
                        end_point = QPoint(point_dict['x'], point_dict['y'])
                        painter.drawLine(start_point, end_point)
                        start_point = end_point

            # 3b. Dibujar Path en progreso (current_path - Ya en coordenadas locales)
            if len(self.current_path) > 1:
                start_point = QPoint(self.current_path[0]['x'], self.current_path[0]['y'])
                for point_dict in self.current_path[1:]:
                    # ¡CORREGIDO! Ya no hay point_point
                    end_point = QPoint(point_dict['x'], point_dict['y']) 
                    painter.drawLine(start_point, end_point)
                    start_point = end_point

    def resizeEvent(self, event):
        super().resizeEvent(event)