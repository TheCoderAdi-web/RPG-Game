import numpy as np # type: ignore
import random as r

from typing import Dict, Tuple, List, Literal, Optional
import numpy.typing as npt # type: ignore
from game_data import Enemy, Chest, level_size, GRID_SIZE, WALK_STEPS

def generate_random_walk_dungeon(grid_size: int, steps: int) -> npt.NDArray[np.int_]:
    """Generates a dungeon map using a random walk algorithm.

    Map key: 0=Wall (█), 1=Floor, 2=Entrance, 3=Chest
    The map is an N x N numpy array where N=grid_size.
    """
    grid: npt.NDArray[np.int_] = np.zeros((grid_size, grid_size), dtype=int)

    # (dr, dc) moves: Up, Down, Left, Right
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

        # Keep the walker within bounds
        if 0 <= new_row < grid_size and 0 <= new_col < grid_size:
            row, col = new_row, new_col
            grid[row, col] = 1 # Carve out a floor tile

    # Mark the entrance (player start) on the central tile
    grid[grid_size // 2, grid_size // 2] = 2
    return grid

def find_entrance(dungeon_map: npt.NDArray[np.int_]) -> Tuple[int, int]:
    """Finds the entrance tile (2) and returns its (y, x) coordinates."""
    # np.argwhere returns a list of (row, col) tuples for the value 2
    entrance_coords = np.argwhere(dungeon_map == 2)
    if entrance_coords.size > 0:
        # Returns the first (y, x) pair found
        return entrance_coords[0][0], entrance_coords[0][1]
    
    # Fallback to center if entrance tile is somehow missing
    grid_size = dungeon_map.shape[0]
    return grid_size // 2, grid_size // 2

def generate_entities(dungeon_map: npt.NDArray[np.int_]) -> Tuple[List[Enemy], List[Chest]]:
    """Places enemies and chests randomly on floor tiles (1) in the dungeon map.
       Uses the efficient .pop() method on a shuffled list of floor tiles."""
       
    # Find all floor tiles (value 1). This returns a NumPy array of (y, x) coordinates.
    floor_tiles_array = np.argwhere(dungeon_map == 1)
    
    # Convert to a standard Python list of tuples and shuffle it for random placement
    floor_tiles_list = [tuple(tile) for tile in floor_tiles_array]
    r.shuffle(floor_tiles_list)

    enemies: List[Enemy] = []
    chests: List[Chest] = []

    possible_items = ["Sword", "Poison Bow"]

    # Simple logic: up to 2 enemies and 1 chests
    num_enemies = min(r.randint(1, 3), len(floor_tiles_list) // 3)
    num_chests = min(1, len(floor_tiles_list) // 4)

    # Place enemies using .pop()
    for _ in range(num_enemies):
        if not floor_tiles_list: break
        y, x = floor_tiles_list.pop() # Gets a unique (y, x) tile and removes it
        enemies.append(Enemy(y, x))

    # Place chests using .pop()
    for _ in range(num_chests):
        if not floor_tiles_list: break
        y, x = floor_tiles_list.pop() # Gets a unique (y, x) tile and removes it
        item = r.choice(possible_items)
        chests.append(Chest(y, x, item))
        dungeon_map[y, x] = 3 # Mark chest location on the map

    return enemies, chests