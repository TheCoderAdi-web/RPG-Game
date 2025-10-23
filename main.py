from typing import List, Tuple, Optional, Callable, Dict
import numpy as np # type: ignore
import numpy.typing as npt # type: ignore
from fight import enemy_encounter
from game_data import Enemy, Player, Chest, MAP_SYMBOLS, GRID_SIZE, WALK_STEPS, GameState, clear_terminal 
from levelgenerator import generate_random_walk_dungeon, find_entrance, generate_entities
from progress_saver import save_game_prompt, load_game_prompt # NEW IMPORT

# --- Game Logic Functions ---

def print_UI(state: GameState) -> None:
    """Print the player UI with name, weapon, and health."""
    clear_terminal()
    print(f"Player: {state.name}")
    print(f"Player Weapon: {state.player.weapon}")
    print(f"Level: {state.level}")
    for _ in range(state.player.health):
        print("♥", end=" ")
    print("\n")

def print_grid(state: GameState) -> None:
    """Print the game grid with player and entities overlayed on the dungeon map."""
    print_UI(state)

    grid_symbols: List[List[str]] = []
    for r in range(state.dungeon_map.shape[0]):
        row_symbols: list[str] = []
        for c in range(state.dungeon_map.shape[1]):
            # Use MAP_SYMBOLS (e.g., 'C' for chests)
            symbol = MAP_SYMBOLS.get(int(state.dungeon_map[r, c]), '?')
            row_symbols.append(symbol)
        grid_symbols.append(row_symbols)

    for enemy in state.enemies:
        if enemy.health > 0:
            grid_symbols[enemy.y][enemy.x] = 'E'

    # Check for chests and place symbol if not opened
    for chest in state.chests:
        if not chest.opened:
            # We use the map value of 3 for chests, but override it here if the player isn't standing on it
            if grid_symbols[chest.y][chest.x] != 'E':
                 grid_symbols[chest.y][chest.x] = 'C'

    # Place player symbol last to ensure visibility
    grid_symbols[state.player.y][state.player.x] = 'P'

    # Print the final grid
    for row in grid_symbols:
        print(' '.join(row))

    # UPDATED: Changed (S) Save to (T) Save/Store
    print("\nCommand: (W/A/S/D) Move, (H) Heal, (T) Save, (Q)uit") 

def handle_player_action(state: GameState, action: str) -> str:
    """Handles non-movement actions like Heal or Save."""
    
    if action == 'H':
        player = state.player
        if player.health < player.max_health and player.weapon != "Fists":
            player.health += 1
            print("You healed 1 health point, at the cost of your Weapon.")
            player.weapon = "Fists"
            return "ActionSuccess"
        elif player.health >= player.max_health:
            print("Health is already full.")
        else:
            print("You cannot heal without a weapon to sacrifice.")
        return "ActionFail"
    
    # NEW: Handle Save Action - now triggered by 'T'
    elif action == 'T':
        save_game_prompt(state)
        return "ActionSuccess"
        
    return "Invalid"

def initialize_game(load: bool = True) -> GameState:
    """
    Handles initial player setup or loads a saved game.
    If 'load' is True, it prompts the user to load a game first.
    """
    
    if load:
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

def update_game_state(state: GameState, action: str) -> None:
    """Handles movement or action, and checks for entity interactions."""
    
    # 1. Handle Movement
    if action in ('W', 'A', 'S', 'D'):
        move_result = state.player.move(action, state.dungeon_map)

        if move_result == "Wall":
            print("Can't move there, it's a wall!")
            input("Press Enter to continue...")
            return

        elif move_result == "NextLevel":
            state.game_state = "next_level_transition"
            return
            
    # 2. Handle Action (Heal or Save)
    # UPDATED: Changed 'S' to 'T' in this check
    elif action in ('H', 'T'):
        action_result = handle_player_action(state, action)
        if action_result in ("ActionSuccess", "ActionFail"):
             # For a Save or Heal action, we return to the playing state's main loop
             return
    
    # 3. Handle Invalid Input
    else:
        print("Invalid command.")
        input("Press Enter to continue...")
        return
    
    # 4. Check Collisions (only after successful movement)
    
    if state.player.health <= 0:
        state.game_state = "game_over"
        return

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
    print_grid(state)
    action: str = input("Command: ").strip().upper()
    
    if action == 'Q':
        state.game_state = "game_over"
        return
        
    update_game_state(state, action)

def handle_next_level_transition(state: GameState):
    transition_to_next_level(state)

def handle_enemy_encounter(state: GameState):
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
                print(f"Error: Unknown game state: {state.game_state}")
                input("Press Enter to continue...")
                state.game_state = "game_over"

        clear_terminal()
        print("Game Over!")
        restart = input("Do you want to play again? (Y/N): ").strip().upper()
        if restart != 'Y':
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    main()
