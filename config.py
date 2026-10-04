"""
Configuration constants for the Robot Path Planning Visualizer.

Centralizing these values keeps the environment, pathfinding, and
rendering modules free of magic numbers, and means the whole app's
look and feel can be tuned from one place.
"""

# --- Grid dimensions ---
CELL_SIZE = 24
GRID_COLS = 40
GRID_ROWS = 25

SIDEBAR_WIDTH = 300
WINDOW_WIDTH = GRID_COLS * CELL_SIZE + SIDEBAR_WIDTH
WINDOW_HEIGHT = GRID_ROWS * CELL_SIZE

FPS = 60
SEARCH_STEPS_PER_FRAME = 8       # search steps revealed per frame (animation speed)
ROBOT_MOVE_DELAY_MS = 90         # ms between robot moves along the final path
DYNAMIC_OBSTACLE_MOVE_MS = 400   # ms between dynamic obstacle steps


class Colors:
    BACKGROUND = (18, 18, 24)
    GRID_LINE = (40, 40, 48)
    EMPTY = (28, 28, 36)
    WALL = (60, 60, 70)
    START = (56, 189, 130)
    GOAL = (230, 90, 90)
    FRONTIER = (240, 200, 80)
    EXPLORED = (70, 100, 160)
    PATH = (120, 220, 150)
    ROBOT = (250, 250, 250)
    DYNAMIC_OBSTACLE = (200, 90, 200)
    TEXT = (230, 230, 235)
    TEXT_DIM = (150, 150, 160)
    PANEL_BG = (26, 26, 34)
    PANEL_BORDER = (50, 50, 60)
    ACCENT = (90, 160, 240)
    BUTTON = (40, 44, 56)
    BUTTON_HOVER = (56, 60, 76)


DIRECTIONS_4 = [(0, -1), (0, 1), (-1, 0), (1, 0)]
DIRECTIONS_8 = DIRECTIONS_4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]
