import streamlit as st
import os
import sys
from dotenv import load_dotenv
import pymongo

# Import utilities and components
from utils.database import init_database
from utils.session import init_session_state, set_page
from components.character import create_character_ui, load_character_ui
from components.inventory import render_inventory_ui
from components.combat import render_combat_ui, trigger_combat

# Add parent directory to path to import game modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Fantasy RPG Adventure",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
def load_css(css_file):
    with open(css_file, "r") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

try:
    load_css("streamlit_app/custom.css")
except Exception as e:
    st.error(f"Error loading CSS: {e}")

# Background image
def add_bg_image():
    bg_image = """
    <style>
    .stApp {
        background-image: url("https://www.transparenttextures.com/patterns/parchment.png");
        background-size: cover;
    }
    </style>
    """
    st.markdown(bg_image, unsafe_allow_html=True)

# Initialize session state
init_session_state()

# Add background image
add_bg_image()

# Connect to MongoDB
try:
    db = init_database()
    st.session_state.db = db
except Exception as e:
    st.error(f"Failed to connect to MongoDB: {e}")
    st.stop()

# Sidebar
def render_sidebar():
    with st.sidebar:
        st.image("https://i.imgur.com/8MsbEfS.png", width=200)  # Replace with your logo
        st.title("Fantasy RPG")
        
        if st.session_state.player:
            player = st.session_state.player
            st.subheader(f"{player['name']} the {player['class']}")
            
            # Character stats
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Level", player.get('level', 1))
                st.metric("Health", f"{player.get('current_health', 0)}/{player.get('max_health', 0)}")
                st.metric("Gold", player.get('gold', 0))
            with col2:
                st.metric("XP", player.get('experience', 0))
                st.metric("Attack", player.get('attack', 0))
                st.metric("Defense", player.get('defense', 0))
            
            # Navigation menu
            st.subheader("Navigation")
            if st.button("Character", key="nav_character"):
                set_page("character")
            
            if st.button("Inventory", key="nav_inventory"):
                set_page("inventory")
            
            if st.button("Quests", key="nav_quests"):
                set_page("quests")
            
            if st.button("Map", key="nav_map"):
                set_page("map")
            
            if st.button("Game", key="nav_game"):
                set_page("game")
            
            if st.button("Main Menu", key="nav_home"):
                set_page("home")
        else:
            st.info("Create or load a character to begin your adventure!")
            
            if st.button("Create Character", key="create_character_sidebar"):
                set_page("create_character")
            
            if st.button("Load Character", key="load_character_sidebar"):
                set_page("load_character")
            
            if st.button("About", key="about_sidebar"):
                set_page("about")

