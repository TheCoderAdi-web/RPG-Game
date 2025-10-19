# Import necessary modules and classes
from typing import List
from fight import fight, enemy_encounter
# Updated imports for new data structure
from game_data import Enemy, Player, Chest, level_size, MAP_SYMBOLS, GRID_SIZE
from levelgenerator import generate_random_walk_dungeon, find_entrance, generate_entities, WALK_STEPS
import numpy as np
import numpy.typing as npt

def print_UI(player: Player, name: str) -> None:
    """Print the player UI with name, weapon, and health."""
    print("\033c", end="")
    print(f"Player: {name}")
    print(f"Player Weapon: {player.weapon}")
    # Print health hearts
    for _ in range(player.health):
        print("♥", end=" ")
    print("\n")

def print_grid(player: Player, enemies: List[Enemy], chests: List[Chest], dungeon_map: npt.NDArray[np.int_], name: str,) -> None:
    """Print the game grid with player and entities overlayed on the dungeon map."""
    print_UI(player, name)

    # Convert the numpy array map to a list of symbols
    grid_symbols: List[List[str]] = []
    for r in range(dungeon_map.shape[0]):
        row_symbols: list[str] = []
        for c in range(dungeon_map.shape[1]):
            # Start with the map symbol (Wall, Floor, Exit)
            symbol = MAP_SYMBOLS.get(int(dungeon_map[r, c]), '?')
            row_symbols.append(symbol)
        grid_symbols.append(row_symbols)

    # Overlay Entities (E and C must be drawn over the map symbol)
    for enemy in enemies:
        if enemy.health > 0:
            grid_symbols[enemy.y][enemy.x] = 'E'
    for chest in chests:
        if not chest.opened:
            grid_symbols[chest.y][chest.x] = 'C'

    # Overlay Player
    grid_symbols[player.y][player.x] = 'P'

    # Print the resulting grid
    for row in grid_symbols:
        print(' '.join(row))

def print_grid_and_update(player: Player, enemies: List[Enemy], chests: List[Chest], dungeon_map: npt.NDArray[np.int_], name: str) -> str:
    """Print the grid, get player move, and update player position based on input."""
    print_grid(player, enemies, chests, dungeon_map, name)
    # The player.move() is now modified to take the dungeon map
    move_result = player.move(dungeon_map)
    return move_result

def start() -> tuple[Player, List[Enemy], List[Chest], npt.NDArray[np.int_], str, str]:
    """Start a new game session, generating the first level."""
    name: str = input("Enter your name: ")
    # Player starts at (0, 0); coordinates will be set by level generation
    player: Player = Player(0, 0, 5, "Fists")
    game_state: str = "playing"

    # Generate the first dungeon map
    dungeon_map = generate_random_walk_dungeon(GRID_SIZE, WALK_STEPS)
    start_x, start_y = find_entrance(dungeon_map)

    # Place player at the entrance
    player.x, player.y = start_x, start_y

    # Generate enemies and chests on the floor tiles
    enemies, chests = generate_entities(dungeon_map)

    print_grid(player, enemies, chests, dungeon_map, name)

    return player, enemies, chests, dungeon_map, game_state, name

def main() -> None:
    """Main game loop."""
    while True:
        # Start the game and generate the first level
        player, enemies, chests, dungeon_map, game_state, name = start()
        current_enemy = None

        while True:
            # Handle different game states
            if game_state == "playing":
                # print_grid_and_update returns the result of the move
                move_result = print_grid_and_update(player, enemies, chests, dungeon_map, name)

                if move_result == "NextLevel":
                    # Transition triggered by hitting the map boundary
                    print("You feel the boundary push you into a new, strange dungeon...")
                    game_state = "next_level_transition"

                # Check for encounters
                for enemy in enemies:
                    if enemy.health > 0 and (player.x, player.y) == (enemy.x, enemy.y):
                        game_state = "enemy_encounter"
                        current_enemy = enemy
                        break
                for chest in chests:
                    if not chest.opened and (player.x, player.y) == (chest.x, chest.y):
                        chest.open(player)

                if player.health <= 0:
                    game_state = "game_over"

            elif game_state == "next_level_transition":
                # Generate a new level
                dungeon_map = generate_random_walk_dungeon(GRID_SIZE, WALK_STEPS)
                start_x, start_y = find_entrance(dungeon_map)
                player.x, player.y = start_x, start_y
                enemies, chests = generate_entities(dungeon_map)
                game_state = "playing"
                print("\033c", end="")

            elif game_state == "game_over":
                print("\033c", end="")
                print("Game Over!")
                restart = input("Do you want to play again? (Y/N): ").strip().upper()
                if restart == 'Y':
                    break  # Break inner loop to restart game
                else:
                    print("Thanks for playing!")
                    return
            elif game_state == "enemy_encounter":
                print("\033c", end="")
                print(f"You encountered an enemy at ({current_enemy.x}, {current_enemy.y})!")
                game_state, player.health = enemy_encounter(game_state, current_enemy, player)


if __name__ == "__main__":
    main()
