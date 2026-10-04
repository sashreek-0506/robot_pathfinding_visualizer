"""
Rendering layer: draws the grid, obstacles, live search visualization,
robot, and sidebar UI/stats panel.

This module has zero knowledge of *how* a path is found - it only
knows how to draw whatever SearchState / grid / robot it's handed
each frame. That separation is what lets the same renderer display
A*, Dijkstra, or BFS without any special-casing.
"""
import pygame

from config import Colors, CELL_SIZE, GRID_COLS, SIDEBAR_WIDTH, WINDOW_HEIGHT


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont("consolas", 22, bold=True)
        self.font = pygame.font.SysFont("consolas", 16)
        self.font_small = pygame.font.SysFont("consolas", 13)
        self.buttons = []

    def cell_rect(self, col, row):
        return pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)

    def draw_grid(self, grid, start, goal, search_state, robot):
        for col in range(grid.cols):
            for row in range(grid.rows):
                cell = grid.get_cell(col, row)
                rect = self.cell_rect(col, row)
                color = Colors.EMPTY if cell.walkable else Colors.WALL
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, Colors.GRID_LINE, rect, width=1)

        if search_state:
            for pos in search_state.explored:
                pygame.draw.rect(self.screen, Colors.EXPLORED, self.cell_rect(*pos))
            for pos in search_state.frontier:
                pygame.draw.rect(self.screen, Colors.FRONTIER, self.cell_rect(*pos))
            if search_state.path:
                for pos in search_state.path:
                    pygame.draw.rect(self.screen, Colors.PATH, self.cell_rect(*pos))

        for pos in grid.dynamic_obstacle_positions():
            r = self.cell_rect(*pos).inflate(-6, -6)
            pygame.draw.rect(self.screen, Colors.DYNAMIC_OBSTACLE, r, border_radius=4)

        if start:
            pygame.draw.rect(self.screen, Colors.START, self.cell_rect(*start))
        if goal:
            pygame.draw.rect(self.screen, Colors.GOAL, self.cell_rect(*goal))

        if robot and robot.pos:
            center = self.cell_rect(*robot.pos).center
            pygame.draw.circle(self.screen, Colors.ROBOT, center, CELL_SIZE // 2 - 4)
            pygame.draw.circle(self.screen, Colors.BACKGROUND, center, CELL_SIZE // 2 - 4, width=2)

    def sidebar_rect(self):
        return pygame.Rect(GRID_COLS * CELL_SIZE, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)

    def draw_sidebar(self, app_state):
        rect = self.sidebar_rect()
        pygame.draw.rect(self.screen, Colors.PANEL_BG, rect)
        pygame.draw.line(self.screen, Colors.PANEL_BORDER, (rect.left, 0), (rect.left, WINDOW_HEIGHT), 2)

        x = rect.left + 18
        title = self.font_title.render("Path Planner", True, Colors.TEXT)
        self.screen.blit(title, (x, 16))

        for btn in self.buttons:
            btn.draw(self.screen)
        y = max((b.rect.bottom for b in self.buttons), default=56) + 14

        pygame.draw.line(self.screen, Colors.PANEL_BORDER, (x, y), (rect.right - 18, y), 1)
        y += 12
        header = self.font.render("Last Run", True, Colors.ACCENT)
        self.screen.blit(header, (x, y))
        y += 24

        result = app_state.get("last_result")
        if result:
            lines = [
                f"Algorithm: {result.algorithm}",
                f"Path found: {'yes' if result.found else 'no'}",
                f"Nodes explored: {result.nodes_explored}",
                f"Path length: {result.path_length}",
                f"Time: {result.elapsed_ms:.2f} ms",
            ]
            for line in lines:
                text = self.font_small.render(line, True, Colors.TEXT_DIM)
                self.screen.blit(text, (x, y))
                y += 20
        else:
            text = self.font_small.render("Run a search to see stats", True, Colors.TEXT_DIM)
            self.screen.blit(text, (x, y))
            y += 20

        compare = app_state.get("compare_results")
        if compare:
            y += 10
            pygame.draw.line(self.screen, Colors.PANEL_BORDER, (x, y), (rect.right - 18, y), 1)
            y += 12
            header = self.font.render("Comparison", True, Colors.ACCENT)
            self.screen.blit(header, (x, y))
            y += 22
            col_w = (SIDEBAR_WIDTH - 36) // 3
            for i, h in enumerate(["Algo", "Nodes", "Len"]):
                t = self.font_small.render(h, True, Colors.TEXT)
                self.screen.blit(t, (x + i * col_w, y))
            y += 18
            for r in compare:
                row = [r.algorithm, str(r.nodes_explored), str(r.path_length)]
                for i, val in enumerate(row):
                    t = self.font_small.render(val, True, Colors.TEXT_DIM)
                    self.screen.blit(t, (x + i * col_w, y))
                y += 18

        y = WINDOW_HEIGHT - 150
        pygame.draw.line(self.screen, Colors.PANEL_BORDER, (x, y), (rect.right - 18, y), 1)
        y += 10
        instructions = [
            "Left click: place start",
            "Right click: place goal",
            "Shift+drag / mid click: walls",
            "Space: run search",
            "C: compare all algorithms",
            "R: reset grid",
            "G: random obstacles",
            "O: add dynamic obstacle",
        ]
        for line in instructions:
            text = self.font_small.render(line, True, Colors.TEXT_DIM)
            self.screen.blit(text, (x, y))
            y += 17
