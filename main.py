"""
Fantasy RPG Text Adventure Game
A text-based adventure game that uses MongoDB for data storage
and Google Gemini for generating responses.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

from game.game_engine import GameEngine

# Load environment variables
load_dotenv()

def print_welcome():
    """Print the welcome message."""
    print("\n" + "=" * 60)
    print("FANTASY RPG TEXT ADVENTURE".center(60))
    print("=" * 60)
    print("A text-based adventure game with MongoDB and Google Gemini".center(60))
    print("=" * 60 + "\n")

def print_menu():
    """Print the main menu."""
    print("\nMAIN MENU:")
    print("1. New Game")
    print("2. Load Game")
    print("3. Delete Game")
    print("4. List All Characters")
    print("5. About")
    print("6. Exit")
    return input("\nSelect an option (1-6): ")

def new_game(game_engine):
    """Create a new game."""
    print("\nCREATE NEW CHARACTER")
    print("--------------------")
    
    name = input("Enter your character's name: ")
    if not name:
        print("Invalid name. Returning to main menu.")
        return
    
    print("\nChoose your class:")
    print("1. Warrior - Strong and tough, specializes in melee combat")
    print("2. Mage - Intelligent and magical, specializes in spells")
    print("3. Rogue - Quick and stealthy, specializes in critical hits")
    
    class_choice = input("\nSelect a class (1-3): ")
    
    class_map = {
        "1": "warrior",
        "2": "mage",
        "3": "rogue"
    }
    
    if class_choice not in class_map:
        print("Invalid choice. Returning to main menu.")
        return
    
    player_class = class_map[class_choice]
    
    success, message = game_engine.create_new_player(name, player_class)
    print(f"\n{message}")
    
    if success:
        start_game(game_engine)

def load_game(game_engine):
    """Load an existing game."""
    print("\nLOAD CHARACTER")
    print("-------------")
    
    name = input("Enter your character's name: ")
    if not name:
        print("Invalid name. Returning to main menu.")
        return
    
    success, message = game_engine.load_player_by_name(name)
    print(f"\n{message}")
    
    if success:
        start_game(game_engine)
        
def delete_game(game_engine):
    """Delete an existing game."""
    print("\nDELETE CHARACTER")
    print("---------------")
    
    name = input("Enter the character's name to delete: ")
    if not name:
        print("Invalid name. Returning to main menu.")
        return
    
    # Confirm deletion
    confirm = input(f"Are you sure you want to delete the character '{name}'? This cannot be undone. (y/n): ")
    if confirm.lower() != "y":
        print("Deletion cancelled. Returning to main menu.")
        return
    
    success, message = game_engine.delete_player_by_name(name)
    print(f"\n{message}")

def list_all_characters(game_engine):
    """List all characters in the database."""
    print("\nALL CHARACTERS")
    print("-------------")
    
    success, result = game_engine.list_all_characters()
    
    if not success:
        print(result)
        return
    
    if not result:
        print("No characters found in the database.")
        return
    
    print(f"{'Name':<15} {'Class':<10} {'Level':<8} {'Last Played':<20}")
    print("-" * 60)
    
    for player in result:
        last_played = player.get("last_played", "Never")
        if isinstance(last_played, datetime):
            last_played = last_played.strftime("%Y-%m-%d %H:%M")
        
        print(f"{player['name']:<15} {player.get('class', 'Unknown'):<10} {player.get('level', 1):<8} {last_played:<20}")
    
    input("\nPress Enter to return to the main menu...")

def about():
    """Show information about the game."""
    print("\nABOUT THE GAME")
    print("-------------")
    print("Fantasy RPG Text Adventure is a text-based adventure game")
    print("that uses MongoDB for data storage and Google Gemini for")
    print("generating dynamic, contextual responses.")
    print("\nCreated as a demonstration project for integrating")
    print("database systems with AI-generated content.")
    input("\nPress Enter to return to the main menu...")

def start_game(game_engine):
    """Start the main game loop."""
    print("\n" + "=" * 60)
    print("Your adventure begins...".center(60))
    print("=" * 60 + "\n")
    
    # Show initial location description
    print(game_engine.get_location_description())
    
    # Main game loop
    while True:
        print("\n" + "-" * 60)
        command = input("> ").strip()
        
        if command.lower() in ["quit", "exit", "menu"]:
            confirm = input("Return to main menu? (y/n): ")
            if confirm.lower() == "y":
                break
            else:
                continue
        
        # Process the command
        response = game_engine.process_command(command)
        print("\n" + response)

def main():
    """Main function."""
    # Check if MongoDB connection string is set
    if not os.getenv("MONGODB_URI"):
        print("Error: MongoDB connection string not found in .env file.")
        print("Please set MONGODB_URI in the .env file.")
        return
    
    # Check if Gemini API key is set
    if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "your_gemini_api_key_here":
        print("Warning: Google Gemini API key not properly set in .env file.")
        print("AI-generated responses will not work correctly.")
        print("Please set GEMINI_API_KEY in the .env file.")
        input("Press Enter to continue anyway...")
    
    # Initialize game engine
    game_engine = GameEngine()
    
    # Show welcome message
    print_welcome()
    
    # Main menu loop
    while True:
        choice = print_menu()
        
        if choice == "1":
            new_game(game_engine)
        elif choice == "2":
            load_game(game_engine)
        elif choice == "3":
            delete_game(game_engine)
        elif choice == "4":
            list_all_characters(game_engine)
        elif choice == "5":
            about()
        elif choice == "6":
            print("\nThank you for playing! Goodbye.")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()