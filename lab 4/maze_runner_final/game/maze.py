import random

CELL = 40  # cell size in pixels


def generate_maze(cols, rows):
    """Recursive backtracker maze generation. Returns 2D grid of walls."""
    visited = [[False] * cols for _ in range(rows)]
    # walls: each cell has [N, S, E, W]
    walls = [[[True, True, True, True] for _ in range(cols)] for _ in range(rows)]

    def neighbors(r, c):
        dirs = [(-1, 0, 0, 1), (1, 0, 1, 0), (0, 1, 2, 3), (0, -1, 3, 2)]
        result = []
        for dr, dc, wd, od in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                result.append((nr, nc, wd, od))
        return result

    stack = [(0, 0)]
    visited[0][0] = True
    while stack:
        r, c = stack[-1]
        nbrs = neighbors(r, c)
        if nbrs:
            nr, nc, wd, od = random.choice(nbrs)
            walls[r][c][wd] = False
            walls[nr][nc][od] = False
            visited[nr][nc] = True
            stack.append((nr, nc))
        else:
            stack.pop()
    return walls


def shortest_path(walls, start, goal):
    """Return the shortest path between two cells using Breadth-First Search.

    The path is returned as a list of (row, column) cells, including start
    and goal. An empty list means that no path exists.
    """
    rows = len(walls)
    cols = len(walls[0]) if rows else 0

    if not rows or not cols:
        return []

    start_r, start_c = start
    goal_r, goal_c = goal
    if not (0 <= start_r < rows and 0 <= start_c < cols):
        return []
    if not (0 <= goal_r < rows and 0 <= goal_c < cols):
        return []

    # Each entry stores the previous cell used to reach it.
    previous = [[None] * cols for _ in range(rows)]
    visited = [[False] * cols for _ in range(rows)]
    queue = [(start_r, start_c)]
    head = 0
    visited[start_r][start_c] = True

    # walls are [N, S, E, W]
    directions = [
        (-1, 0, 0, 1),  # North
        (1, 0, 1, 0),   # South
        (0, 1, 2, 3),   # East
        (0, -1, 3, 2),  # West
    ]

    while head < len(queue):
        r, c = queue[head]
        head += 1

        if (r, c) == (goal_r, goal_c):
            break

        for dr, dc, wall_dir, opposite_dir in directions:
            nr, nc = r + dr, c + dc

            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            if visited[nr][nc]:
                continue
            if walls[r][c][wall_dir]:
                continue

            # The shared wall must be open from both sides.
            if walls[nr][nc][opposite_dir]:
                continue

            visited[nr][nc] = True
            previous[nr][nc] = (r, c)
            queue.append((nr, nc))

    if not visited[goal_r][goal_c]:
        return []

    path = []
    current = (goal_r, goal_c)
    while current is not None:
        path.append(current)
        if current == (start_r, start_c):
            break
        r, c = current
        current = previous[r][c]

    path.reverse()
    return path


def cell_rect(r, c, import_pygame=None):
    import pygame
    return pygame.Rect(c * CELL, r * CELL, CELL, CELL)
