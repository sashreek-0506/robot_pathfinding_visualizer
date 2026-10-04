# Robot Path Planning Visualizer

A real-time visualization of A*, Dijkstra, and BFS pathfinding for a simulated robot navigating a 2D grid with static and dynamic obstacles, built with Python and Pygame.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

Requires Python 3.9+.

## Controls

| Input | Action |
|---|---|
| Left click | Place start cell |
| Right click | Place goal cell |
| Shift + left-click drag, or middle-click drag | Paint / erase walls |
| `Space` | Run the selected algorithm (animated) |
| `C` | Compare A*, Dijkstra, and BFS side by side on the current grid |
| `R` | Reset grid (clears walls, dynamic obstacles, robot) |
| `G` | Generate random static obstacles |
| `O` | Enter "add dynamic obstacle" mode, then click two cells to define a patrol line |
| `1` / `2` / `3` | Switch algorithm to A* / Dijkstra / BFS |
| `D` | Toggle diagonal movement |

All of these are also available as buttons in the sidebar.

## What it does

- **Live search animation**: as an algorithm runs, explored nodes (blue), the current frontier (yellow), and the final path (green) are drawn onto the grid in real time.
- **Robot simulation**: once a path is found, a robot walks it cell by cell.
- **Dynamic obstacles**: obstacles patrol back and forth along a line you draw. If one steps into the robot's planned path, the robot automatically replans from its current position rather than restarting from the original start cell.
- **Algorithm comparison**: pressing `C` runs A*, Dijkstra, and BFS on the identical grid and reports nodes explored, path length, and time taken for each, side by side.

## Architecture

The project follows the separation-of-concerns split described by the design:

| File | Responsibility |
|---|---|
| `config.py` | All tunable constants and the color palette. |
| `environment.py` | `Grid`, `Cell`, and `DynamicObstacle` — the world model. Knows nothing about search or rendering. |
| `pathfinding/base.py` | `Pathfinder` abstract base class. Every algorithm is a generator yielding a `SearchState` after each step, which is what makes the algorithms swappable and animatable. |
| `pathfinding/astar.py`, `dijkstra.py`, `bfs.py` | The three interchangeable search strategies. |
| `heuristics.py` | Manhattan / Euclidean / Chebyshev heuristics, decoupled from the A* implementation. |
| `robot.py` | The `Robot` entity that walks a computed path and detects when it's blocked. |
| `renderer.py` / `ui.py` | The Pygame drawing layer and sidebar widgets. Has no knowledge of *how* a path was found. |
| `main.py` | The `App` class — the only place that wires environment, pathfinding, robot, and renderer together, and handles the event loop. |

Because every algorithm implements the same `Pathfinder` interface (a generator of `SearchState`s), `main.py` treats A*, Dijkstra, and BFS completely interchangeably — swapping the algorithm is a one-line dictionary lookup, and adding a fourth algorithm (e.g. Greedy Best-First) means writing one new file with no changes anywhere else.

## Notes on the algorithms

- **A\*** uses `g + h` (cost-so-far plus a heuristic estimate to the goal), so it explores far fewer nodes than the uninformed searches while still finding the shortest path.
- **Dijkstra** is uniform-cost search — equivalent to A* with a heuristic of zero. It explores more broadly than A* but still guarantees the shortest path under the grid's cost model.
- **BFS** ignores cost entirely and expands in uniform rings. It only guarantees a shortest path when every move has equal cost, which is why it's included as the baseline comparison point.

Run the comparison mode (`C`) on a grid with some obstacles to see this difference directly — A* typically explores 3-4x fewer nodes than BFS/Dijkstra for the same optimal path.
