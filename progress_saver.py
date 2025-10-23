from typing import Optional
from game_data import GameState, clear_terminal

SAVE_FILE = 'savegame.dat'

def save_game_prompt(state: GameState) -> None:
    """Prompt the user to save the game and execute the save."""
    clear_terminal()
    print("--- Save Game ---")
    action = input("Do you want to save your current progress? (Y/N): ").strip().upper()
    
    if action == 'Y':
        state.save_to_file(SAVE_FILE)
    else:
        print("Save cancelled.")
        
    input("Press Enter to continue...")

def load_game_prompt() -> Optional[GameState]:
    """Prompt the user to load the game and execute the load."""
    clear_terminal()
    print("--- Load Game ---")
    action = input("Do you want to load a saved game? (Y/N): ").strip().upper()
    
    if action == 'Y':
        return GameState.load_from_file(SAVE_FILE)
    else:
        return None