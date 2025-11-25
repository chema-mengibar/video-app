from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, Signal

class GridOverlayWidget(QWidget):
    """
    Widget transparente que dibuja el grid (triángulo + pines).
    No interfiere con el video; solo dibuja encima.
    """

    # Señal para avisar cuando un nodo ha sido movido
    node_moved = Signal(object)  # podemos enviar el nodo o toda la info que necesite el editor

    def __init__(self, grids_manager, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_AlwaysStackOnTop, True)

        self.grids_manager = grids_manager
        self.active_grid = None
        self._dragging_node = None

    def set_current_time(self, msec: int):
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

    def mousePressEvent(self, e):
        if not self.active_grid:
            return
        x, y = e.position().x(), e.position().y()
        for name, node in self.active_grid.nodes.items():
            if abs(node.x - x) < 10 and abs(node.y - y) < 10:
                self._dragging_node = name
                break

    def mouseMoveEvent(self, e):
        if not self._dragging_node:
            return
        node = self.active_grid.nodes[self._dragging_node]
        node.x = int(e.position().x())
        node.y = int(e.position().y())
        self.update()
        # Emitimos la señal cada vez que se mueve un nodo
        self.node_moved.emit({"name": self._dragging_node, "x": node.x, "y": node.y})

    def mouseReleaseEvent(self, e):
        self._dragging_node = None
