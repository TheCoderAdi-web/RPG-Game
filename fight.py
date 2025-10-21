# Import necessary modules and classes
from typing import Tuple
from random import randint
from game_data import Enemy, Player, WEAPON_DAMAGE, WEAPON_STATUS_EFFECTS, PLAYER_DEFENCE_OUTCOMES, ENEMY_DEFENCE_OUTCOMES, clear_terminal

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
            return enemy_action, ENEMY_DEFENCE_OUTCOMES[randint(0, 2)]
        else:
            return enemy_action, "Both you and the enemy are defending. A stalemate occurs."
    elif enemy_action == 'H':
        return enemy_action, "Enemy heals and regains 1 health."
    else:
        return enemy_action, "does nothing." # Impossible, but needed for type checking

def handle_turn_outcomes(enemy_action: str, action: str, health: int, enemy_health: int, damage: int, result: str) -> Tuple[int, int]:
    """Handles the turn outcomes and returns the updated healths."""
    
    # If Enemy Heals
    if enemy_action == 'H':
        if action == 'D':
            enemy_health += 1
        elif action == 'A':
            # Enemy's heal is interrupted by attack, damage is applied in fight()
            enemy_health -= damage

    # If Enemy Attacks and Player Defends or Attacks
    elif enemy_action == 'A':
        if action == 'D':
            if "failed to defend" in result:
                    health -= 1
            else:
                pass  # No damage taken when successfully defending
        elif action == 'A':
            health -= 1
            enemy_health -= damage
        else:
            health -= 1
        
    # If Enemy Defends, and Player Attacks
    elif enemy_action == 'D':
        if action == 'A':
            if "block is broken" in result:
                enemy_health -= damage
            elif "parries your attack" in result:
                health -= 1

    return enemy_health, health


def fight(health: int, enemy_health: int, enemy_status: str, enemy_status_duration: int, weapon: str) -> Tuple[int, str, bool]:
    """Actual fight sequence. Returns updated health and whether enemy is defeated."""

    damage: int = 0
    status_effect: str = enemy_status
    status_effect_duration: int = enemy_status_duration
    is_critical_hit: bool = False # New flag to track critical hit

    while health > 0 and enemy_health > 0:
        clear_terminal()
        print(f"\nYour Health: {health} | Enemy Health: {enemy_health}")

        # Player's Turn
        action: str = input("Do you want to (A)ttack or (D)efend? ").strip().upper()
        print("\n")
        
        # Reset turn variables
        damage = 0
        is_critical_hit = False
        
        # If Player Attacks
        if action == 'A':
            base_damage: int
            crit_damage: int
            base_damage, crit_damage = WEAPON_DAMAGE.get(weapon, (1, 1))
            status_effect = WEAPON_STATUS_EFFECTS.get(weapon, "None")
            
            # 10% chance for critical hit (randint(0, 9) == 0 gives 1/10)
            if randint(0, 9) == 0: 
                damage = crit_damage
                is_critical_hit = True
            else:
                damage = base_damage

            # Apply Poison status effect to the "Poison Bow"
            if weapon == "Poison Bow" and randint(0, 9) < 2:  # 20% chance to apply poison
                status_effect = "Poisoned"
                status_effect_duration = 2  # Poison lasts for 3 turns

        # If Player Defends
        elif action == 'D':
            print("You defend and brace yourself!")
        
        # Invalid Action by the Player
        else:
            print("Invalid action. You lose your turn!")
            action = ''

        # Enemy's turn
        enemy_action: str
        restult: str
        enemy_action, result = enemy_turn(action)
        print(result) # Print enemy's main turn message

        # Critical Hit Message
        if is_critical_hit:
            print("Your attack was a Critical Hit!")

        # Enemy Heal Disrupted Message
        if action == 'A' and enemy_action == 'H':
            # The enemy is healing, but the player attacked, interrupting the heal.
            print("The Enemy's Heal was Disrupted by your Attack. They lose 1 HP!")

        # Apply Poison Effect if applicable
        if status_effect == "Poisoned" and status_effect_duration > 0:
            enemy_health -= 1
            status_effect_duration -= 1
            print("The enemy takes 1 poison damage!")
        
        input("Press Enter to continue...")

        # Turn Outcomes
        enemy_health, health = handle_turn_outcomes(enemy_action, action, health, enemy_health, damage, result)

        # The enemy has been defeated
        if enemy_health <= 0:
            print("Enemy defeated!")
            return health, "None", True
        # The player has been defeated
        if health <= 0:
            print("You were defeated!")
            return 0, "None", False

    return health, status_effect, enemy_health <= 0

def enemy_encounter(game_state: str, enemy: Enemy, player: Player) -> tuple[str, int]:
    """Handle the enemy encounter state. Returns updated game state and health."""

    # Initialize encounter
    print("You encountered an enemy!")

    while True:

        # Choose to Fight or Run
        clear_terminal()
        action = input("Do you want to (F)ight or (R)un away? ").upper()

        # Player chooses to fight
        if action == 'F':
            print("You chose to fight!")
            player.health, enemy.status, enemy_defeated = fight(player.health, enemy.health, enemy.status, enemy.status_duration, player.weapon)

            # Update Enemy Health based on Fight Outcome
            enemy.health = 0 if enemy_defeated else enemy.health

            # Checking for All Possible ways to End the Encounter
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