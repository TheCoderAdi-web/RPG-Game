import numpy as np
import random as r

from typing import Dict, Tuple, List, Literal
import numpy.typing as npt
# Import necessary entities and constants from game_data
from game_data import Enemy, Chest, level_size, GRID_SIZE, WALK_STEPS

def generate_random_walk_dungeon(grid_size: int, steps: int) -> npt.NDArray[np.int_]:
    """Generates a dungeon map using a random walk algorithm.

    Map key: 0=Wall (█), 1=Floor ( ), 2=Exit (now Floor), 4=Entrance ( )
    """
    grid: npt.NDArray[np.int_] = np.zeros((grid_size, grid_size), dtype=int)

    moves: Tuple[Tuple[int, int], ...] = ((-1, 0), (1, 0), (0, -1), (0, 1))

    # Start near the center
    row, col = grid_size // 2, grid_size // 2

    # Initialize a 3x3 area of floor tiles at the start
    for r_offset in range(-1, 2):
        for c_offset in range(-1, 2):
            r_new = row + r_offset
            c_new = col + c_offset
            if 0 <= r_new < grid_size and 0 <= c_new < grid_size:
                grid[r_new, c_new] = 1

    # Perform the random walk
    for _ in range(steps):
        dr, dc = r.choice(moves)

        new_row, new_col = row + dr, col + dc

        if 0 <= new_row < grid_size and 0 <= new_col < grid_size:
            row, col = new_row, new_col
            grid[row, col] = 1

    # Set start point
    start_row, start_col = grid_size // 2, grid_size // 2

    # Entrance (4) - player spawn
    grid[start_row, start_col] = 4

    # Remove the Exit tile (2) functionality:
    # Any tile with a value of 2 is explicitly converted back to floor (1).
    grid[grid == 2] = 1

    return grid

def find_entrance(grid: npt.NDArray[np.int_]) -> Tuple[int, int]:
    """Returns the (x, y) coordinates of the Entrance (4)"""
    entrance_coords = np.where(grid == 4)

    if len(entrance_coords[0]) > 0:
        # Note: numpy uses (row, column), which corresponds to (y, x) in the game
        start_y = int(entrance_coords[0][0])
        start_x = int(entrance_coords[1][0])
        return start_x, start_y
    else:
        # Fallback to center if entrance is somehow missing
        grid_size = grid.shape[0]
        return grid_size // 2, grid_size // 2

def generate_entities(dungeon_map: npt.NDArray[np.int_]) -> Tuple[List[Enemy], List[Chest]]:
    """Places enemies and chests randomly on floor tiles (1) in the dungeon map."""
    floor_tiles = np.argwhere(dungeon_map == 1)
    r.shuffle(floor_tiles)

    enemies: List[Enemy] = []
    chests: List[Chest] = []

    # Simple logic: up to 3 enemies and 2 chests
    num_enemies = min(3, len(floor_tiles) // 3)
    num_chests = min(2, len(floor_tiles) // 4)

    # Place entities on unique floor tiles
    used_tiles = set()

    def get_unique_tile():
        for i in range(len(floor_tiles)):
            y, x = floor_tiles[i]
            if (x, y) not in used_tiles:
                used_tiles.add((x, y))
                return x, y
        return None, None

    # Place enemies
    for _ in range(num_enemies):
        x, y = get_unique_tile()
        if x is not None:
            enemies.append(Enemy(x, y))

    # Place chests
    possible_items = ["Bow", "Sword"]
    for _ in range(num_chests):
        x, y = get_unique_tile()
        if x is not None:
            item = r.choice(possible_items)
            chests.append(Chest(x, y, item))

    return enemies, chests