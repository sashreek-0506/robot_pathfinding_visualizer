"""Robot entity: moves step-by-step along a computed path.

Kept separate from pathfinding so "the thing that follows the path"
can evolve independently of "the thing that finds the path" - e.g.
adjusting movement speed, or detecting that a dynamic obstacle has
blocked the way ahead and a replan is needed.
"""
import pygame


class Robot:
    def __init__(self, start_pos, move_delay_ms=90):
        self.pos = start_pos
        self.path = []
        self.path_index = 0
        self.move_delay_ms = move_delay_ms
        self._last_move_time = 0
        self.moving = False

    def set_path(self, path):
        self.path = path
        self.path_index = 0
        self.moving = bool(path)
        self._last_move_time = pygame.time.get_ticks()
        if path:
            self.pos = path[0]

    def blocked_ahead(self, grid):
        """Check whether the next step on the current path has become
        blocked (used to trigger dynamic replanning)."""
        if not self.moving or self.path_index + 1 >= len(self.path):
            return False
        nxt = self.path[self.path_index + 1]
        return not grid.is_walkable(*nxt)

    def update(self, now_ms):
        if not self.moving:
            return
        if now_ms - self._last_move_time < self.move_delay_ms:
            return
        if self.path_index + 1 >= len(self.path):
            self.moving = False
            return
        self.path_index += 1
        self.pos = self.path[self.path_index]
        self._last_move_time = now_ms

    def reset(self, start_pos):
        self.pos = start_pos
        self.path = []
        self.path_index = 0
        self.moving = False
