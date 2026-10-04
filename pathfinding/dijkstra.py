"""Dijkstra's algorithm: uniform-cost search. Equivalent to A* with a
heuristic of zero, but implemented independently so each algorithm
stays easy to read and reason about in isolation."""
import heapq
import itertools

from pathfinding.base import Pathfinder, SearchState


class Dijkstra(Pathfinder):
    name = "Dijkstra"

    def search(self, start, goal):
        counter = itertools.count()
        open_heap = [(0, next(counter), start)]
        open_set = {start}
        came_from = {}
        g_score = {start: 0}
        explored = set()

        while open_heap:
            _, _, current_pos = heapq.heappop(open_heap)
            if current_pos not in open_set:
                continue
            open_set.discard(current_pos)

            if current_pos == goal:
                path = self.reconstruct_path(came_from, current_pos)
                yield SearchState(frontier=open_set, explored=explored,
                                   current=current_pos, path=path,
                                   done=True, found=True)
                return

            explored.add(current_pos)
            current_cell = self.grid.get_cell(*current_pos)

            for neighbor in self.grid.neighbors(current_cell, self.diagonal):
                diag = self.diagonal and neighbor.col != current_cell.col and neighbor.row != current_cell.row
                step_cost = 1.4142 if diag else 1
                tentative_g = g_score[current_pos] + step_cost * neighbor.weight
                if tentative_g < g_score.get(neighbor.pos, float("inf")):
                    came_from[neighbor.pos] = current_pos
                    g_score[neighbor.pos] = tentative_g
                    heapq.heappush(open_heap, (tentative_g, next(counter), neighbor.pos))
                    open_set.add(neighbor.pos)

            yield SearchState(frontier=set(open_set), explored=set(explored),
                               current=current_pos, done=False, found=False)

        yield SearchState(frontier=set(), explored=explored, current=start,
                           path=[], done=True, found=False)
