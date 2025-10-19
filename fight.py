# Import necessary modules and classes
from typing import Tuple
from random import randint
from game_data import Enemy, Player

# Weapon effects dictionary
WEAPON_EFFECTS = {
    "Sword": lambda: 2,
    "Poison Bow": lambda: 1 if randint(0, 50) != 0 else 0,
    "Fists": lambda: 1
}

WEAPON_EFFECTS["Sword"] = WEAPON_EFFECTS["Sword"] if randint(0, 100) != 0 else lambda: 4 # Critical Hit for Sword
WEAPON_EFFECTS["Fists"] = WEAPON_EFFECTS["Fists"] if randint(0, 100) != 0 else lambda: 3 # Critical Hit for Fists
WEAPON_EFFECTS["Poison Bow"] = WEAPON_EFFECTS["Poison Bow"] if randint(0, 100) != 0 else lambda: 2 # Critical Hit for Poison Bow

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

def enemy_turn(player_action: str) -> tuple[str, str]:
    """Determine and process the enemy's action. Returns (enemy_action, message)."""

    enemy_actions = {0: 'A', 1: 'D', 2: 'H'}
    enemy_action_decider1 = randint(0, 2)
    enemy_action = enemy_actions[enemy_action_decider1]

    if enemy_action == 'A':
        if player_action == 'D':
            return enemy_action, PLAYER_DEFENCE_OUTCOMES[randint(0, 1)]
        return enemy_action, "Enemy attacks! You take 1 damage!"
    elif enemy_action == 'D':
        if player_action == 'A':
            return enemy_action, ENEMY_DEFENCE_OUTCOMES[randint(0, 3)]
        else:
            return enemy_action, "Enemy defends and blocks your attack!"
    else:
        return enemy_action, "Enemy heals and regains 1 health." if randint(0, 1) == 0 else "Enemy Awaits your move."

def fight(health: int, enemy_health: int, weapon: str) -> Tuple[int, bool]:
    """Actual fight sequence. Returns updated health and whether enemy is defeated."""

    damage: int = 0 # Initialize damage before the loop

    while health > 0 and enemy_health > 0:
        print("\033c", end="")
        print(f"\nYour Health: {health} | Enemy Health: {enemy_health}")

        # Player's Turn
        action: str = input("Do you want to (A)ttack or (D)efend? ").strip().upper()
        print("\n")
        
        # Reset damage calculation for the turn
        damage = 0 
        
        if action == 'A':
            print("You attack the enemy!")
            damage = WEAPON_EFFECTS.get(weapon, lambda: 1)()
            # Check if the Arrow Misses, when Shooting with the "Poison Bow"
            if weapon == "Poison Bow" and damage == 0:
                print("Your arrow missed!")
        elif action == 'D':
            print("You defend and brace yourself!")
        else:
            print("Invalid action. You lose your turn!")
            action = ''

        # Enemy's turn
        enemy_action, result = enemy_turn(action)
        print(result)
        input("Press Enter to continue...")

        # Apply effects based on both actions
        if enemy_action == 'H':
            if "Enemy heals" in result:
                enemy_health += 1

        elif enemy_action == 'A':
            if action == 'D':
                if "failed to defend" in result:
                    health -= 1
            elif action == 'A':
                health -= 1
                enemy_health -= damage
            else:
                health -= 1
        
        elif enemy_action == 'D':
            if action == 'A':
                # Player attacks a defending enemy (requires string checks)
                if "block is broken" in result:
                    enemy_health -= damage
                elif "parries your attack" in result:
                    health -= 1

        # The enemy has been defeated
        if enemy_health <= 0:
            print("Enemy defeated!")
            return health, True
        # The player has been defeated
        if health <= 0:
            print("You were defeated!")
            return 0, False
        
    return health, enemy_health <= 0

def enemy_encounter(game_state: str, enemy: Enemy, player: Player) -> tuple[str, int]:
    """Handle the enemy encounter state. Returns updated game state and health."""

    # Initialize encounter
    print("You encountered an enemy!")

    while True:

        # Choose to Fight or Run
        print("\033c", end="")
        action = input("Do you want to (F)ight or (R)un away? ").upper()

        # Player chooses to fight
        if action == 'F':
            print("You chose to fight!")
            player.health, enemy_defeated = fight(player.health, enemy.health, player.weapon)
            enemy.health = 0 if enemy_defeated else enemy.health
            if player.health <= 0:
                game_state = "game_over"
            elif enemy_defeated:
                print("You defeated the enemy!")
                game_state = "playing"
            break

        # Player chooses to run away
        elif action == 'R':
            print("You chose to run away!")
            game_state = "playing"
            break

        # Handle Invalid Inputs
        else:
            print("Invalid action.")
    return game_state, player.health
