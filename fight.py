# Import necessary modules and classes
from typing import Tuple, Optional
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

def handle_turn_outcomes(enemy_action: str, action: str, player: Player, enemy: Enemy, damage: int, result: str) -> None:
    """Handles the turn outcomes by modifying Player and Enemy objects directly."""
    
    # If Enemy Heals
    if enemy_action == 'H':
        if action == 'D':
            enemy.health += 1
        elif action == 'A':
            # Enemy's heal is interrupted by attack, damage is applied in fight()
            enemy.health -= damage

    # If Enemy Attacks and Player Defends or Attacks
    elif enemy_action == 'A':
        if action == 'D':
            if "failed to defend" in result:
                    player.health -= 1
            else:
                pass  # No damage taken when successfully defending
        elif action == 'A':
            player.health -= 1
            enemy.health -= damage
        else:
            player.health -= 1
        
    # If Enemy Defends, and Player Attacks
    elif enemy_action == 'D':
        if action == 'A':
            if "block is broken" in result:
                enemy.health -= damage
            elif "parries your attack" in result:
                player.health -= 1

def fight(player: Player, enemy: Enemy) -> bool:
    """Actual fight sequence. Returns whether enemy is defeated."""

    damage: int = 0
    is_critical_hit: bool = False # New flag to track critical hit

    while player.health > 0 and enemy.health > 0:
        clear_terminal()
        print(f"\nYour Health: {player.health} | Enemy Health: {enemy.health}")

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
            base_damage, crit_damage = WEAPON_DAMAGE.get(player.weapon, (1, 1))
            
            # 10% chance for critical hit (randint(0, 9) == 0 gives 1/10)
            if randint(0, 9) == 0: 
                damage = crit_damage
                is_critical_hit = True
            else:
                damage = base_damage

            # Apply Status Effects
            weapon_status: str = WEAPON_STATUS_EFFECTS.get(player.weapon, "None")
            if weapon_status != "None" and randint(0, 9) < 2: # 2 / 10 OR 20% chance for effect. Also eleminates weapons with "None" status effect
                enemy.status = weapon_status
                enemy.status_duration = 2

        # If Player Defends
        elif action == 'D':
            print("You defend and brace yourself!")
        
        # Invalid Action by the Player
        else:
            print("Invalid action. You lose your turn!")
            action = ''

        # Enemy's turn
        enemy_action: str
        result: str
        enemy_action, result = enemy_turn(action)
        print(result) # Print enemy's main turn message

        # Critical Hit Message
        if is_critical_hit:
            print("Your attack was a Critical Hit!")

        # Enemy Heal Disrupted Message
        if action == 'A' and enemy_action == 'H':
            # The enemy is healing, but the player attacked, interrupting the heal.
            print("The Enemy's Heal was Disrupted by your Attack!")

        # Apply Poison Effect if applicable
        if enemy.status == "Poisoned" and enemy.status_duration > 0:
            enemy.health -= 1
            enemy.status_duration -= 1
            print("The enemy takes 1 poison damage!")
        
        input("Press Enter to continue...")

        # Turn Outcomes
        handle_turn_outcomes(enemy_action, action, player, enemy, damage, result)

        # The enemy has been defeated
        if enemy.health <= 0:
            print("Enemy defeated!")
            return True
        # The player has been defeated
        if player.health <= 0:
            print("You were defeated!")
            return False

    return enemy.health <= 0

def enemy_encounter(game_state: str, enemy: Enemy, player: Player) -> Tuple[str, int]:
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
            enemy_defeated = fight(player, enemy)

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