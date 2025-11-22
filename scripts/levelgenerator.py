import numpy as np # type: ignore
import random as r

from typing import Dict, Tuple, List, Literal, Optional
import numpy.typing as npt # type: ignore
# Import necessary entities and constants from game_data
from game_data import Enemy, Chest, level_size, GRID_SIZE, WALK_STEPS

def generate_random_walk_dungeon(grid_size: int, steps: int) -> npt.NDArray[np.int_]:
    """Generates a dungeon map using a random walk algorithm.

    Map key: 0=Wall (█), 1=Floor, 2=Entrance, 4=Exit (>)
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
            grid[row, col] = 1 # Mark the current position as a floor tile

    # 1. Place the Exit tile (4) on a random floor space (1)
    floor_tiles = np.argwhere(grid == 1)
    if floor_tiles.size > 0:
        # Choose a random floor tile for the exit
        exit_index = r.randint(0, len(floor_tiles) - 1)
        exit_y, exit_x = floor_tiles[exit_index]
        grid[exit_y, exit_x] = 4 # 4 represents the exit tile '>'
        
    # 2. Set the entrance tile (2) where the walk started
    grid[grid_size // 2, grid_size // 2] = 2 

    return grid

def find_entrance(dungeon_map: npt.NDArray[np.int_]) -> Tuple[int, int]:
    """Finds the coordinates (y, x) of the entrance tile (2)."""
    # np.argwhere returns a list of (row, col) tuples
    entrance_coords = np.argwhere(dungeon_map == 2)
    if entrance_coords.size > 0:
        return tuple(entrance_coords[0]) # Returns the first (y, x) found
    # Fallback to center if entrance not found
    grid_size = dungeon_map.shape[0]
    return grid_size // 2, grid_size // 2

def get_unique_tile(floor_tiles: npt.NDArray[np.int_], used_tiles: set) -> Optional[Tuple[int, int]]:
    """Returns the (y, x) coordinates of a unique floor tile, avoiding tiles already used for entities."""
    # floor_tiles are (row, col) which is (y, x)
    # We must also ensure we don't place entities on the Exit tile (4)
    for y, x in floor_tiles: 
        if (y, x) not in used_tiles: # Check using (y, x) format
            used_tiles.add((y, x)) # Add using (y, x) format
            return (y, x) # Return as (y, x)
    return None

def generate_entities(dungeon_map: npt.NDArray[np.int_]) -> Tuple[List[Enemy], List[Chest]]:
    """Places enemies and chests randomly on valid floor tiles (1) in the dungeon map, avoiding Exits (4)."""
    
    # Only consider floor tiles (1) for entity placement
    # We explicitly exclude tile 4 (Exit) since generate_random_walk_dungeon sets it
    valid_tiles = np.argwhere(dungeon_map == 1) 
    r.shuffle(valid_tiles)

    enemies: List[Enemy] = []
    chests: List[Chest] = []

    # Simple logic: up to 3 enemies and 1 chest (based on available tiles)
    num_enemies = min(r.randint(1, 3), len(valid_tiles) // 3)
    num_chests = min(1, len(valid_tiles) // 4)

    # Place entities on unique floor tiles
    used_tiles = set()

    # Place enemies
    for _ in range(num_enemies):
        result = get_unique_tile(valid_tiles, used_tiles)
        if result is not None:
            y, x = result
            # Enemy health scales slightly with level, assuming level is > 0
            enemies.append(Enemy(y, x, health=r.randint(2, 3)))

    # Place chests
    for _ in range(num_chests):
        result = get_unique_tile(valid_tiles, used_tiles)
        if result is not None:
            y, x = result
            chests.append(Chest(y, x, item=r.choice(["Sword", "Poison Bow", "Iron Armour"])))
            
    return enemies, chests
