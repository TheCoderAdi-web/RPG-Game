import numpy as np # type: ignore
import random as r

from typing import Dict, Tuple, List, Literal, Optional
import numpy.typing as npt # type: ignore
# Import necessary entities and constants from game_data
from game_data import Enemy, Chest, level_size, GRID_SIZE, WALK_STEPS

def generate_random_walk_dungeon(grid_size: int, steps: int) -> npt.NDArray[np.int_]:
    """Generates a dungeon map using a random walk algorithm.

    Map key: 0=Wall (█), 1=Floor, 2=Entrance,
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

    # Entrance (2) - player spawn
    grid[start_row, start_col] = 2

    return grid

def find_entrance(grid: npt.NDArray[np.int_]) -> Tuple[int, int]:
    """Returns the (y, x) coordinates of the Entrance (2)"""
    entrance_coords = np.where(grid == 2)

    if len(entrance_coords[0]) > 0:
        # NumPy returns (row, column) which is (y, x)
        start_y = int(entrance_coords[0][0])
        start_x = int(entrance_coords[1][0])
        # CHANGED: Return (y, x) instead of (x, y)
        return start_y, start_x
    else:
        grid_size = grid.shape[0]
        return grid_size // 2, grid_size // 2


def get_unique_tile(floor_tiles: npt.NDArray[np.int_], used_tiles: set) -> Optional[Tuple[int, int]]:
    """Returns the (y, x) coordinates of a unique floor tile."""
    # floor_tiles are (row, col) which is (y, x)
    for y, x in floor_tiles: 
        if (y, x) not in used_tiles: # Check using (y, x) format
            used_tiles.add((y, x)) # Add using (y, x) format
            return (y, x) # Return as (y, x)
    return None

def generate_entities(dungeon_map: npt.NDArray[np.int_]) -> Tuple[List[Enemy], List[Chest]]:
    """Places enemies and chests randomly on floor tiles (1) in the dungeon map."""
    floor_tiles = np.argwhere(dungeon_map == 1)
    r.shuffle(floor_tiles)

    enemies: List[Enemy] = []
    chests: List[Chest] = []

    # Simple logic: up to 2 enemies and 1 chests
    num_enemies = min(r.randint(1, 3), len(floor_tiles) // 3)
    num_chests = min(1, len(floor_tiles) // 4)

    # Place entities on unique floor tiles
    used_tiles = set()

    # Place enemies
    for _ in range(num_enemies):
        result = get_unique_tile(floor_tiles, used_tiles)
        if result is not None:
            y, x = result
            enemies.append(Enemy(y, x))

    # Place chests
    possible_items = ["Poison Bow", "Sword"]
    for _ in range(num_chests):
        result = get_unique_tile(floor_tiles, used_tiles)
        if result is not None:
            y, x = result
            item = r.choice(possible_items)
            chests.append(Chest(y, x, item))

    return enemies, chests