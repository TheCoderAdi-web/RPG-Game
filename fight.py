# Import necessary modules and classes
from typing import Tuple
from random import randint
from game_data import Enemy, Player

def enemy_turn(player_action: str) -> tuple[str, str]:
    """Determine and process the enemy's action. Returns (enemy_action, message)."""
    enemy_actions = {0: 'A', 1: 'D', 2: 'H'}
    enemy_action_decider1 = randint(0, 2)
    enemy_action = enemy_actions[enemy_action_decider1]

    if enemy_action == 'A':
        if player_action == 'D':
            defend_outcomes = {
                0: "Enemy attacks! You defended and take no damage!",
                1: "Enemy attacks! You failed to defend. You take 1 damage!"
            }
            return enemy_action, defend_outcomes[randint(0, 1)]
        return enemy_action, "Enemy attacks! You take 1 damage!"
    elif enemy_action == 'D':
        if player_action == 'A':
            defend_outcomes = {
                0: "Enemy defends and blocks your attack!",
                1: "Enemy's block is broken! You deal damage!",
                2: "Enemy parries your attack and counters! You take 1 damage!"
            }
            return enemy_action, defend_outcomes[randint(0, 2)]
        else:
            return enemy_action, "Enemy defends and blocks your attack!"
    else:
        if player_action == 'A':
            return 'D', "Enemy defends and blocks your attack!"
        return enemy_action, "Enemy heals and regains 1 health."

def fight(health: int, enemy_health: int, weapon: str) -> Tuple[int, bool]:
    """Actual fight sequence. Returns updated health and whether enemy is defeated."""

    print("Battle Start!")
    # Weapon effects dictionary
    weapon_effects = {
        "Sword": lambda: 2,
        "Bow": lambda: 2 if randint(0, 100) != 0 else 0,
        "Fists": lambda: 1
    }

    while health > 0 and enemy_health > 0:
        print("\033c", end="")
        print(f"\nYour Health: {health} | Enemy Health: {enemy_health}")

        # Player's Turn
        action = input("Do you want to (A)ttack or (D)efend? ").strip().upper()
        print("\n")
        if action == 'A':
            print("You attack the enemy!")
            damage = weapon_effects.get(weapon, lambda: 1)()
            if weapon == "Bow" and damage == 0:
                print("Your arrow missed!")
            # Don't apply damage yet; wait for enemy's response
        elif action == 'D':
            print("You defend and brace yourself!")
        else:
            print("Invalid action. You lose your turn!")
            action = ''  # No valid action

        # Enemy's turn
        enemy_action, result = enemy_turn(action)
        print(result)
        input("Press Enter to continue...")

        # Apply effects based on both actions
        if action == 'A' and enemy_action == 'A':
            # Both attack: both take damage
            enemy_health -= damage
            health -= 1
        elif action == 'A':
            if "block is broken" in result:
                enemy_health -= damage
            elif "Enemy defends and blocks" in result:
                pass  # No damage
            elif "parries your attack" in result:
                health -= 1
            elif "You take 1 damage" in result:
                health -= 1
            elif "Enemy heals" in result:
                enemy_health += 1
            else:
                # If enemy did not defend, apply normal damage
                enemy_health -= damage
        elif action == 'D':
            if "You take 1 damage" in result:
                health -= 1
            elif "Enemy heals" in result:
                enemy_health += 1
            # No other effects for defend
        else:
            if "You take 1 damage" in result:
                health -= 1
            elif "Enemy heals" in result:
                enemy_health += 1

        # The enemy has been defeated
        if enemy_health <= 0:
            print("Enemy defeated!")
            return health, True
        if health <= 0:
            print("You were defeated!")
            return 0, False
    return health, enemy_health <= 0

def enemy_encounter(game_state: str, enemy: Enemy, player: Player) -> tuple[str, int]:
    """Handle the enemy encounter state. Returns updated game state and health."""

    print("You encountered an enemy!")
    while True:
        print("\033c", end="")
        action = input("Do you want to (F)ight or (R)un away? ").upper()
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
        elif action == 'R':
            print("You chose to run away!")
            # Running away puts the player back on the map, but the enemy is still there.
            game_state = "playing"
            break
        else:
            print("Invalid action.")
    return game_state, player.health
