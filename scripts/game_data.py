from typing import Dict, Tuple, List, Optional
import numpy as np # type: ignore
import numpy.typing as npt# type: ignore
import os
import platform
import pickle # New import for saving/loading

# --- Global Variables for Level Generation ---
GRID_SIZE: int = 25
WALK_STEPS: int = 450
level_size: int = GRID_SIZE

# Symbols for map rendering (0:Wall, 1:Floor, 2:Entrance, 3:Chest, 4:Exit)
MAP_SYMBOLS: Dict[int, str] = {0: '█', 1: ' ', 2: ' ', 3: 'C', 4: '>'} # ADDED '4' FOR EXIT

# Weapon damage dictiona                ry (Base, Crit)
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

# Outcome Codes (Used for robust combat logic)
class OutcomeCodes:
    PLAYER_DEFEND_SUCCESS = "P_DEF_OK"
    PLAYER_DEFEND_FAIL = "P_DEF_FAIL"
    ENEMY_BLOCK_OK = "E_BLOCK_OK"
    ENEMY_BLOCK_BROKEN = "E_BLOCK_BROKEN"
    ENEMY_PARRY = "E_PARRY"
    STALEMATE = "STALEMATE"

# Outcomes for Player Defend vs Enemy Attack
PLAYER_DEFENCE_OUTCOMES_MAP: Dict[int, Tuple[str, str]] = {
    0: (OutcomeCodes.PLAYER_DEFEND_SUCCESS, "Enemy attacks! You defended and take no damage!"),
    1: (OutcomeCodes.PLAYER_DEFEND_FAIL, "Enemy attacks! You failed to defend. You take 1 damage!"),
    2: (OutcomeCodes.PLAYER_DEFEND_SUCCESS, "Enemy Heals while you defended! No damage taken.")
}

ENEMY_DEFENCE_OUTCOMES_MAP: Dict[int, Tuple[str, str]] = {
    0: (OutcomeCodes.ENEMY_BLOCK_OK, "Enemy defends and blocks your attack!"),
    1: (OutcomeCodes.ENEMY_BLOCK_BROKEN, "Enemy's block is broken! You deal damage!"),
    2: (OutcomeCodes.ENEMY_PARRY, "Enemy parries! You take 1 damage.")
}


def clear_terminal() -> None:
    """Clears the terminal screen."""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# --- Entity Classes ---

class Enemy:
    """Class representing an enemy."""
    # Added __slots__ for faster object access and to help with pickling
    __slots__ = ['x', 'y', 'health', 'max_health', 'status', 'status_duration'] 

    def __init__(self, y: int, x: int, health: int):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = health
        self.status = "None"
        self.status_duration = 0

class Player:
    """Class representing the player."""
    # Added __slots__ for faster object access and to help with pickling
    __slots__ = ['x', 'y', 'health', 'max_health', 'gear', 'status', 'status_duration'] 

    def __init__(self, y: int, x: int) -> None:
        self.x: int = x
        self.y: int = y
        self.health: int = 5
        self.max_health: int = 5
        self.gear: str = "Fists"
        self.status: str = "None"
        self.status_duration: int = 0
    
    def move(self, direction: str, dungeon_map: npt.NDArray[np.int_]) -> str:
        """Move the player based on input and map boundaries."""
        new_y, new_x = self.y, self.x

        if direction == 'W': new_y -= 1
        elif direction == 'S': new_y += 1
        elif direction == 'A': new_x -= 1
        elif direction == 'D': new_x += 1

        map_height, map_width = dungeon_map.shape

        if 0 <= new_y < map_height and 0 <= new_x < map_width:
            target_tile = dungeon_map[new_y, new_x]
            
            if target_tile == 0:
                return "Wall"
            
            self.y, self.x = new_y, new_x
            
            # Check for the exit tile (value 4)
            if target_tile == 4:
                return "ExitTile" # Custom return for the exit tile
            
            return "Moved"

        else:
            # If attempting to move outside the current map boundaries, it's a wall.
            return "Wall"

class Chest:
    """Class representing a chest in the game."""
    # Added __slots__ for faster object access and to help with pickling
    __slots__ = ['x', 'y', 'item', 'opened'] 

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
        self.game_state: str = "next_level_transition" # Start at transition to generate Lvl 1
        self.current_enemy: Optional[Enemy] = None # Enemy in current fight

    def save_to_file(self, filename: str = 'savegame.dat') -> None:
        """Saves the entire GameState object using pickle."""
        try:
            with open(filename, 'wb') as f:
                pickle.dump(self, f)
            print(f"\nGame successfully saved to {filename}!")
        except Exception as e:
            print(f"\nERROR: Could not save game: {e}")

    @staticmethod
    def load_from_file(filename: str = 'savegame.dat') -> Optional['GameState']:
        """Loads a GameState object from a file using pickle."""
        try:
            with open(filename, 'rb') as f:
                state = pickle.load(f)
            print(f"\nGame successfully loaded from {filename}!")
            return state
        except FileNotFoundError:
            print("\nNo save file found. Starting new game.")
            return None
        except Exception as e:
            print(f"\nERROR: Could not load game: {e}. Starting new game.")
            return None
