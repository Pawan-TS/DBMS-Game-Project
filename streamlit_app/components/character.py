import streamlit as st
import random
from utils.database import save_player_data
from utils.session import set_player, add_game_text, set_page
from utils.ai_helper import generate_command_response

def create_character_ui():
    """
    Render the character creation UI.
    """
    st.title("Create Your Character")
    
    with st.form("character_creation_form"):
        name = st.text_input("Character Name")
        
        st.subheader("Choose Your Class")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="class-card" id="warrior">
                <h3>Warrior</h3>
                <p>Strong and resilient fighters specializing in physical combat.</p>
                <ul>
                    <li>High Health</li>
                    <li>Strong Attack</li>
                    <li>Good Defense</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="class-card" id="mage">
                <h3>Mage</h3>
                <p>Masters of arcane magic with powerful spells.</p>
                <ul>
                    <li>Medium Health</li>
                    <li>Very High Attack</li>
                    <li>Low Defense</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="class-card" id="rogue">
                <h3>Rogue</h3>
                <p>Agile and stealthy characters with high evasion.</p>
                <ul>
                    <li>Medium Health</li>
                    <li>Medium Attack</li>
                    <li>Medium Defense</li>
                    <li>High Chance to Evade</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        class_choice = st.radio(
            "Select your class:",
            options=["Warrior", "Mage", "Rogue"],
            horizontal=True
        )
        
        submit = st.form_submit_button("Begin Adventure")
        
        if submit and name:
            return create_character(name, class_choice)
        elif submit:
            st.warning("Please enter a character name.")
    
    return None

def create_character(name, character_class):
    """
    Create a new character with the given name and class.
    
    Args:
        name: Character name
        character_class: Character class (Warrior, Mage, Rogue)
        
    Returns:
        dict: New player data or None if creation failed
    """
    try:
        db = st.session_state.db
        
        # Initialize character stats based on class
        if character_class == "Warrior":
            stats = {
                "max_health": 100,
                "current_health": 100,
                "attack": 15,
                "defense": 15,
                "evasion": 5
            }
        elif character_class == "Mage":
            stats = {
                "max_health": 70,
                "current_health": 70,
                "attack": 25,
                "defense": 5,
                "evasion": 10
            }
        else:  # Rogue
            stats = {
                "max_health": 80,
                "current_health": 80,
                "attack": 15,
                "defense": 10,
                "evasion": 20
            }
        
        # Create character document
        player = {
            "name": name,
            "class": character_class,
            "level": 1,
            "experience": 0,
            "gold": 10,
            "inventory": [],
            "equipped": {},
            "quests": [],
            "location": "town_square",  # Starting location
            **stats
        }
        
        # Save to database
        result = db.players.insert_one(player)
        player["_id"] = result.inserted_id
        
        # Set in session state
        set_player(player)
        
        # Set starting location
        st.session_state.current_location = db.world.find_one({"id": "town_square"})
        
        # Add welcome message
        from game.ai_generator import generate_response
        
        ai_message = generate_response(
            context=f"The player {name} the {character_class} has just begun their adventure in the town square.",
            prompt="Generate a welcome message for a new player starting their adventure."
        )
        
        add_game_text(f"Welcome to the world of adventure, {name} the {character_class}!")
        add_game_text(ai_message, "ai")
        
        # Set game page
        set_page("game")
        
        return player
    except Exception as e:
        st.error(f"Error creating character: {e}")
        return None

def load_character_ui():
    """
    Render the character loading UI.
    """
    st.title("Load Character")
    
    try:
        db = st.session_state.db
        characters = list(db.players.find())
        
        if not characters:
            st.info("No characters found. Create a new one!")
            if st.button("Create New Character"):
                set_page("create_character")
            return None
        
        for character in characters:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="character-card">
                    <h3>{character['name']} the {character['class']}</h3>
                    <p>Level {character.get('level', 1)} | Gold: {character.get('gold', 0)}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("Load", key=f"load_{character['_id']}"):
                    return load_character(character)
    except Exception as e:
        st.error(f"Error loading characters: {e}")
    
    return None

def load_character(character):
    """
    Load an existing character.
    
    Args:
        character: Character data dictionary
        
    Returns:
        dict: Loaded player data
    """
    try:
        db = st.session_state.db
        
        # Set player data in session state
        set_player(character)
        
        # Set current location
        st.session_state.current_location = db.world.find_one({"id": character['location']})
        
        # Set game state
        st.session_state.inventory = character.get('inventory', [])
        st.session_state.quests = character.get('quests', [])
        
        # Add welcome back message
        add_game_text(f"Welcome back, {character['name']} the {character['class']}!")
        
        # Set game page
        set_page("game")
        
        return character
    except Exception as e:
        st.error(f"Error loading character: {e}")
        return None
