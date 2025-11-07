from typing import List, Tuple, Optional, Callable, Dict
import numpy as np # type: ignore
import numpy.typing as npt # type: ignore
from scripts.fight import enemy_encounter
# Ensure all necessary classes and constants are imported from game_data
from game_data import Enemy, Player, Chest, MAP_SYMBOLS, GRID_SIZE, WALK_STEPS, GameState, clear_terminal 
# These functions are required by initialize_game and handle_player_action
from progress_saver import save_game_prompt, load_game_prompt 
from levelgenerator import generate_random_walk_dungeon, find_entrance, generate_entities

# --- Game Logic Functions ---

def print_UI(state: GameState) -> None:
    """Print the player UI with name, weapon, status, health, and enemy count."""
    clear_terminal()
    print(f"Player: {state.name}")
    print(f"Player Weapon: {state.player.weapon}")
    print(f"Level: {state.level}")
    
    # Display Player Status if active
    if state.player.status != "None":
        print(f"Status: {state.player.status} ({state.player.status_duration} turns)")

    # Display health hearts
    print("Health:", end=" ")
    for _ in range(state.player.health):
        print("♥", end=" ")
    print(f" ({state.player.health}/{state.player.max_health})")

    # Display remaining enemies count (Crucial for exit logic visibility)
    enemies_remaining = [e for e in state.enemies if e.health > 0]
    print(f"Enemies remaining: {len(enemies_remaining)}")
    print("-" * 25)

def print_grid(state: GameState) -> None:
    """Print the game grid with player and entities overlayed on the dungeon map."""
    print_UI(state)

    grid_symbols: List[List[str]] = []
    for r in range(state.dungeon_map.shape[0]):
        row_symbols: list[str] = []
        for c in range(state.dungeon_map.shape[1]):
            # Use MAP_SYMBOLS (0:Wall, 1:Floor, 2:Entrance, 3:Chest, 4:Exit)
            # Entrance (2) is rendered as floor ' ' and Exit (4) as '>'
            symbol = MAP_SYMBOLS.get(int(state.dungeon_map[r, c]), '?') 
            row_symbols.append(symbol)
        grid_symbols.append(row_symbols)

    # Place Enemy symbols (E)
    for enemy in state.enemies:
        if enemy.health > 0:
            grid_symbols[enemy.y][enemy.x] = 'E'

    # Check for chests and place symbol (C) if not opened and no enemy is on the tile
    for chest in state.chests:
        if not chest.opened:
            if grid_symbols[chest.y][chest.x] not in ['E', 'P']:
                 grid_symbols[chest.y][chest.x] = 'C'

    # Place player symbol last to ensure visibility
    grid_symbols[state.player.y][state.player.x] = 'P'

    # Print the final grid
    for row in grid_symbols:
        print(' '.join(row))

    print("\nCommand: (W/A/S/D) Move, (H) Heal, (T) Save, (Q)uit") 

def handle_player_action(state: GameState, action: str) -> str:
    """Handles non-movement actions like Heal or Save."""
    
    if action == 'H':
        player = state.player
        if player.status != "None":
            print(f"You cannot focus to heal while {player.status}!")
        elif player.health < player.max_health and player.weapon != "Fists":
            player.health += 1
            print("You healed 1 health point, at the cost of your Weapon.")
            player.weapon = "Fists"
            return "ActionSuccess"
        elif player.health >= player.max_health:
            print("Health is already full.")
        else:
            print("You cannot heal without a weapon to sacrifice.")
        
        # All healing attempts result in a turn, even if failed
        return "ActionSuccess" 
    
    # Handle Save Action - triggered by 'T'
    elif action == 'T':
        # Relies on the external save_game_prompt function
        save_game_prompt(state) 
        return "ActionSuccess"
        
    return "Invalid"

def initialize_game(load: bool = True) -> GameState:
    """Handles initial player setup or loads a saved game."""
    
    if load:
        # Relies on the external load_game_prompt function
        loaded_state = load_game_prompt() 
        if loaded_state:
            return loaded_state
            
    name: str = input("Enter your name: ")
    player: Player = Player(0, 0) 
    
    state = GameState(name, player)
    return state

def transition_to_next_level(state: GameState) -> None:
    """Generates a new level, places the player, and updates the GameState object."""
    dungeon_map = generate_random_walk_dungeon(GRID_SIZE, WALK_STEPS)
    start_y, start_x = find_entrance(dungeon_map)
    state.player.y, state.player.x = start_y, start_x
    
    state.enemies, state.chests = generate_entities(dungeon_map) 

    state.dungeon_map = dungeon_map
    state.level += 1
    state.game_state = "playing"
    clear_terminal()
    print(f"*** Level {state.level} Reached! ***")
    input("Press Enter to continue...")

