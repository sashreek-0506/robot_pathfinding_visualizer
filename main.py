"""
Robot Path Planning Visualizer
--------------------------------
Entry point: wires together the Grid (environment), the pathfinding
algorithms (A*, Dijkstra, BFS), the Robot, and the Pygame Renderer.

Run with:  python main.py
"""
import sys
from time import perf_counter

import pygame

from config import (
    CELL_SIZE, GRID_COLS, GRID_ROWS, WINDOW_WIDTH, WINDOW_HEIGHT,
    FPS, SEARCH_STEPS_PER_FRAME, ROBOT_MOVE_DELAY_MS, DYNAMIC_OBSTACLE_MOVE_MS,
    Colors,
)
from environment import Grid, line_cells
from robot import Robot
from renderer import Renderer
from ui import Button
from pathfinding.base import SearchResult
from pathfinding.astar import AStar
from pathfinding.dijkstra import Dijkstra
from pathfinding.bfs import BFS


ALGORITHMS = {"astar": AStar, "dijkstra": Dijkstra, "bfs": BFS}


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Robot Path Planning Visualizer")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.grid = Grid(GRID_COLS, GRID_ROWS)
        self.renderer = Renderer(self.screen)

        self.start = (2, GRID_ROWS // 2)
        self.goal = (GRID_COLS - 3, GRID_ROWS // 2)
        self.robot = Robot(self.start, ROBOT_MOVE_DELAY_MS)

        self.algorithm_key = "astar"
        self.diagonal = False

        self.search_gen = None
        self.search_state = None
        self.searching = False
        self.search_start_time = 0

        self.last_result = None
        self.compare_results = None
        self.app_state = {"last_result": None, "compare_results": None}

        self.dynamic_mode = False
        self.placing_dynamic = []   # collects up to 2 clicks to define a patrol line
        self.last_dyn_move = 0
        self.dragging_wall = None   # True = painting walls, False = erasing, None = idle

        self._build_buttons()

    # ---------------------------------------------------------- UI setup
    def _build_buttons(self):
        font = self.renderer.font
        x = GRID_COLS * CELL_SIZE + 18
        w, h, gap = 84, 30, 8
        y = 56

        def algo_btn(key, label, col_i):
            return Button((x + col_i * (w + gap), y, w, h), label,
                           lambda k=key: self.set_algorithm(k), font,
                           active_check=lambda k=key: self.algorithm_key == k)

        self.renderer.buttons = [
            algo_btn("astar", "A*", 0),
            algo_btn("dijkstra", "Dij.", 1),
            algo_btn("bfs", "BFS", 2),
        ]
        y += h + gap
        full_w = 3 * w + 2 * gap

        self.renderer.buttons.append(
            Button((x, y, full_w, h), "Toggle Diagonal", self.toggle_diagonal, font,
                   active_check=lambda: self.diagonal)
        )
        y += h + gap
        self.renderer.buttons.append(
            Button((x, y, full_w, h), "Run Search  [Space]", self.start_search, font)
        )
        y += h + gap
        self.renderer.buttons.append(
            Button((x, y, full_w, h), "Compare All  [C]", self.compare_all, font)
        )
        y += h + gap
        half_w = full_w // 2 - 4
        self.renderer.buttons.append(
            Button((x, y, half_w, h), "Random  [G]", self.random_obstacles, font)
        )
        self.renderer.buttons.append(
            Button((x + half_w + 8, y, half_w, h), "Reset  [R]", self.reset_grid, font)
        )
        y += h + gap
        self.renderer.buttons.append(
            Button((x, y, full_w, h), "Add Dynamic Obst. [O]", self.toggle_dynamic_mode, font,
                   active_check=lambda: self.dynamic_mode)
        )

    # ---------------------------------------------------------- actions
    def set_algorithm(self, key):
        self.algorithm_key = key
        self._clear_search()

    def toggle_diagonal(self):
        self.diagonal = not self.diagonal
        self._clear_search()

    def toggle_dynamic_mode(self):
        self.dynamic_mode = not self.dynamic_mode
        self.placing_dynamic = []

    def random_obstacles(self):
        self.grid.randomize_obstacles(density=0.22, exclude={self.start, self.goal})
        self._clear_search()

    def reset_grid(self):
        self.grid.clear_walls()
        self.grid.clear_dynamic_obstacles()
        self.robot.reset(self.start)
        self._clear_search()
        self.last_result = None
        self.compare_results = None
        self.app_state["last_result"] = None
        self.app_state["compare_results"] = None

    def _clear_search(self):
        self.search_gen = None
        self.search_state = None
        self.searching = False

    def start_search(self):
        if self.searching:
            return
        algo_cls = ALGORITHMS[self.algorithm_key]
        pathfinder = algo_cls(self.grid, diagonal=self.diagonal)
        self.search_gen = pathfinder.search(self.start, self.goal)
        self.search_state = None
        self.searching = True
        self.search_start_time = perf_counter()
        self.compare_results = None
        self.app_state["compare_results"] = None
        self.robot.reset(self.start)

    def replan_from_robot(self):
        """Triggered when a dynamic obstacle blocks the robot's
        current path - replans from the robot's live position rather
        than the original start cell."""
        algo_cls = ALGORITHMS[self.algorithm_key]
        pathfinder = algo_cls(self.grid, diagonal=self.diagonal)
        result = pathfinder.run_to_completion(self.robot.pos, self.goal)
        if result.found:
            self.robot.set_path(result.path)
        self.last_result = result
        self.app_state["last_result"] = result

    def compare_all(self):
        results = []
        for cls in ALGORITHMS.values():
            pf = cls(self.grid, diagonal=self.diagonal)
            results.append(pf.run_to_completion(self.start, self.goal))
        self.compare_results = results
        self.app_state["compare_results"] = results
        self.last_result = results[0]
        self.app_state["last_result"] = results[0]
        self._clear_search()

    # ---------------------------------------------------------- events
    def handle_mouse(self, event):
        gx, gy = event.pos
        if gx >= GRID_COLS * CELL_SIZE:
            for btn in self.renderer.buttons:
                btn.handle_event(event)
            return

        col, row = gx // CELL_SIZE, gy // CELL_SIZE
        if not self.grid.in_bounds(col, row):
            return
        protected = (col, row) in (self.start, self.goal)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.dynamic_mode:
                self.placing_dynamic.append((col, row))
                if len(self.placing_dynamic) == 2:
                    path = line_cells(*self.placing_dynamic)
                    self.grid.add_dynamic_obstacle(path)
                    self.placing_dynamic = []
                return
            if event.button == 1:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    if not protected:
                        self.dragging_wall = True
                        self.grid.set_wall(col, row, True)
                else:
                    self.start = (col, row)
                    self.robot.reset(self.start)
                    self._clear_search()
            elif event.button == 3:
                self.goal = (col, row)
                self._clear_search()
            elif event.button == 2 and not protected:
                self.dragging_wall = not self.grid.get_cell(col, row).walkable
                self.grid.toggle_wall(col, row)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_wall = None
        elif event.type == pygame.MOUSEMOTION:
            for btn in self.renderer.buttons:
                btn.handle_event(event)
            if self.dragging_wall is not None and not protected:
                self.grid.set_wall(col, row, self.dragging_wall)

    def handle_key(self, event):
        actions = {
            pygame.K_SPACE: self.start_search,
            pygame.K_c: self.compare_all,
            pygame.K_r: self.reset_grid,
            pygame.K_g: self.random_obstacles,
            pygame.K_o: self.toggle_dynamic_mode,
            pygame.K_d: self.toggle_diagonal,
            pygame.K_1: lambda: self.set_algorithm("astar"),
            pygame.K_2: lambda: self.set_algorithm("dijkstra"),
            pygame.K_3: lambda: self.set_algorithm("bfs"),
        }
        action = actions.get(event.key)
        if action:
            action()

    # ---------------------------------------------------------- update
    def update(self, now):
        if self.grid.dynamic_obstacles and now - self.last_dyn_move > DYNAMIC_OBSTACLE_MOVE_MS:
            self.grid.step_dynamic_obstacles()
            self.last_dyn_move = now
            if self.robot.blocked_ahead(self.grid):
                self.replan_from_robot()

        if self.searching and self.search_gen is not None:
            for _ in range(SEARCH_STEPS_PER_FRAME):
                try:
                    self.search_state = next(self.search_gen)
                except StopIteration:
                    self.searching = False
                    break
                if self.search_state.done:
                    self.searching = False
                    elapsed_ms = (perf_counter() - self.search_start_time) * 1000
                    result = SearchResult(
                        algorithm=ALGORITHMS[self.algorithm_key].name,
                        found=self.search_state.found,
                        path=self.search_state.path,
                        nodes_explored=len(self.search_state.explored),
                        path_length=len(self.search_state.path),
                        elapsed_ms=elapsed_ms,
                    )
                    self.last_result = result
                    self.app_state["last_result"] = result
                    if self.search_state.found:
                        self.robot.set_path(self.search_state.path)
                    break

        self.robot.update(now)

    def draw(self):
        self.screen.fill(Colors.BACKGROUND)
        self.renderer.draw_grid(self.grid, self.start, self.goal, self.search_state, self.robot)
        self.renderer.draw_sidebar(self.app_state)
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            now = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                    self.handle_mouse(event)
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event)

            self.update(now)
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    App().run()
