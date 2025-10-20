from typing import List, Tuple, Optional
import numpy as np
import numpy.typing as npt
from fight import enemy_encounter
from game_data import Enemy, Player, Chest, MAP_SYMBOLS, GRID_SIZE, WALK_STEPS, GameState
from levelgenerator import generate_random_walk_dungeon, find_entrance, generate_entities

def print_UI(state: GameState) -> None:
    """Print the player UI with name, weapon, and health."""
    print("\033c", end="")
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
            symbol = MAP_SYMBOLS.get(int(state.dungeon_map[r, c]), '?')
            row_symbols.append(symbol)
        grid_symbols.append(row_symbols)

    for enemy in state.enemies:
        if enemy.health > 0:
            grid_symbols[enemy.y][enemy.x] = 'E'
    for chest in state.chests:
        if not chest.opened:
            grid_symbols[chest.y][chest.x] = MAP_SYMBOLS[2]

    grid_symbols[state.player.y][state.player.x] = 'P'

    for row in grid_symbols:
        print(' '.join(row))

def print_grid_and_update(state: GameState) -> str:
    """Print the grid, get player move, and update player position based on input."""
    print_grid(state)
    move_result = state.player.move(state.dungeon_map)
    return move_result

def initialize_game() -> GameState:
    """Handles initial player setup and returns the initial GameState object."""
    name: str = input("Enter your name: ")
    player: Player = Player(0, 0)
    return GameState(name, player)

def transition_to_next_level(state: GameState) -> None:
    """Generates a new level, places the player, and updates the GameState object."""
    dungeon_map = generate_random_walk_dungeon(GRID_SIZE, WALK_STEPS)
    start_x, start_y = find_entrance(dungeon_map)
    state.player.x, state.player.y = start_x, start_y
    state.enemies, state.chests = generate_entities(dungeon_map)
    state.dungeon_map = dungeon_map
    state.level += 1
    state.game_state = "playing"
    print("\033c", end="")

def update_game_state(state: GameState) -> None:
    """Handles player movement, checks for entity interactions, and updates the GameState."""
    
    move_result = print_grid_and_update(state)
    state.current_enemy = None

    if move_result == "NextLevel":
        state.game_state = "next_level_transition"
        return

    for enemy in state.enemies:
        if enemy.health > 0 and (state.player.x, state.player.y) == (enemy.x, enemy.y):
            state.game_state = "enemy_encounter"
            state.current_enemy = enemy
            return

    for chest in state.chests:
        if not chest.opened and (state.player.x, state.player.y) == (chest.x, chest.y):
            chest.open(state.player)

    if state.player.health <= 0:
        state.game_state = "game_over"


def main() -> None:
    """Main game loop for continuous sessions, handling setup, transitions, and state changes."""

    while True:
        state = initialize_game()

        while state.game_state != "game_over":
            
            if state.game_state == "playing":
                update_game_state(state)

            elif state.game_state == "next_level_transition":
                transition_to_next_level(state)

            elif state.game_state == "enemy_encounter":
                if state.current_enemy:
                    print("\033c", end="")
                    print(f"You encountered an enemy at ({state.current_enemy.x}, {state.current_enemy.y})!")
                    
                    # enemy_encounter returns (new_game_state, player_health)
                    new_state, player_health = enemy_encounter(state.game_state, state.current_enemy, state.player)
                    
                    state.game_state = new_state
                    state.player.health = player_health

                    if state.game_state == "playing" and state.current_enemy.health <= 0:
                        state.current_enemy.health = 0
                    
                    state.current_enemy = None

        print("\033c", end="")
        print("Game Over!")
        restart = input("Do you want to play again? (Y/N): ").strip().upper()
        if restart != 'Y':
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    main()