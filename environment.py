"""
Environment module: defines the grid, individual cells, and static /
dynamic obstacle management.

This module is intentionally independent of both the pathfinding
algorithms and the rendering layer - it only exposes queries like
"is this cell walkable" and "what are this cell's neighbors", so any
of the three layers (environment / pathfinding / rendering) can be
changed without touching the others.
"""
import random

from config import GRID_COLS, GRID_ROWS, DIRECTIONS_8


class Cell:
    """A single grid cell. Only knows about its own state - never
    about search algorithms or how it will be drawn."""

    __slots__ = ("col", "row", "walkable", "weight")

    def __init__(self, col, row, walkable=True, weight=1):
        self.col = col
        self.row = row
        self.walkable = walkable
        self.weight = weight  # supports weighted terrain later on

    @property
    def pos(self):
        return (self.col, self.row)

    def __repr__(self):
        return f"Cell({self.col},{self.row},walkable={self.walkable})"


class DynamicObstacle:
    """An obstacle that patrols back and forth along a fixed path of
    cells. Completely independent of pathfinding; the Grid just asks
    it for its current position each frame."""

    def __init__(self, path_cells):
        if len(path_cells) < 2:
            raise ValueError("DynamicObstacle needs at least 2 cells to patrol between")
        self.path_cells = path_cells
        self.index = 0
        self.direction = 1

    @property
    def pos(self):
        return self.path_cells[self.index]

    def step(self):
        self.index += self.direction
        if self.index >= len(self.path_cells):
            self.index = len(self.path_cells) - 2
            self.direction = -1
        elif self.index < 0:
            self.index = 1
            self.direction = 1


def line_cells(a, b):
    """Bresenham's line algorithm - returns the list of grid cells
    from a to b inclusive. Used to turn two clicked endpoints into a
    walkable patrol path for a dynamic obstacle."""
    x0, y0 = a
    x1, y1 = b
    cells = []
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        cells.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy
    return cells


class Grid:
    """Owns the 2D array of Cells plus any dynamic obstacles.
    Provides the neighbor / walkability queries that pathfinding
    algorithms rely on, without knowing anything about A*, BFS, etc."""

    def __init__(self, cols=GRID_COLS, rows=GRID_ROWS):
        self.cols = cols
        self.rows = rows
        self.cells = [[Cell(c, r) for r in range(rows)] for c in range(cols)]
        self.dynamic_obstacles = []

    def in_bounds(self, col, row):
        return 0 <= col < self.cols and 0 <= row < self.rows

    def get_cell(self, col, row):
        return self.cells[col][row]

    def set_wall(self, col, row, is_wall=True):
        if self.in_bounds(col, row):
            self.cells[col][row].walkable = not is_wall

    def toggle_wall(self, col, row):
        if self.in_bounds(col, row):
            c = self.cells[col][row]
            c.walkable = not c.walkable

    def is_walkable(self, col, row, ignore_dynamic=False):
        if not self.in_bounds(col, row):
            return False
        if not self.cells[col][row].walkable:
            return False
        if not ignore_dynamic:
            for obs in self.dynamic_obstacles:
                if obs.pos == (col, row):
                    return False
        return True

    def neighbors(self, cell, diagonal=False):
        """Yield walkable neighbor cells. Diagonal moves are blocked
        if both orthogonal cells forming the corner are walls, so the
        robot never 'cuts the corner' through solid geometry."""
        dirs = DIRECTIONS_8 if diagonal else DIRECTIONS_8[:4]
        for dc, dr in dirs:
            nc, nr = cell.col + dc, cell.row + dr
            if not self.is_walkable(nc, nr):
                continue
            if diagonal and dc != 0 and dr != 0:
                if not self.is_walkable(cell.col + dc, cell.row) and not self.is_walkable(cell.col, cell.row + dr):
                    continue
            yield self.cells[nc][nr]

    def clear_walls(self):
        for col in self.cells:
            for cell in col:
                cell.walkable = True

    def randomize_obstacles(self, density=0.22, exclude=None):
        """Fill the grid with random static obstacles, excluding a
        set of protected cells (typically start/goal)."""
        exclude = exclude or set()
        self.clear_walls()
        for col in self.cells:
            for cell in col:
                if cell.pos in exclude:
                    continue
                if random.random() < density:
                    cell.walkable = False

    def add_dynamic_obstacle(self, path_cells):
        self.dynamic_obstacles.append(DynamicObstacle(list(path_cells)))

    def clear_dynamic_obstacles(self):
        self.dynamic_obstacles = []

    def step_dynamic_obstacles(self):
        for obs in self.dynamic_obstacles:
            obs.step()

    def dynamic_obstacle_positions(self):
        return {obs.pos for obs in self.dynamic_obstacles}
