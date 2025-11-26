from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor
from features.grid.grid_data import GridNode, GridData # <--- NUEVAS IMPORTACIONES
from PySide6.QtCore import Qt, Signal, Slot 

class GridOverlayWidget(QWidget):
    """
    Widget transparente que dibuja el grid (triángulo + pines).
    No interfiere con el video; solo dibuja encima.
    """

    # Señal para avisar cuando un nodo ha sido movido
    node_moved = Signal(object)

    def __init__(self, grids_manager, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_AlwaysStackOnTop, True)

        self.grids_manager = grids_manager
        self.active_grid = None
        self._dragging_node = None

    def set_current_time(self, msec: int):
        """Actualiza el grid activo y fuerza un repintado."""
        self.active_grid = self.grids_manager.get_active_grid(msec)
        self.update()

    def paintEvent(self, event):
        if not self.active_grid:
            return
        painter = QPainter(self)
        pen = QPen(QColor(0, 180, 255), 2)
        painter.setPen(pen)
        A = self.active_grid.nodes["A"]
        B = self.active_grid.nodes["B"]
        C = self.active_grid.nodes["C"]
        painter.drawLine(A.x, A.y, B.x, B.y)
        painter.drawLine(B.x, B.y, C.x, C.y)
        painter.drawLine(C.x, C.y, A.x, A.y)
        painter.setPen(QPen(QColor(255, 150, 0), 1))
        painter.drawLine(A.x, A.y, C.x, C.y)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 180, 255))
        radius = 6
        for node in [A, B, C]:
            painter.drawEllipse(node.x - radius, node.y - radius, radius*2, radius*2)


    @Slot(object)
    def set_active_grid_data(self, grid_data: GridData | None):
        """
        🟢 CRÍTICO: Slot llamado por GridsManager (active_grid_changed) para 
        actualizar el grid que debe dibujar.
        """
        self.active_grid = grid_data
        self.update() # Forzar el redibujo

    def mousePressEvent(self, e):
        if not self.active_grid:
            return
        x, y = e.position().x(), e.position().y()
        for name, node in self.active_grid.nodes.items():
            if abs(node.x - x) < 10 and abs(node.y - y) < 10:
                self._dragging_node = name
                break

    def mouseMoveEvent(self, e):
        if self._dragging_node and self.active_grid:
            x, y = e.position().x(), e.position().y()
            
            # 1. Actualizar las coordenadas del nodo arrastrado
            self._dragging_node.x = int(x)
            self._dragging_node.y = int(y)
            
            # 2. Notificar que el nodo fue movido
            # Buscar el label correspondiente
            node_label = None
            for label, node in self.active_grid.nodes.items():
                if node is self._dragging_node:
                    node_label = label
                    break
            
            if node_label:
                # Emitimos la señal con el label y el objeto GridNode
                self.node_moved.emit({'label': node_label, 'node': self._dragging_node})
                
            # 3. Forzar repintado para mover el pin en la UI
            self.update()

    def mouseReleaseEvent(self, e):
        self._dragging_node = None
