"""
Fantasy RPG Text Adventure Game - Streamlit Edition
A text-based adventure game that uses MongoDB for data storage
and Google Gemini for generating responses.
"""

import os
import sys
import streamlit as st
from dotenv import load_dotenv

from game.game_engine import GameEngine

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Fantasy RPG Text Adventure",
    page_icon="🧙‍♂️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-title {
        font-size: 3rem !important;
        font-weight: 700 !important;
        color: #4B0082 !important;
        text-align: center !important;
        margin-bottom: 1rem !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    .sub-title {
        font-size: 1.2rem !important;
        font-weight: 400 !important;
        color: #6A5ACD !important;
        text-align: center !important;
        margin-bottom: 2rem !important;
    }
    .divider {
        margin: 2rem 0;
        border-top: 2px solid #DDA0DD;
    }
    .game-area {
        background-color: #F8F8FF;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #DDA0DD;
        margin-bottom: 20px;
    }
    .command-input {
        border: 2px solid #9370DB !important;
        border-radius: 5px !important;
    }
    .stButton button {
        background-color: #9370DB !important;
        color: white !important;
        font-weight: bold !important;
    }
    .stButton button:hover {
        background-color: #7B68EE !important;
    }
    .response-area {
        background-color: #F0F0F8;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #9370DB;
        margin: 10px 0;
    }
    .character-info {
        background-color: #E6E6FA;
        padding: 15px;
        border-radius: 5px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'game_engine' not in st.session_state:
        st.session_state.game_engine = GameEngine()
    
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
    
    if 'current_screen' not in st.session_state:
        st.session_state.current_screen = "main_menu"
    
    if 'game_log' not in st.session_state:
        st.session_state.game_log = []

def display_welcome():
    """Display the welcome message."""
    st.markdown("<h1 class='main-title'>FANTASY RPG TEXT ADVENTURE</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>A text-based adventure game with MongoDB and Google Gemini</p>", unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

def display_main_menu():
    """Display the main menu."""
    st.subheader("MAIN MENU")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("New Game", key="new_game_btn"):
            st.session_state.current_screen = "new_game"
    
    with col2:
        if st.button("Load Game", key="load_game_btn"):
            st.session_state.current_screen = "load_game"
    
    with col3:
        if st.button("Delete Game", key="delete_game_btn"):
            st.session_state.current_screen = "delete_game"
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("About", key="about_btn"):
            st.session_state.current_screen = "about"
    
    with col2:
        if st.button("Exit", key="exit_btn"):
            st.session_state.current_screen = "exit"
            st.markdown("Thank you for playing! Close this browser tab to exit completely.")

def new_game_screen():
    """Create a new game screen."""
    st.subheader("CREATE NEW CHARACTER")
    
    with st.form("new_character_form"):
        name = st.text_input("Enter your character's name:")
        
        st.write("Choose your class:")
        class_choice = st.radio(
            "Select a class:",
            [
                "Warrior - Strong and tough, specializes in melee combat",
                "Mage - Intelligent and magical, specializes in spells",
                "Rogue - Quick and stealthy, specializes in critical hits"
            ],
            index=0
        )
        
        submit_button = st.form_submit_button("Create Character")
        
        if submit_button:
            if not name:
                st.error("Please enter a character name.")
            else:
                # Map the class choice to the expected format
                class_map = {
                    "Warrior - Strong and tough, specializes in melee combat": "warrior",
                    "Mage - Intelligent and magical, specializes in spells": "mage",
                    "Rogue - Quick and stealthy, specializes in critical hits": "rogue"
                }
                
                player_class = class_map[class_choice]
                
                success, message = st.session_state.game_engine.create_new_player(name, player_class)
                
                if success:
                    st.success(message)
                    st.session_state.game_started = True
                    st.session_state.current_screen = "game"
                    st.session_state.game_log = [f"Welcome, {name} the {player_class.capitalize()}!"]
                    # Add the initial location description to the game log
                    location_desc = st.session_state.game_engine.get_location_description()
                    st.session_state.game_log.append(location_desc)
                else:
                    st.error(message)
    
    if st.button("Back to Main Menu", key="back_from_new_game"):
        st.session_state.current_screen = "main_menu"

def load_game_screen():
    """Load an existing game screen."""
    st.subheader("LOAD CHARACTER")
    
    with st.form("load_character_form"):
        name = st.text_input("Enter your character's name:")
        
        submit_button = st.form_submit_button("Load Character")
        
        if submit_button:
            if not name:
                st.error("Please enter a character name.")
            else:
                success, message = st.session_state.game_engine.load_player_by_name(name)
                
                if success:
                    st.success(message)
                    st.session_state.game_started = True
                    st.session_state.current_screen = "game"
                    st.session_state.game_log = [f"Welcome back, {name}!"]
                    # Add the current location description to the game log
                    location_desc = st.session_state.game_engine.get_location_description()
                    st.session_state.game_log.append(location_desc)
                else:
                    st.error(message)
    
    if st.button("Back to Main Menu", key="back_from_load_game"):
        st.session_state.current_screen = "main_menu"

def delete_game_screen():
    """Delete an existing game screen."""
    st.subheader("DELETE CHARACTER")
    
    with st.form("delete_character_form"):
        name = st.text_input("Enter the character's name to delete:")
        
        confirm = st.checkbox("I understand this action cannot be undone.")
        
        submit_button = st.form_submit_button("Delete Character")
        
        if submit_button:
            if not name:
                st.error("Please enter a character name.")
            elif not confirm:
                st.error("You must confirm the deletion.")
            else:
                success, message = st.session_state.game_engine.delete_player_by_name(name)
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
    
    if st.button("Back to Main Menu", key="back_from_delete_game"):
        st.session_state.current_screen = "main_menu"

def about_screen():
    """Show information about the game."""
    st.subheader("ABOUT THE GAME")
    
    st.markdown("""
    Fantasy RPG Text Adventure is a text-based adventure game that uses MongoDB for data storage 
    and Google Gemini for generating dynamic, contextual responses.
    
    Created as a demonstration project for integrating database systems with AI-generated content.
    
    **How to Play:**
    1. Create a new character or load an existing one
    2. Explore the world by typing commands like "go north", "look around", "talk to merchant"
    3. Battle enemies, complete quests, and discover items
    4. Type "help" at any time to see available commands
    """)
    
    if st.button("Back to Main Menu", key="back_from_about"):
        st.session_state.current_screen = "main_menu"

def game_screen():
    """Main game screen."""
    # Display character info in the sidebar
    with st.sidebar:
        st.subheader("Character Info")
        player = st.session_state.game_engine.current_player
        
        # Only show character info if a player is loaded
        if player:
            st.markdown(f"""
            <div class='character-info'>
                <p><strong>Name:</strong> {player['name']}</p>
                <p><strong>Class:</strong> {player['class'].capitalize()}</p>
                <p><strong>Level:</strong> {player['level']}</p>
                <p><strong>Health:</strong> {player['health']}/{player['max_health']}</p>
                <p><strong>Gold:</strong> {player['gold']}</p>
                <p><strong>Location:</strong> {st.session_state.game_engine.current_location['_id'] if st.session_state.game_engine.current_location else 'Unknown'}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No character loaded. Please create or load a character.")
        
        # Only show these buttons if a player is loaded
        if player:
            if st.button("Character Status"):
                status = st.session_state.game_engine._show_character_status()
                st.session_state.game_log.append(status)
            
            if st.button("Show Inventory"):
                inventory = st.session_state.game_engine._show_inventory()
                st.session_state.game_log.append(inventory)
            
            if st.button("Show Quests"):
                quests = st.session_state.game_engine._show_quests()
                st.session_state.game_log.append(quests)
        
        # Always show help button
        if st.button("Help"):
            help_text = st.session_state.game_engine._show_help()
            st.session_state.game_log.append(help_text)
        
        if st.button("Return to Main Menu"):
            if st.session_state.game_started:
                st.session_state.current_screen = "confirm_exit"
            else:
                st.session_state.current_screen = "main_menu"
    
    # Main game area
    st.markdown("<div class='game-area'>", unsafe_allow_html=True)
    
    # Display game log (scrollable area)
    game_log_container = st.container()
    with game_log_container:
        if st.session_state.game_log:
            for log_entry in st.session_state.game_log:
                st.markdown(f"<div class='response-area'>{log_entry}</div>", unsafe_allow_html=True)
        else:
            st.info("Your adventure begins here. Type a command below to start playing.")
    
    # Command input
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    command = st.text_input("Enter your command:", key="command_input")
    
    if command and command.strip():  # Check if command is not None and not just whitespace
        if command.lower() in ["quit", "exit", "menu"]:
            st.session_state.current_screen = "confirm_exit"
        else:
            # Process the command
            response = st.session_state.game_engine.process_command(command)
            st.session_state.game_log.append(response)
            
            # Clear the command input by forcing a rerun
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def confirm_exit_screen():
    """Confirm exit from game screen."""
    st.subheader("Return to Main Menu?")
    st.write("Any unsaved progress may be lost.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Yes, return to menu"):
            st.session_state.current_screen = "main_menu"
    
    with col2:
        if st.button("No, continue playing"):
            st.session_state.current_screen = "game"

def check_environment():
    """Check if required environment variables are set."""
    missing_vars = []
    
    if not os.getenv("MONGODB_URI"):
        missing_vars.append("MONGODB_URI")
    
    if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "your_gemini_api_key_here":
        missing_vars.append("GEMINI_API_KEY")
    
    return missing_vars

def main():
    """Main function."""
    # Initialize session state
    initialize_session_state()
    
    # Display welcome message
    display_welcome()
    
    # Check environment variables
    missing_vars = check_environment()
    if missing_vars:
        st.error(f"Missing environment variables: {', '.join(missing_vars)}")
        st.info("Please set these variables in your .env file to ensure the game works correctly.")
        
        if "GEMINI_API_KEY" in missing_vars:
            st.warning("Without a Google Gemini API key, AI-generated responses will not work correctly.")
        
        if "MONGODB_URI" in missing_vars:
            st.error("MongoDB connection string is required for the game to function.")
            return
    
    # Display the appropriate screen based on current_screen state
    if st.session_state.current_screen == "main_menu":
        display_main_menu()
    elif st.session_state.current_screen == "new_game":
        new_game_screen()
    elif st.session_state.current_screen == "load_game":
        load_game_screen()
    elif st.session_state.current_screen == "delete_game":
        delete_game_screen()
    elif st.session_state.current_screen == "about":
        about_screen()
    elif st.session_state.current_screen == "game":
        # Check if a player is loaded before showing the game screen
        if st.session_state.game_engine.current_player:
            game_screen()
        else:
            st.error("No character loaded. Please create or load a character first.")
            st.session_state.current_screen = "main_menu"
            display_main_menu()
    elif st.session_state.current_screen == "confirm_exit":
        confirm_exit_screen()
    elif st.session_state.current_screen == "exit":
        st.markdown("Thank you for playing! Close this browser tab to exit completely.")

if __name__ == "__main__":
    main()