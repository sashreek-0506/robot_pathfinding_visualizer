"""
Abstract base class for all pathfinding strategies.

Every algorithm is implemented as a generator (`search`) that yields
a SearchState after each node expansion. This lets the renderer
animate the search frontier growing in real time regardless of which
algorithm is running, and lets a headless "compare algorithms" mode
simply drain the generator to collect final statistics.

Keeping this contract identical across A*, Dijkstra, and BFS is what
lets main.py treat them completely interchangeably.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from time import perf_counter


@dataclass
class SearchState:
    """Snapshot of a pathfinder's progress at a single step."""
    frontier: set
    explored: set
    current: tuple
    path: list = field(default_factory=list)
    done: bool = False
    found: bool = False


@dataclass
class SearchResult:
    """Final summary statistics once a search finishes."""
    algorithm: str
    found: bool
    path: list
    nodes_explored: int
    path_length: int
    elapsed_ms: float


class Pathfinder(ABC):
    """Subclass and implement `search()` as a generator that yields
    SearchState objects, ending with one that has done=True."""

    name = "Pathfinder"

    def __init__(self, grid, diagonal=False):
        self.grid = grid
        self.diagonal = diagonal

    @abstractmethod
    def search(self, start, goal):
        """Generator yielding SearchState after each node expansion."""
        raise NotImplementedError

    def run_to_completion(self, start, goal):
        """Convenience method for the non-visual 'compare algorithms'
        mode. Drains the generator and returns a SearchResult."""
        t0 = perf_counter()
        explored_count = 0
        final_state = None
        for state in self.search(start, goal):
            explored_count = len(state.explored)
            final_state = state
        elapsed_ms = (perf_counter() - t0) * 1000
        path = final_state.path if final_state else []
        return SearchResult(
            algorithm=self.name,
            found=bool(final_state and final_state.found),
            path=path,
            nodes_explored=explored_count,
            path_length=len(path),
            elapsed_ms=elapsed_ms,
        )

    @staticmethod
    def reconstruct_path(came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
