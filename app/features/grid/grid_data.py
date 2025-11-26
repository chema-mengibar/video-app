# src/app/features/grid/grid_data.py

class GridNode:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class GridSegment:
    def __init__(self, name: str, distance: float = 0.0, computed: bool = False):
        self.name = name              # "AB", "BC", "CA", "AC"
        self.distance = distance      # metros
        self.computed = computed      # si se calcula automáticamente


class GridData:
    """
    Representa un solo grid con 3 pines y 4 segmentos.
    """
    def __init__(self, msec_from: int, msec_to: int):
        self.msec_from = msec_from
        self.msec_to = msec_to

        # Puntos A, B, C (coordenadas del canvas/video)
        self.nodes = {
            "A": GridNode(),
            "B": GridNode(),
            "C": GridNode(),
        }

        # Segmentos laterales + segmento interno AC
        self.segments = {
            "AB": GridSegment("AB"),
            "BC": GridSegment("BC"),
            "CA": GridSegment("CA"),
            "AC": GridSegment("AC"),  # segmento interno para medir
        }

    def contains_time(self, msec: int) -> bool:
        return self.msec_from <= msec <= self.msec_to
