# Import necessary type hints and numpy
from typing import Dict, Tuple, List
import numpy as np
import numpy.typing as npt

# --- Global Variables for Level Generation ---
GRID_SIZE: int = 25
WALK_STEPS: int = 450
level_size: int = GRID_SIZE # Use the generator's size

# Symbols for map rendering (0:Wall, 1:Floor, 2:Treasure, 4:Entrance)
MAP_SYMBOLS: Dict[int, str] = {0: '█', 1: ' ', 2: '💰', 4: '🏰'}

# Weapon damage dictionary
WEAPON_DAMAGE = {
    "Sword": (2, 4),
    "Poison Bow": (1, 2),
    "Fists": (1, 2)
}

# Weapon Status Effects dictionary
WEAPON_STATUS_EFFECTS = {
    "Poison Bow": "None",
    "Sword": "None",
    "Fists": "None"
}

# Outcomes for Player Defend vs Enemy Attack
PLAYER_DEFENCE_OUTCOMES = {
    0: "Enemy attacks! You defended and take no damage!",
    1: "Enemy attacks! You failed to defend. You take 1 damage!",
    2: "Enemy Heals while you defended! No damage taken."
}

ENEMY_DEFENCE_OUTCOMES = {
    0: "Enemy defends and blocks your attack!",
    1: "Enemy's block is broken! You deal damage!",
    2: "Enemy parries your attack and counters! You take 1 damage!"
}

# Classes for each Entity
class Enemy:
    """Class representing an enemy in the game."""

    def __init__(self, x: int, y: int, health: int = 3):
        self.x = x
        self.y = y
        self.health = health
        self.status = "None"
        self.status_duration = 0

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