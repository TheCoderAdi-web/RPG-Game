# Import necessary type hints and numpy
from typing import Dict, Tuple, List
import numpy as np
import numpy.typing as npt

# --- Global Variables for Level Generation ---
GRID_SIZE: int = 14
WALK_STEPS: int = 450
level_size: int = GRID_SIZE # Use the generator's size

# Symbols for map rendering (0:Wall, 1:Floor, 2:Treasure/Exit, 4:Entrance)
MAP_SYMBOLS: Dict[int, str] = {0: '█', 1: ' ', 2: ' ', 4: ' '}

# Classes for each Entity
class Enemy:
    """Class representing an enemy in the game."""

    def __init__(self, x: int, y: int, health: int = 3):
        self.x = x
        self.y = y
        self.health = health

class Player:
    """Class representing the player in the game."""

    def __init__(self, x: int, y: int, health: int = 5, weapon: str = "Sword"):
        self.x = x
        self.y = y
        self.health = health
        self.weapon = weapon

    def move(self, dungeon_map: npt.NDArray[np.int_]) -> str:
        """Move the player based on input, checking for walls and level bounds.
        Returns a string indicating the result of the move.
        """
        direction = input("Move (W/A/S/D). Enter (H) to Heal: ").strip().upper()
        dr, dc = 0, 0

        # Determine change in coordinates (dr: delta row/y, dc: delta column/x)
        if direction == 'W': dr, dc = -1, 0
        elif direction == 'S': dr, dc = 1, 0
        elif direction == 'A': dr, dc = 0, -1
        elif direction == 'D': dr, dc = 0, 1
        elif direction == 'H':
            # Handle healing
            if self.health < 5:
                self.health += 1
                print("You healed 1 health point.")
            else:
                print("Health is already full.")
            input("Press Enter to continue...")
            return "Healed" # Not a positional move
        else:
            print("Invalid input.")
            return "Invalid"

        new_y, new_x = self.y + dr, self.x + dc
        map_height, map_width = dungeon_map.shape

        if 0 <= new_y < map_height and 0 <= new_x < map_width:
            # Check if the new tile is a Wall (0)
            if dungeon_map[new_y, new_x] != 0:
                self.y, self.x = new_y, new_x
                return "Moved"
            else:
                return "Wall"
        else:
            # Hitting the boundary of the map
            return "NextLevel" # Signal for new level generation

class Chest:
    """Class representing a chest in the game."""

    def __init__(self, x: int, y: int, item: str):
        self.x = x
        self.y = y
        self.item = item
        self.opened = False

    def open(self, player: Player) -> None:
        if not self.opened:
            print(f"You found a {self.item}!")
            player.weapon = self.item
            self.opened = True
            input("Press Enter to continue...")
        else:
            print("The chest is empty.")
            input("Press Enter to continue...")
