# =====================================
# FILE: grids_manager.py
# =====================================


class Node:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class Grid:
    def __init__(self, grid_id: str, nodes: dict):
        self.id = grid_id
        self.nodes = nodes # {'A': Node, 'B': Node, 'C': Node}


class GridsManager:
    def __init__(self):
        self.grids: dict[str, Grid] = {}
        self.active_grid_id: str | None = None


    def add_grid(self, grid: Grid):
        """Añade un objeto Grid, usando su ID interno como clave."""
        self.grids[grid.id] = grid


    def get(self, grid_id: str) -> Grid | None:
        return self.grids.get(grid_id)

    
    def all(self) -> dict[str, Grid]:
        """Devuelve todos los grids (necesario para GridsListWidget)."""
        return self.grids


    def get_active_grid(self, msec: int) -> Grid | None:
        if self.active_grid_id:
            return self.grids.get(self.active_grid_id)
        return None


    def set_active_grid(self, grid_id: str):
        if grid_id in self.grids:
            self.active_grid_id = grid_id