# Home page
def render_home():
    st.title("Fantasy RPG Text Adventure")
    st.markdown("""
    <div class="game-container">
        <h2>Welcome, Adventurer!</h2>
        <p>Embark on an epic journey through a world of magic, monsters, and mystery.</p>
        <p>Create a character, explore the realm, complete quests, and become a legendary hero!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Create New Character", key="create_character"):
            set_page("create_character")
    
    with col2:
        if st.button("Load Character", key="load_character"):
            set_page("load_character")
    
    with col3:
        if st.button("About", key="about"):
            set_page("about")

# World map
def render_map():
    from utils.database import get_all_locations
    from utils.session import get_player, get_current_location, add_game_text, set_current_location
    import random
    
    st.title("World Map")
    
    # Get all locations
    try:
        locations = get_all_locations(st.session_state.db)
        current_location = get_current_location()
        player = get_player()
        
        if not locations:
            st.info("No locations found.")
            return
        
        # Simplified map view
        st.write("Click on a location to travel there:")
        
        # Create a grid of locations
        cols = st.columns(3)
        current_location_id = current_location['id']
        
        for i, location in enumerate(locations):
            with cols[i % 3]:
                is_current = location['id'] == current_location_id
                
                # Determine if the location is accessible
                is_accessible = False
                
                if is_current:
                    is_accessible = True
                else:
                    # Check if this location is connected to the current location
                    for exit_info in current_location.get('exits', []):
                        if exit_info['target'] == location['id']:
                            is_accessible = True
                            break
                
                # Display location
                background_color = "#4a2511" if is_current else ("#8b5a2b" if is_accessible else "#a9a9a9")
                
                st.markdown(f"""
                <div style="background-color: {background_color}; color: white; padding: 10px; border-radius: 5px; margin: 5px; text-align: center;">
                    <h3>{location['name']}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Add travel button if accessible
                if is_accessible and not is_current:
                    if st.button(f"Travel to {location['name']}", key=f"travel_{location['id']}"):
                        # Move to new location
                        set_current_location(location)
                        
                        # Update player location in database
                        st.session_state.db.players.update_one(
                            {"_id": player["_id"]},
                            {"$set": {"location": location['id']}}
                        )
                        
                        # Add movement message
                        add_game_text(f"You travel to {location['name']}.")
                        
                        # Random encounter check (20% chance)
                        if random.random() < 0.2:
                            trigger_combat()
                        
                        set_page("game")
                        st.experimental_rerun()
                elif is_current:
                    st.info("You are here")
                else:
                    st.write("Not accessible from current location")
    
    except Exception as e:
        st.error(f"Error loading map: {e}")
    
    if st.button("Return to Game"):
        set_page("game")

# About page
def render_about():
    st.title("About Fantasy RPG")
    
    st.markdown("""
    <div class="game-container">
        <h2>Fantasy RPG Text Adventure</h2>
        <p>Welcome to our fantasy text adventure game combining traditional RPG mechanics with modern technologies.</p>
        
        <h3>Key Features:</h3>
        <ul>
            <li>Character creation and progression</li>
            <li>Combat system with various enemies</li>
            <li>Quest system</li>
            <li>Inventory management</li>
            <li>World exploration</li>
        </ul>
        
        <h3>Technical Details:</h3>
        <ul>
            <li>Built with Python and Streamlit</li>
            <li>MongoDB for data persistence</li>
            <li>Google Gemini AI for dynamic content generation</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Return to Home"):
        set_page("home")

# Quest page
def render_quests():
    from utils.session import get_player, set_page
    
    st.title("Quest Journal")
    
    player = get_player()
    
    # Get active quests
    active_quests = player.get('quests', [])
    
    if not active_quests:
        st.info("You don't have any active quests.")
    else:
        for quest in active_quests:
            # Display quest information
            with st.expander(quest.get('name', 'Unknown Quest'), expanded=True):
                st.markdown(f"""
                <div class="quest-item">
                    <p><strong>Description:</strong> {quest.get('description', '')}</p>
                    <p><strong>Status:</strong> {get_quest_status(quest)}</p>
                    <p><strong>Rewards:</strong> {get_quest_rewards(quest)}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show objectives
                st.subheader("Objectives")
                
                for objective in quest.get('objectives', []):
                    status = "Completed" if objective.get('completed', False) else "In Progress"
                    st.markdown(f"""
                    <div class="quest-item {'quest-complete' if status == 'Completed' else ''}">
                        <p>{objective.get('description', '')}: {status}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    if st.button("Return to Game"):
        set_page("game")

def get_quest_status(quest):
    objectives = quest.get('objectives', [])
    completed = sum(1 for obj in objectives if obj.get('completed', False))
    total = len(objectives)
    
    if completed == total:
        return "Completed"
    else:
        return f"In Progress ({completed}/{total})"

def get_quest_rewards(quest):
    rewards = []
    
    if 'xp_reward' in quest:
        rewards.append(f"{quest['xp_reward']} XP")
    
    if 'gold_reward' in quest:
        rewards.append(f"{quest['gold_reward']} Gold")
    
    if 'item_rewards' in quest:
        for item in quest.get('item_rewards', []):
            rewards.append(item.get('name', 'Unknown Item'))
    
    return ", ".join(rewards) if rewards else "None"

# Character details page
def render_character():
    from utils.session import get_player, set_page
    
    st.title("Character Sheet")
    
    player = get_player()
    
    # Character info
    st.header(f"{player['name']} the {player['class']}")
    
    # Character stats
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Stats")
        st.metric("Level", player.get('level', 1))
        st.metric("Experience", player.get('experience', 0))
        st.metric("Next Level", player.get('level', 1) * 100)
        st.metric("Health", f"{player.get('current_health', 0)}/{player.get('max_health', 0)}")
        st.metric("Gold", player.get('gold', 0))
    
    with col2:
        st.subheader("Combat Stats")
        st.metric("Attack", player.get('attack', 0))
        st.metric("Defense", player.get('defense', 0))
        st.metric("Evasion", f"{player.get('evasion', 0)}%")
        
        # Show equipped items
        st.subheader("Equipped Items")
        
        equipped = player.get('equipped', {})
        
        if not equipped:
            st.info("No items equipped.")
        else:
            for slot, item in equipped.items():
                st.markdown(f"""
                <div class="item-card">
                    <p><strong>{slot.capitalize()}:</strong> {item.get('name', 'Unknown')}</p>
                </div>
                """, unsafe_allow_html=True)
    
    if st.button("Return to Game"):
        set_page("game")

# Main game interface
def render_game():
    from utils.session import get_player, get_current_location, add_game_text, get_game_text, is_in_combat, set_page
    from utils.ai_helper import generate_command_response, generate_location_description
    import random
    
    player = get_player()
    
    if not player:
        st.warning("No character loaded. Please create or load a character first.")
        if st.button("Return to Home"):
            set_page("home")
        return
    
    # Get current location
    location = get_current_location()
    
    st.title(location['name'])
    
    # Display location description with AI enhancement
    st.markdown(f"""
    <div class="game-text">
        {location.get('description', 'You are in a mysterious place.')}
    </div>
    """, unsafe_allow_html=True)
    
    # Game text history
    st.subheader("Adventure Log")
    with st.container():
        for entry in get_game_text()[-10:]:  # Show last 10 entries
            if entry["type"] == "system":
                st.info(entry["text"])
            elif entry["type"] == "player":
                st.success(entry["text"])
            elif entry["type"] == "ai":
                st.write(entry["text"])
            elif entry["type"] == "combat":
                st.warning(entry["text"])
    
    # Combat interface
    if is_in_combat():
        render_combat_ui()
    else:
        # Available actions
        st.subheader("What would you like to do?")
        
        # Command input
        command = st.text_input("Enter a command", key="command_input")
        
        if st.button("Submit", key="submit_command"):
            if command:
                # Process command
                process_command(command)
                st.experimental_rerun()
        
        # Quick action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Look around"):
                process_command("look around")
                st.experimental_rerun()
        
        with col2:
            if st.button("Check inventory"):
                set_page("inventory")
                st.experimental_rerun()
        
        with col3:
            if st.button("View quests"):
                set_page("quests")
                st.experimental_rerun()
        
        with col4:
            if st.button("View map"):
                set_page("map")
                st.experimental_rerun()
        
        # Location exits
        st.subheader("Available Paths")
        exit_cols = st.columns(len(location.get('exits', [])) or 1)
        
        for i, exit_info in enumerate(location.get('exits', [])):
            with exit_cols[i]:
                if st.button(f"Go to {exit_info['name']}"):
                    # Move to new location
                    new_location = st.session_state.db.world.find_one({"id": exit_info['target']})
                    if new_location:
                        st.session_state.current_location = new_location
                        
                        # Update player location in database
                        st.session_state.db.players.update_one(
                            {"_id": player["_id"]},
                            {"$set": {"location": new_location['id']}}
                        )
                        
                        # Add movement message
                        add_game_text(f"You travel to {new_location['name']}.")
                        
                        # Random encounter check (20% chance)
                        if random.random() < 0.2:
                            trigger_combat()
                        
                        st.experimental_rerun()

def process_command(command):
    from utils.session import get_player, get_current_location, add_game_text, set_page
    from utils.ai_helper import generate_command_response
    from components.combat import trigger_combat
    
    command = command.lower()
    
    # Add command to game text
    add_game_text(f"> {command}", "player")
    
    # Process common commands
    if "look" in command:
        # Generate AI description of the surroundings
        location = get_current_location()
        
        from game.ai_generator import generate_response
        ai_message = generate_response(
            context=f"The player is in {location['name']}. {location.get('description', '')}",
            prompt="Describe the surroundings in detail."
        )
        
        add_game_text(ai_message, "ai")
    elif "inventory" in command:
        set_page("inventory")
    elif "quest" in command:
        set_page("quests")
    elif "map" in command:
        set_page("map")
    elif "stats" in command or "character" in command:
        set_page("character")
    elif any(direction in command for direction in ["north", "south", "east", "west", "go to"]):
        # Handle movement
        location = get_current_location()
        target_location = None
        
        for exit_info in location.get('exits', []):
            exit_name = exit_info['name'].lower()
            
            if exit_name in command or (
                "north" in command and "north" in exit_name or
                "south" in command and "south" in exit_name or
                "east" in command and "east" in exit_name or
                "west" in command and "west" in exit_name
            ):
                target_location = exit_info['target']
                break
        
        if target_location:
            new_location = st.session_state.db.world.find_one({"id": target_location})
            if new_location:
                st.session_state.current_location = new_location
                
                # Update player location in database
                st.session_state.db.players.update_one(
                    {"_id": get_player()["_id"]},
                    {"$set": {"location": new_location['id']}}
                )
                
                # Add movement message
                add_game_text(f"You travel to {new_location['name']}.")
                
                # Random encounter check (20% chance)
                if random.random() < 0.2:
                    trigger_combat()
        else:
            add_game_text("You can't go that way.")
    else:
        # Use AI to process other commands
        location = get_current_location()
        player = get_player()
        
        from game.ai_generator import generate_response
        ai_message = generate_response(
            context=f"The player {player['name']} the {player['class']} is in {location['name']}. They issued the command: '{command}'",
            prompt=f"Respond to the player's command: {command}"
        )
        
        add_game_text(ai_message, "ai")

# Main app logic
def main():
    # Render sidebar
    render_sidebar()
    
    # Render appropriate page based on session state
    if st.session_state.page == "home":
        render_home()
    elif st.session_state.page == "create_character":
        create_character_ui()
    elif st.session_state.page == "load_character":
        load_character_ui()
    elif st.session_state.page == "game":
        render_game()
    elif st.session_state.page == "inventory":
        render_inventory_ui()
    elif st.session_state.page == "quests":
        render_quests()
    elif st.session_state.page == "character":
        render_character()
    elif st.session_state.page == "map":
        render_map()
    elif st.session_state.page == "about":
        render_about()

if __name__ == "__main__":
    main()
