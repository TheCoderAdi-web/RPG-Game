# Import necessary modules and classes
from typing import List
from fight import fight, enemy_encounter
from game_data import Enemy, Player, Chest, level_size

def print_UI(player: Player, name: str) -> None:
    """Print the player UI with name, weapon, and health."""
    print("\033c", end="")
    print(f"Player: {name}")
    print(f"Player Weapon: {player.weapon}")
    for i in range(player.health):
        print("♥", end=" ")
    print("\n")

def print_grid(player: Player, enemies: List[Enemy], chests: List[Chest], level_size: int, name: str,) -> None:
    """Print the game grid with player and enemies."""

    print_UI(player, name)
    grid: list[list[str]] = [['.' for _ in range(level_size)] for _ in range(level_size)]
    for enemy in enemies:
        if enemy.health > 0:
            grid[enemy.y][enemy.x] = 'E'
    for chest in chests:
        grid[chest.y][chest.x] = 'C'
    grid[player.y][player.x] = 'P'
    for row in grid:
        print(' '.join(row))

def print_grid_and_update(player: Player, enemies: List[Enemy], chests: List[Chest], level_size: int, name: str) -> None:
    """Print the grid and update player position based on input."""
    print_grid(player, enemies, chests, level_size, name)
    player.move()
    print_grid(player, enemies, chests, level_size, name)

def start() -> tuple[Player, List[Enemy], str, str]:
    """Start a new game session."""
    name: str = input("Enter your name: ")
    player: Player = Player(2, 2, 5, "Fists")
    game_state: str = "playing"

    # Place multiple enemies
    enemies: List[Enemy] = [Enemy(5, 5), Enemy(7, 2), Enemy(3, 8)]
    chests: List[Chest] = [Chest(4, 4, "Bow"), Chest(8, 8, "Sword")]
    print_grid(player, enemies, chests, level_size, name)

    return player, enemies, game_state, name

def main() -> None:
    """Main game loop."""
    while True:
        player, enemies, game_state, name = start()
        # Place multiple enemies and chests for each new game
        enemies: List[Enemy] = [Enemy(5, 5), Enemy(7, 2), Enemy(3, 8), Enemy(1, 6)]
        chests: List[Chest] = [Chest(4, 4, "Bow"), Chest(8, 8, "Sword")]
        print_grid(player, enemies, chests, level_size, name)

        while True:
            # Handle different game states
            if game_state == "playing":
                print_grid_and_update(player, enemies, chests, level_size, name)
                for enemy in enemies:
                    if enemy.health > 0 and (player.x, player.y) == (enemy.x, enemy.y):
                        game_state = "enemy_encounter"
                        current_enemy = enemy
                        break
                for chest in chests:
                    if (player.x, player.y) == (chest.x, chest.y):
                        chest.open(player)

                if player.health <= 0:
                    game_state = "game_over"
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
                print("You encountered an enemy!")
                game_state, player.health = enemy_encounter(game_state, current_enemy, player)


if __name__ == "__main__":
    main()