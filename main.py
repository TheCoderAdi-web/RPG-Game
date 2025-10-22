from typing import List, Tuple, Optional, Callable, Dict
import numpy as np # type: ignore
import numpy.typing as npt # type: ignore
from fight import enemy_encounter
from game_data import Enemy, Player, Chest, MAP_SYMBOLS, GRID_SIZE, WALK_STEPS, GameState, clear_terminal 
from levelgenerator import generate_random_walk_dungeon, find_entrance, generate_entities

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

    # Place player symbol last to ensure visibility
    grid_symbols[state.player.y][state.player.x] = 'P'

    # Print the final grid
    for row in grid_symbols:
        print(' '.join(row))

    print("\nCommand: (W/A/S/D) Move, (H) Heal, (Q)uit")

def handle_player_action(state: GameState, action: str) -> str:
    """Handles non-movement actions like Heal."""
    
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
        
    return "Invalid"

def initialize_game() -> GameState:
    """Handles initial player setup and returns the initial GameState object."""
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

        if move_result == "NextLevel":
            state.game_state = "next_level_transition"
            return
            
    # 2. Handle Action (Heal)
    elif action in ('H'):
        action_result = handle_player_action(state, action)
        if action_result in ("ActionSuccess", "ActionFail"):
             input("Press Enter to continue...")
             return
    
    # 3. Handle Invalid Input
    else:
        print("Invalid command.")
        input("Press Enter to continue...")
        return
    
    # 4. Check Collisions
    
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
        
    player_pos_tile = state.dungeon_map[state.player.y, state.player.x]
    if player_pos_tile == 4:  # 4 is our stairs tile
        
        # Check if any enemies are still alive
        any_enemies_alive = any(enemy.health > 0 for enemy in state.enemies)

        if any_enemies_alive:
            # Enemies are alive: print a message and "bump" the player back
            print("The stairs are blocked by an unseen force...")
            print("You must defeat all enemies on this level to proceed!")
            
            # Revert player's position to their last tile
            state.player.y = state.player.last_y
            state.player.x = state.player.last_x
            
            input("Press Enter to continue...")
        else:
            # All enemies are dead: proceed to the next level
            print("All enemies are defeated! You descend the stairs...")
            input("Press Enter to continue...")
            state.game_state = "next_level_transition"

        return

def handle_playing(state: GameState):
    """Handles the main 'playing' Game State loop."""
    print_grid(state)
    action: str = input("Command: ").strip().upper()
    
    if action == 'Q':
        state.game_state = "game_over"
        return
        
    update_game_state(state, action)

def handle_next_level_transition(state: GameState):
    """Handle the Next Level Transition Game State"""
    transition_to_next_level(state)

def handle_enemy_encounter(state: GameState):
    """Handle the Enemy Encounter Game State"""
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

def print_instructions():
    """Instructions on How to Play the Game, Before Starting"""
    print("How To Play:")
    print("P = Player, E = Enemy, C = Chest, > = Stairs")
    print("To move, press the keys W/A/S/D to go in Up, Left, Down, and Right Directions Respectively.")
    print("On each level, you must defeat all enemies to progress to the next level by moving into the Stairs tile.")
    input("To Continue, Press Enter")

# --- STATE MACHINE DICTIONARY ---
# Maps game state names (strings) to their handler functions
STATE_HANDLERS: Dict[str, Callable[[GameState], None]] = {
    'next_level_transition': handle_next_level_transition,
    'playing': handle_playing,
    'enemy_encounter': handle_enemy_encounter
}

def main() -> None:
    """Main game loop for continuous sessions, handling setup, transitions, and state changes."""

    print_instructions()
    
    while True:
        state = initialize_game()

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
