from typing import Dict, Tuple, List, Optional
import numpy as np
import numpy.typing as npt
import os
import platform

# --- Global Variables for Level Generation ---
GRID_SIZE: int = 25
WALK_STEPS: int = 450
level_size: int = GRID_SIZE

# Symbols for map rendering (0:Wall, 1:Floor, 2:Entrance)
MAP_SYMBOLS: Dict[int, str] = {0: '█', 1: ' ', 2: ' ',}

# Weapon damage dictionary (Base, Crit)
WEAPON_DAMAGE: Dict[str, Tuple[int, int]] = {
    "Sword": (2, 4),
    "Poison Bow": (1, 2),
    "Fists": (1, 2)
}

# Weapon Status Effects dictionary
WEAPON_STATUS_EFFECTS: Dict[str, str] = {
    "Poison Bow": "Poisoned",
    "Sword": "None",
    "Fists": "None"
}

# Outcomes for Player Defend vs Enemy Attack
PLAYER_DEFENCE_OUTCOMES: Dict[int, str] = {
    0: "Enemy attacks! You defended and take no damage!",
    1: "Enemy attacks! You failed to defend. You take 1 damage!",
    2: "Enemy Heals while you defended! No damage taken."
}

ENEMY_DEFENCE_OUTCOMES: Dict[int, str] = {
    0: "Enemy defends and blocks your attack!",
    1: "Enemy's block is broken! You deal damage!",
    2: "Enemy parries your attack and counters! You take 1 damage!"
}

# Function to clear the terminal
def clear_terminal() -> None:
    """Clears the console screen using OS-specific commands."""
    # Check the operating system
    if platform.system() == "Windows":
        os.system('cls')  # Command for Windows
    else:
        # Command for Linux and macOS (POSIX systems)
        os.system('clear')

# Classes for Entities
class Enemy:
    """Class representing an enemy in the game."""

    def __init__(self, x: int, y: int, health: int = 3):
        self.y = y
        self.x = x
        self.health = health
        self.status = "None"
        self.status_duration = 0

class Player:
    """Class representing the player in the game."""

    def __init__(self, y: int, x: int, health: int = 5, weapon: str = "Fists"):
        self.y = y
        self.x = x
        self.health = health
        self.max_health = 5
        self.weapon = weapon

    def move(self, dungeon_map: npt.NDArray[np.int_]) -> str:
        """Move the player based on input, checking for walls and level bounds.
        Returns a string indicating the result of the move.
        """
        direction = input("Move (W/A/S/D). Enter (H) to Heal: ").strip().upper()
        dr, dc = 0, 0

        if direction == 'W': dr, dc = -1, 0
        elif direction == 'S': dr, dc = 1, 0
        elif direction == 'A': dr, dc = 0, -1
        elif direction == 'D': dr, dc = 0, 1
        elif direction == 'H':
            if self.health < self.max_health and self.weapon != "Fists":
                self.health += 1
                print("You healed 1 health point, at the cost of your Weapon.")
                self.weapon = "Fists"  # Reset weapon to fists after healing
            elif self.health >= self.max_health:
                print("Health is already full.")
            else:
                print("You cannot heal without a weapon to sacrafice.")
            input("Press Enter to continue...")
            return "Healed"
        else:
            print("Invalid input.")
            return "Invalid"

        new_y, new_x = self.y + dr, self.x + dc
        map_height, map_width = dungeon_map.shape

        if 0 <= new_y < map_height and 0 <= new_x < map_width:
            if dungeon_map[new_y, new_x] != 0:
                self.y, self.x = new_y, new_x
                return "Moved"
            else:
                return "Wall"
        else:
            return "NextLevel"

class Chest:
    """Class representing a chest in the game."""

    def __init__(self, y: int, x: int, item: str):
        self.y = y
        self.x = x
        self.item = item
        self.opened = False

    def open(self, player: Player) -> None:
        """Opens the chest, giving the player its item."""
        if not self.opened:
            print(f"You found a {self.item}!")
            player.weapon = self.item
            self.opened = True
            input("Press Enter to continue...")
        else:
            print("The chest is empty.")
            input("Press Enter to continue...")

class GameState:
    """Class to hold all current game data for a single session."""

    def __init__(self, player_name: str, player_obj: Player):
        self.name: str = player_name
        self.player: Player = player_obj
        self.enemies: List[Enemy] = []
        self.chests: List[Chest] = []
        self.dungeon_map: npt.NDArray[np.int_] = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
        self.level: int = 0
        self.game_state: str = "next_level_transition" # Start by generating the first level
        self.current_enemy: Optional[Enemy] = None