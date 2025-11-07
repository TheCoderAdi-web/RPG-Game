from typing import Tuple, Optional
from random import randint
from game_data import Enemy, Player, WEAPON_DAMAGE, WEAPON_STATUS_EFFECTS, PLAYER_DEFENCE_OUTCOMES_MAP, ENEMY_DEFENCE_OUTCOMES_MAP, clear_terminal, OutcomeCodes

def enemy_turn(player_action: str) -> tuple[str, str, str]:
    """Determine and process the enemy's action. Returns (enemy_action, outcome_code, message)."""

    enemy_actions = {0: 'A', 1: 'D', 2: 'H'}
    enemy_action = enemy_actions[randint(0, 2)]

    # Enemy Attacks
    if enemy_action == 'A':
        if player_action == 'D':
            # Use outcome map to get code and message
            code, message = PLAYER_DEFENCE_OUTCOMES_MAP[randint(0, 1)]
            return enemy_action, code, message
        
        # Player is attacking or invalid action
        return enemy_action, "None", "Enemy attacks! You take 1 damage!"
    
    # Enemy Defends
    elif enemy_action == 'D':
        if player_action == 'A':
            # Use outcome map to get code and message
            code, message = ENEMY_DEFENCE_OUTCOMES_MAP[randint(0, 2)]
            return enemy_action, code, message
        else:
            return enemy_action, OutcomeCodes.STALEMATE, "Both you and the enemy are defending. A stalemate occurs."
            
    # Enemy Heals
    elif enemy_action == 'H':
        # If player defended, the message is pulled from the Defence Map (index 2)
        if player_action == 'D':
            code, message = PLAYER_DEFENCE_OUTCOMES_MAP[2]
            return enemy_action, code, message
        
        return enemy_action, "None", "Enemy heals and regains 1 health."
    
    else:
        # Fallback (should not be reached)
        return enemy_action, "None", "does nothing."

def handle_turn_outcomes(enemy_action: str, action: str, player: Player, enemy: Enemy, damage: int, outcome_code: str) -> None:
    """Handles the turn outcomes by modifying Player and Enemy objects directly.
       Uses the robust outcome_code instead of checking message strings."""
    
    # If Enemy Heals
    if enemy_action == 'H':
        if action == 'D':
            # Enemy gets +1 health if player defended
            enemy.health += 1
        elif action == 'A':
            # Enemy's heal is interrupted by attack, damage is applied
            enemy.health -= damage

    # If Enemy Attacks
    elif enemy_action == 'A':
        if action == 'D':
            # Check the specific defense outcome code
            if outcome_code == OutcomeCodes.PLAYER_DEFEND_FAIL:
                    player.health -= 1
            # If outcome_code is PLAYER_DEFEND_SUCCESS, no damage is taken.
        elif action == 'A':
            # Both attack: standard damage is applied
            player.health -= 1
            enemy.health -= damage
        else:
            # Player invalid action: standard enemy damage
            player.health -= 1
        
    # If Enemy Defends
    elif enemy_action == 'D':
        if action == 'A':
            # Check the specific enemy defense outcome code
            if outcome_code == OutcomeCodes.ENEMY_BLOCK_BROKEN:
                enemy.health -= damage
            elif outcome_code == OutcomeCodes.ENEMY_PARRY:
                player.health -= 1 # Player takes parry damage

def fight(player: Player, enemy: Enemy) -> bool:
    """Actual fight sequence. Returns whether enemy is defeated."""

    damage: int = 0
    is_critical_hit: bool = False

    while player.health > 0 and enemy.health > 0:
        clear_terminal()
        print(f"\nYour Health: {player.health} | Enemy Health: {enemy.health}")
        print(f"Enemy Status: {enemy.status} (Duration: {enemy.status_duration})")

        # Player's Turn
        action: str = input("Do you want to (A)ttack or (D)efend? ").strip().upper()
        print("\n")
        
        # Reset turn variables
        damage = 0
        is_critical_hit = False
        
        if action == 'A':
            base_damage: int
            crit_damage: int
            base_damage, crit_damage = WEAPON_DAMAGE.get(player.weapon, (1, 1))
            
            if randint(0, 9) == 0: 
                damage = crit_damage
                is_critical_hit = True
            else:
                damage = base_damage

            weapon_status: str = WEAPON_STATUS_EFFECTS.get(player.weapon, "None")
            if weapon_status != "None" and randint(0, 9) < 2:
                enemy.status = weapon_status
                enemy.status_duration = 2

        elif action == 'D':
            print("You defend and brace yourself!")
        
        else:
            print("Invalid action. You lose your turn!")
            action = ''

        # Enemy's turn - returns code and message
        enemy_action: str
        outcome_code: str
        result_message: str
        enemy_action, outcome_code, result_message = enemy_turn(action)
        print(result_message)

        # Print secondary messages
        if is_critical_hit:
            print("Your attack was a Critical Hit!")
        if action == 'A' and enemy_action == 'H':
            print("The Enemy's Heal was Disrupted by your Attack!")

        # Apply Poison Effect if applicable
        if enemy.status == "Poisoned" and enemy.status_duration > 0:
            enemy.health -= 1
            enemy.status_duration -= 1
            print("The enemy takes 1 poison damage!")
        
        input("Press Enter to continue...")

        # Turn Outcomes - uses the robust outcome_code
        handle_turn_outcomes(enemy_action, action, player, enemy, damage, outcome_code)

        if enemy.health <= 0:
            print("Enemy defeated!")
            return True
        if player.health <= 0:
            print("You were defeated!")
            return False

    return enemy.health <= 0

def enemy_encounter(game_state: str, enemy: Enemy, player: Player) -> Tuple[str, int]:
    """Handle the enemy encounter state. Returns updated game state and player health."""

    print("You encountered an enemy!")

    while True:
        clear_terminal()
        action = input("Do you want to (F)ight or (R)un away? ").upper()

        if action == 'F':
            print("You chose to fight!")
            enemy_defeated = fight(player, enemy)

            if player.health <= 0:
                game_state = "game_over"
            elif enemy_defeated:
                print("You defeated the enemy!")
                game_state = "playing"
            break

        elif action == 'R':
            print("You chose to run away!")
            game_state = "playing"
            break

        else:
            print("Invalid action.")

    return game_state, player.health