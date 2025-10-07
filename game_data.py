# Global Variables
level_size: int = 10

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

    def move(self) -> None:
        direction = input("Move (W/A/S/D). Enter (H) to Heal: ").strip().upper()
        if direction == 'W' and self.y > 0:
            self.y -= 1
        elif direction == 'S' and self.y < level_size - 1:
            self.y += 1
        elif direction == 'A' and self.x > 0:
            self.x -= 1
        elif direction == 'D' and self.x < level_size - 1:
            self.x += 1
        elif direction == 'H':
            if self.health < 5:
                self.health += 1
                print("You healed 1 health point.")
            else:
                print("Health is already full.")
            input("Press Enter to continue...")
        else:
            print("Invalid move or out of bounds.")

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
        else:
            print("The chest is empty.")
            input("Press Enter to continue...")