def apply_status_effects(state: GameState) -> None:
    """Applies and decays status effects at the start of the player's turn."""
    player = state.player
    if player.status == "Poisoned":
        player.health -= 1
        player.status_duration -= 1
        print_UI(state) # Re-print UI to show damage
        print(f"The poison bites at you, dealing 1 damage! {player.health} health remaining.")
        if player.status_duration <= 0:
            player.status = "None"
            player.status_duration = 0
            print("The poison wears off.")
        input("Press Enter to continue...")
    
    # Check for death after status damage
    if player.health <= 0:
        state.game_state = "game_over"

def update_game_state(state: GameState, action: str) -> None:
    """Handles movement or action, and checks for entity interactions."""
    
    # 1. Handle Movement
    if action in ('W', 'A', 'S', 'D'):
        # move() method in Player determines if player hits a Wall, Moves, or hits ExitTile
        move_result = state.player.move(action, state.dungeon_map) 

        if move_result == "Wall":
            return

        # VITAL LOGIC: Check for the Exit Tile and enemy clearance
        elif move_result == "ExitTile":
            # Check if all enemies are defeated (health > 0)
            enemies_remaining = [e for e in state.enemies if e.health > 0]
            
            if not enemies_remaining:
                # All enemies cleared, transition immediately
                print("You found the exit! All enemies defeated. Moving to the next level...")
                state.game_state = "next_level_transition"
                return
            else:
                # Player is on the exit tile, but transition is blocked
                print(f"The exit is here (>) but you must defeat {len(enemies_remaining)} enemies before proceeding!")
                # Move back to prevent continuous attempts on the same turn
                # The player class handles moving the player to the exit tile. 
                # We do not revert the player position, just block the state transition.
                input("Press Enter to continue...")
                return 
        
    # 2. Handle Action (Heal or Save)
    elif action in ('H', 'T'):
        handle_player_action(state, action)
        return
    
    # 3. Handle Quit Input
    elif action == 'Q':
        save = input("Would you like to save your game before quitting? (Y/N): ")
        if save.strip().upper() == 'N':
            state.game_state = "game_over"
            return
        elif save.strip().upper() == 'Y':
            save_game_prompt(state)
        else:
            save = input("Invalid Input. Would you like to save your game before quitting? (Y/N): ")

    
    # 4. Handle Invalid Input
    elif action != "": 
        print("Invalid command.")
        input("Press Enter to continue...")
        return
    
    # 5. Check Collisions (only after successful movement or action)
    
    # Check for enemy encounter
    for enemy in state.enemies:
        if enemy.health > 0 and (state.player.y, state.player.x) == (enemy.y, enemy.x):
            state.game_state = "enemy_encounter"
            state.current_enemy = enemy
            return

    # Check for chest interaction
    for chest in state.chests:
        if not chest.opened and (state.player.y, state.player.x) == (chest.y, chest.x):
            chest.open(state.player)
            return

def handle_playing(state: GameState):
    """Handles the main 'playing' input loop."""
    
    # 0. Apply status effects at the start of the turn
    apply_status_effects(state)
    if state.game_state == "game_over":
        return
        
    print_grid(state)
    action: str = input("Command: ").strip().upper()
        
    update_game_state(state, action)

def handle_next_level_transition(state: GameState):
    """Handles the level transition state."""
    transition_to_next_level(state)

def handle_enemy_encounter(state: GameState):
    """Handles the enemy encounter state."""
    if state.current_enemy:
        clear_terminal()
        print(f"You encountered an enemy at ({state.current_enemy.y}, {state.current_enemy.x})!")
                    
        # enemy_encounter returns (new_game_state, player_health)
        new_state, player_health = enemy_encounter(state.game_state, state.current_enemy, state.player)
        
        state.game_state = new_state
        state.player.health = player_health

        if state.current_enemy.health <= 0:
            state.current_enemy.health = 0
                    
        state.current_enemy = None
    else:
        state.game_state = "playing"

# --- STATE MACHINE DICTIONARY ---
# Maps game state names (strings) to their handler functions
STATE_HANDLERS: Dict[str, Callable[[GameState], None]] = {
    'next_level_transition': handle_next_level_transition,
    'playing': handle_playing,
    'enemy_encounter': handle_enemy_encounter
}

def main() -> None:
    """Main game loop for continuous sessions, handling setup, transitions, and state changes."""

    while True:
        # Load Game Prompt is run before initialization.
        state = initialize_game(load=True)

        while state.game_state != "game_over":
            handler = STATE_HANDLERS.get(state.game_state)
            
            if handler:
                handler(state)
            else:
                # Fallback for an unknown state, though unlikely
                print(f"Error: Unknown game state: {state.game_state}")
                input("Press Enter to continue...")
                state.game_state = "game_over"

        # Case for Game Over state
        clear_terminal()
        print("Game Over!")
        restart = input("Do you want to play again? (Y/N): ").strip().upper()
        if restart != 'Y':
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    main()
