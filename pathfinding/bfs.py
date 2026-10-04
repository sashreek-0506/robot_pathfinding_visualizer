"""Breadth-first search: explores in uniform 'rings' outward from the
start, ignoring cost entirely. Only guarantees a shortest path when
every move has equal cost (which is why it's a useful comparison
point against Dijkstra and A*)."""
from collections import deque

from pathfinding.base import Pathfinder, SearchState


class BFS(Pathfinder):
    name = "BFS"

    def search(self, start, goal):
        frontier = deque([start])
        frontier_set = {start}
        came_from = {}
        explored = set()

        while frontier:
            current_pos = frontier.popleft()
            frontier_set.discard(current_pos)

            if current_pos == goal:
                path = self.reconstruct_path(came_from, current_pos)
                yield SearchState(frontier=frontier_set, explored=explored,
                                   current=current_pos, path=path,
                                   done=True, found=True)
                return

            explored.add(current_pos)
            current_cell = self.grid.get_cell(*current_pos)

            for neighbor in self.grid.neighbors(current_cell, self.diagonal):
                if neighbor.pos in explored or neighbor.pos in frontier_set or neighbor.pos in came_from:
                    continue
                came_from[neighbor.pos] = current_pos
                frontier.append(neighbor.pos)
                frontier_set.add(neighbor.pos)

            yield SearchState(frontier=set(frontier_set), explored=set(explored),
                               current=current_pos, done=False, found=False)

        yield SearchState(frontier=set(), explored=explored, current=start,
                           path=[], done=True, found=False)
