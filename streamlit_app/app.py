import streamlit as st
import os
import sys
from dotenv import load_dotenv
import pymongo
from PIL import Image
import base64
import time
import random
import datetime

# Add parent directory to path to import game modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import game modules
from game.database import connect_to_mongodb
from game.ai_generator import generate_response

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

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = False
    st.session_state.player = None
    st.session_state.current_location = None
    st.session_state.game_text = []
    st.session_state.inventory = []
    st.session_state.quests = []
    st.session_state.in_combat = False
    st.session_state.combat_enemy = None
    st.session_state.page = "home"

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

add_bg_image()

# Connect to MongoDB
try:
    db = connect_to_mongodb()
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
                st.session_state.page = "character"
            
            if st.button("Inventory", key="nav_inventory"):
                st.session_state.page = "inventory"
            
            if st.button("Quests", key="nav_quests"):
                st.session_state.page = "quests"
            
            if st.button("Map", key="nav_map"):
                st.session_state.page = "map"
            
            if st.button("Game", key="nav_game"):
                st.session_state.page = "game"
            
            if st.button("Main Menu", key="nav_home"):
                st.session_state.page = "home"
        else:
            st.info("Create or load a character to begin your adventure!")
            
            if st.button("Create Character", key="create_character_sidebar"):
                st.session_state.page = "create_character"
            
            if st.button("Load Character", key="load_character_sidebar"):
                st.session_state.page = "load_character"
            
            if st.button("About", key="about_sidebar"):
                st.session_state.page = "about"

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
            st.session_state.page = "create_character"
    
    with col2:
        if st.button("Load Character", key="load_character"):
            st.session_state.page = "load_character"
    
    with col3:
        if st.button("About", key="about"):
            st.session_state.page = "about"

# Character creation
def render_character_creation():
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
            # Initialize character stats based on class
            if class_choice == "Warrior":
                stats = {
                    "max_health": 100,
                    "current_health": 100,
                    "attack": 15,
                    "defense": 15,
                    "evasion": 5
                }
            elif class_choice == "Mage":
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
                "class": class_choice,
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
            try:
                result = db.players.insert_one(player)
                player["_id"] = result.inserted_id
                st.session_state.player = player
                st.session_state.page = "game"
                
                # Set starting location
                st.session_state.current_location = db.world.find_one({"id": "town_square"})
                
                # Add welcome message
                ai_message = generate_response(
                    context=f"The player {name} the {class_choice} has just begun their adventure in the town square.",
                    prompt="Generate a welcome message for a new player starting their adventure."
                )
                
                st.session_state.game_text = [{
                    "type": "system",
                    "text": f"Welcome to the world of adventure, {name} the {class_choice}!"
                }, {
                    "type": "ai",
                    "text": ai_message
                }]
                
                st.success("Character created successfully!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error creating character: {e}")
        elif submit:
            st.warning("Please enter a character name.")

# Load character
def render_load_character():
    st.title("Load Character")
    
    try:
        characters = list(db.players.find())
        
        if not characters:
            st.info("No characters found. Create a new one!")
            if st.button("Create New Character"):
                st.session_state.page = "create_character"
            return
        
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
                    st.session_state.player = character
                    st.session_state.current_location = db.world.find_one({"id": character['location']})
                    st.session_state.page = "game"
                    
                    # Load game state
                    st.session_state.inventory = character.get('inventory', [])
                    st.session_state.quests = character.get('quests', [])
                    
                    # Add welcome back message
                    st.session_state.game_text = [{
                        "type": "system",
                        "text": f"Welcome back, {character['name']} the {character['class']}!"
                    }]
                    
                    st.experimental_rerun()
    except Exception as e:
        st.error(f"Error loading characters: {e}")

# Main game interface
def render_game():
    if not st.session_state.player:
        st.warning("No character loaded. Please create or load a character first.")
        if st.button("Return to Home"):
            st.session_state.page = "home"
        return
    
    # Get current location
    location = st.session_state.current_location
    
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
        for entry in st.session_state.game_text[-10:]:  # Show last 10 entries
            if entry["type"] == "system":
                st.info(entry["text"])
            elif entry["type"] == "player":
                st.success(entry["text"])
            elif entry["type"] == "ai":
                st.write(entry["text"])
            elif entry["type"] == "combat":
                st.warning(entry["text"])
    
    # Combat interface
    if st.session_state.in_combat:
        render_combat()
    else:
        # Available actions
        st.subheader("What would you like to do?")
        
        # Command input
        command = st.text_input("Enter a command", key="command_input")
        
        if st.button("Submit", key="submit_command"):
            if command:
                # Process command (simplified for this example)
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
                st.session_state.page = "inventory"
                st.experimental_rerun()
        
        with col3:
            if st.button("View quests"):
                st.session_state.page = "quests"
                st.experimental_rerun()
        
        with col4:
            if st.button("View map"):
                st.session_state.page = "map"
                st.experimental_rerun()
        
        # Location exits
        st.subheader("Available Paths")
        exit_cols = st.columns(len(location.get('exits', [])) or 1)
        
        for i, exit_info in enumerate(location.get('exits', [])):
            with exit_cols[i]:
                if st.button(f"Go to {exit_info['name']}"):
                    # Move to new location
                    new_location = db.world.find_one({"id": exit_info['target']})
                    if new_location:
                        st.session_state.current_location = new_location
                        
                        # Update player location in database
                        db.players.update_one(
                            {"_id": st.session_state.player["_id"]},
                            {"$set": {"location": new_location['id']}}
                        )
                        
                        # Add movement message
                        st.session_state.game_text.append({
                            "type": "system",
                            "text": f"You travel to {new_location['name']}."
                        })
                        
                        # Random encounter check (20% chance)
                        if random.random() < 0.2:
                            trigger_combat()
                        
                        st.experimental_rerun()

# Combat interface
def render_combat():
    enemy = st.session_state.combat_enemy
    
    st.subheader(f"Combat: {enemy['name']}")
    
    # Enemy stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Enemy Health", f"{enemy['current_health']}/{enemy['max_health']}")
    with col2:
        st.metric("Enemy Attack", enemy['attack'])
    with col3:
        st.metric("Enemy Defense", enemy['defense'])
    
    # Combat actions
    st.subheader("Combat Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Attack"):
            combat_round("attack")
            st.experimental_rerun()
    
    with col2:
        if st.button("Defend"):
            combat_round("defend")
            st.experimental_rerun()
    
    with col3:
        if st.button("Use Item"):
            st.session_state.page = "combat_item"
            st.experimental_rerun()
    
    with col4:
        if st.button("Flee"):
            # 50% chance to flee
            if random.random() < 0.5:
                st.session_state.in_combat = False
                st.session_state.combat_enemy = None
                st.session_state.game_text.append({
                    "type": "system",
                    "text": "You successfully fled from combat!"
                })
            else:
                st.session_state.game_text.append({
                    "type": "system",
                    "text": "You failed to flee and the enemy attacks!"
                })
                
                # Enemy gets a free attack
                damage = max(1, enemy['attack'] - st.session_state.player['defense'] // 2)
                st.session_state.player['current_health'] -= damage
                
                st.session_state.game_text.append({
                    "type": "combat",
                    "text": f"The {enemy['name']} hits you for {damage} damage!"
                })
                
                # Update player in database
                db.players.update_one(
                    {"_id": st.session_state.player["_id"]},
                    {"$set": {"current_health": st.session_state.player['current_health']}}
                )
                
                # Check if player died
                check_player_death()
            
            st.experimental_rerun()

# Combat logic
def trigger_combat():
    # Get a random enemy
    enemies = list(db.enemies.find())
    if not enemies:
        return
    
    enemy = random.choice(enemies)
    enemy['current_health'] = enemy['max_health']
    
    st.session_state.in_combat = True
    st.session_state.combat_enemy = enemy
    
    # Add combat start message
    st.session_state.game_text.append({
        "type": "system",
        "text": f"You encounter a {enemy['name']}!"
    })
    
    # AI generated combat intro
    ai_message = generate_response(
        context=f"The player {st.session_state.player['name']} the {st.session_state.player['class']} has encountered a {enemy['name']}.",
        prompt=f"Describe the encounter with the {enemy['name']}."
    )
    
    st.session_state.game_text.append({
        "type": "ai",
        "text": ai_message
    })

def combat_round(player_action):
    player = st.session_state.player
    enemy = st.session_state.combat_enemy
    
    # Player action
    if player_action == "attack":
        # Calculate damage
        damage = max(1, player['attack'] - enemy['defense'] // 2)
        enemy['current_health'] -= damage
        
        st.session_state.game_text.append({
            "type": "combat",
            "text": f"You hit the {enemy['name']} for {damage} damage!"
        })
    elif player_action == "defend":
        # Boost defense for this round
        temp_defense_boost = player['defense'] // 2
        
        st.session_state.game_text.append({
            "type": "system",
            "text": f"You take a defensive stance, increasing your defense by {temp_defense_boost}."
        })
    
    # Check if enemy is defeated
    if enemy['current_health'] <= 0:
        handle_enemy_defeat(enemy)
        return
    
    # Enemy action
    damage = max(1, enemy['attack'] - (player['defense'] + (temp_defense_boost if player_action == "defend" else 0)))
    
    # Check for evasion
    if random.random() * 100 < player['evasion']:
        st.session_state.game_text.append({
            "type": "system",
            "text": f"You dodged the {enemy['name']}'s attack!"
        })
    else:
        player['current_health'] -= damage
        
        st.session_state.game_text.append({
            "type": "combat",
            "text": f"The {enemy['name']} hits you for {damage} damage!"
        })
        
        # Update player in database
        db.players.update_one(
            {"_id": player["_id"]},
            {"$set": {"current_health": player['current_health']}}
        )
        
        # Check if player died
        check_player_death()

def handle_enemy_defeat(enemy):
    # Calculate rewards
    xp_reward = enemy.get('xp_reward', 10)
    gold_reward = enemy.get('gold_reward', 5)
    
    # Update player
    player = st.session_state.player
    player['experience'] += xp_reward
    player['gold'] += gold_reward
    
    # Check for level up
    level_up = check_level_up()
    
    # Update database
    db.players.update_one(
        {"_id": player["_id"]},
        {"$set": {
            "experience": player['experience'],
            "gold": player['gold'],
            "level": player['level']
        }}
    )
    
    # Add victory message
    st.session_state.game_text.append({
        "type": "system",
        "text": f"You defeated the {enemy['name']} and gained {xp_reward} XP and {gold_reward} gold!"
    })
    
    if level_up:
        st.session_state.game_text.append({
            "type": "system",
            "text": f"You leveled up to level {player['level']}!"
        })
    
    # Reset combat state
    st.session_state.in_combat = False
    st.session_state.combat_enemy = None
    
    # AI generated victory message
    ai_message = generate_response(
        context=f"The player {player['name']} the {player['class']} has defeated a {enemy['name']} and gained {xp_reward} XP and {gold_reward} gold.",
        prompt=f"Describe the victory over the {enemy['name']}."
    )
    
    st.session_state.game_text.append({
        "type": "ai",
        "text": ai_message
    })

def check_player_death():
    player = st.session_state.player
    
    if player['current_health'] <= 0:
        player['current_health'] = 0
        
        # Add death message
        st.session_state.game_text.append({
            "type": "system",
            "text": "You have been defeated!"
        })
        
        # Respawn at town square with penalty
        player['current_health'] = player['max_health'] // 2
        player['gold'] = max(0, player['gold'] - player['gold'] // 4)  # Lose 25% of gold
        
        # Update database
        db.players.update_one(
            {"_id": player["_id"]},
            {"$set": {
                "current_health": player['current_health'],
                "gold": player['gold'],
                "location": "town_square"
            }}
        )
        
        # Update game state
        st.session_state.current_location = db.world.find_one({"id": "town_square"})
        st.session_state.in_combat = False
        st.session_state.combat_enemy = None
        
        # Add respawn message
        st.session_state.game_text.append({
            "type": "system",
            "text": "You wake up at the town square with half health and have lost some gold."
        })

def check_level_up():
    player = st.session_state.player
    
    # Simple level up formula: level * 100 XP needed
    xp_needed = player['level'] * 100
    
    if player['experience'] >= xp_needed:
        player['level'] += 1
        
        # Improve stats
        player['max_health'] += 10
        player['current_health'] = player['max_health']  # Heal on level up
        player['attack'] += 3
        player['defense'] += 2
        
        # Update database with new stats
        db.players.update_one(
            {"_id": player["_id"]},
            {"$set": {
                "level": player['level'],
                "max_health": player['max_health'],
                "current_health": player['current_health'],
                "attack": player['attack'],
                "defense": player['defense']
            }}
        )
        
        return True
    
    return False

# Process player commands
def process_command(command):
    command = command.lower()
    
    # Add command to game text
    st.session_state.game_text.append({
        "type": "player",
        "text": f"> {command}"
    })
    
    # Process common commands
    if "look" in command:
        # Generate AI description of the surroundings
        location = st.session_state.current_location
        ai_message = generate_response(
            context=f"The player is in {location['name']}. {location.get('description', '')}",
            prompt="Describe the surroundings in detail."
        )
        
        st.session_state.game_text.append({
            "type": "ai",
            "text": ai_message
        })
    elif "inventory" in command:
        st.session_state.page = "inventory"
    elif "quest" in command:
        st.session_state.page = "quests"
    elif "map" in command:
        st.session_state.page = "map"
    elif "stats" in command or "character" in command:
        st.session_state.page = "character"
    elif any(direction in command for direction in ["north", "south", "east", "west", "go to"]):
        # Handle movement
        location = st.session_state.current_location
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
            new_location = db.world.find_one({"id": target_location})
            if new_location:
                st.session_state.current_location = new_location
                
                # Update player location in database
                db.players.update_one(
                    {"_id": st.session_state.player["_id"]},
                    {"$set": {"location": new_location['id']}}
                )
                
                # Add movement message
                st.session_state.game_text.append({
                    "type": "system",
                    "text": f"You travel to {new_location['name']}."
                })
                
                # Random encounter check (20% chance)
                if random.random() < 0.2:
                    trigger_combat()
        else:
            st.session_state.game_text.append({
                "type": "system",
                "text": "You can't go that way."
            })
    else:
        # Use AI to process other commands
        location = st.session_state.current_location
        player = st.session_state.player
        
        ai_message = generate_response(
            context=f"The player {player['name']} the {player['class']} is in {location['name']}. They issued the command: '{command}'",
            prompt=f"Respond to the player's command: {command}"
        )
        
        st.session_state.game_text.append({
            "type": "ai",
            "text": ai_message
        })

# Inventory page
def render_inventory():
    st.title("Inventory")
    
    player = st.session_state.player
    
    # Show gold
    st.subheader(f"Gold: {player.get('gold', 0)}")
    
    # Get inventory items
    inventory = player.get('inventory', [])
    
    if not inventory:
        st.info("Your inventory is empty.")
    else:
        # Group items by type
        weapons = [item for item in inventory if item.get('type') == 'weapon']
        armor = [item for item in inventory if item.get('type') == 'armor']
        consumables = [item for item in inventory if item.get('type') == 'consumable']
        other = [item for item in inventory if item.get('type') not in ['weapon', 'armor', 'consumable']]
        
        # Create tabs for item categories
        tabs = st.tabs(["All Items", "Weapons", "Armor", "Consumables", "Other"])
        
        with tabs[0]:
            render_item_list(inventory, "all")
        
        with tabs[1]:
            render_item_list(weapons, "weapon")
        
        with tabs[2]:
            render_item_list(armor, "armor")
        
        with tabs[3]:
            render_item_list(consumables, "consumable")
        
        with tabs[4]:
            render_item_list(other, "other")
    
    if st.button("Return to Game"):
        st.session_state.page = "game"

def render_item_list(items, item_type):
    if not items:
        st.info(f"No {item_type} items in inventory.")
        return
    
    for item in items:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div class="item-card">
                <h3>{item.get('name', 'Unknown Item')}</h3>
                <p>{item.get('description', '')}</p>
                <p><small>{item_type_description(item)}</small></p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if item.get('type') == 'weapon' or item.get('type') == 'armor':
                if st.button("Equip", key=f"equip_{item.get('id', '')}"):
                    equip_item(item)
            
            if item.get('type') == 'consumable':
                if st.button("Use", key=f"use_{item.get('id', '')}"):
                    use_item(item)
            
            if st.button("Drop", key=f"drop_{item.get('id', '')}"):
                drop_item(item)

def item_type_description(item):
    item_type = item.get('type', 'item')
    
    if item_type == 'weapon':
        return f"Weapon | Attack: +{item.get('attack_bonus', 0)}"
    elif item_type == 'armor':
        return f"Armor | Defense: +{item.get('defense_bonus', 0)}"
    elif item_type == 'consumable':
        effects = []
        if 'health_restore' in item:
            effects.append(f"Restores {item['health_restore']} health")
        
        return f"Consumable | {', '.join(effects)}"
    else:
        return "Miscellaneous item"

def equip_item(item):
    player = st.session_state.player
    
    # Update equipped items
    if 'equipped' not in player:
        player['equipped'] = {}
    
    item_type = item.get('type')
    player['equipped'][item_type] = item
    
    # Update stats
    if item_type == 'weapon':
        player['attack'] += item.get('attack_bonus', 0)
    elif item_type == 'armor':
        player['defense'] += item.get('defense_bonus', 0)
    
    # Update player in database
    db.players.update_one(
        {"_id": player["_id"]},
        {"$set": {
            "equipped": player['equipped'],
            "attack": player['attack'],
            "defense": player['defense']
        }}
    )
    
    st.success(f"You equipped {item.get('name')}!")
    time.sleep(1)
    st.experimental_rerun()

def use_item(item):
    player = st.session_state.player
    
    # Apply item effects
    if 'health_restore' in item:
        player['current_health'] = min(player['max_health'], player['current_health'] + item['health_restore'])
        
        # Add message to game text
        st.session_state.game_text.append({
            "type": "system",
            "text": f"You used {item.get('name')} and restored {item['health_restore']} health."
        })
    
    # Remove item from inventory
    player['inventory'].remove(item)
    
    # Update player in database
    db.players.update_one(
        {"_id": player["_id"]},
        {"$set": {
            "current_health": player['current_health'],
            "inventory": player['inventory']
        }}
    )
    
    st.success(f"You used {item.get('name')}!")
    time.sleep(1)
    st.experimental_rerun()

def drop_item(item):
    player = st.session_state.player
    
    # Remove item from inventory
    player['inventory'].remove(item)
    
    # Update player in database
    db.players.update_one(
        {"_id": player["_id"]},
        {"$set": {"inventory": player['inventory']}}
    )
    
    # Add message to game text
    st.session_state.game_text.append({
        "type": "system",
        "text": f"You dropped {item.get('name')}."
    })
    
    st.success(f"You dropped {item.get('name')}!")
    time.sleep(1)
    st.experimental_rerun()

# Quest page
def render_quests():
    st.title("Quest Journal")
    
    player = st.session_state.player
    
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
        st.session_state.page = "game"

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
    st.title("Character Sheet")
    
    player = st.session_state.player
    
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
        st.session_state.page = "game"

# World map
def render_map():
    st.title("World Map")
    
    # Get all locations
    try:
        locations = list(db.world.find())
        
        if not locations:
            st.info("No locations found.")
            return
        
        # Map legend
        st.markdown("""
        <div class="map-legend" style="display: flex; justify-content: center; margin-bottom: 15px;">
            <div style="margin: 0 10px; display: flex; align-items: center;">
                <div style="background-color: #4a2511; width: 20px; height: 20px; margin-right: 5px; border-radius: 3px;"></div>
                <span>Current Location</span>
            </div>
            <div style="margin: 0 10px; display: flex; align-items: center;">
                <div style="background-color: #8b5a2b; width: 20px; height: 20px; margin-right: 5px; border-radius: 3px;"></div>
                <span>Accessible Location</span>
            </div>
            <div style="margin: 0 10px; display: flex; align-items: center;">
                <div style="background-color: #a9a9a9; width: 20px; height: 20px; margin-right: 5px; border-radius: 3px;"></div>
                <span>Inaccessible Location</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Simplified map view
        st.write("Click on a location to travel there:")
        
        # Create a grid of locations
        cols = st.columns(3)
        current_location_id = st.session_state.current_location['id']
        
        for i, location in enumerate(locations):
            with cols[i % 3]:
                is_current = location['id'] == current_location_id
                
                # Determine if the location is accessible
                is_accessible = False
                
                if is_current:
                    is_accessible = True
                else:
                    # Check if this location is connected to the current location
                    for exit_info in st.session_state.current_location.get('exits', []):
                        if exit_info['target'] == location['id']:
                            is_accessible = True
                            break
                
                # Display location with icons and better styling
                background_color = "#4a2511" if is_current else ("#8b5a2b" if is_accessible else "#a9a9a9")
                
                # Determine location type icon
                location_type = location.get('type', 'wilderness')
                icon = "🏰" if location_type == 'town' else "🌲" if location_type == 'forest' else "🏚️" if location_type == 'ruins' else "🗻" if location_type == 'mountain' else "🌄"
                
                # Enhanced location card with icon and description
                st.markdown(f"""
                <div style="background-color: {background_color}; color: white; padding: 10px; border-radius: 5px; margin: 5px; text-align: center; height: 120px; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <h3 style="margin: 0;">{icon} {location['name']}</h3>
                        <p style="font-size: 0.8em; margin-top: 5px; height: 40px; overflow: hidden;">{location.get('short_desc', '')}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Add travel button if accessible
                if is_accessible and not is_current:
                    if st.button(f"Travel to {location['name']}", key=f"travel_{location['id']}"):
                        # Move to new location
                        st.session_state.current_location = location
                        
                        # Update player location in database
                        db.players.update_one(
                            {"_id": st.session_state.player["_id"]},
                            {"$set": {"location": location['id']}}
                        )
                        
                        # Add movement message
                        st.session_state.game_text.append({
                            "type": "system",
                            "text": f"You travel to {location['name']}."
                        })
                        
                        # Random encounter check (20% chance)
                        if random.random() < 0.2:
                            trigger_combat()
                        
                        st.session_state.page = "game"
                        st.experimental_rerun()
                elif is_current:
                    st.info("You are here")
                else:
                    st.write("Not accessible from current location")
        
        # Add current location details at the bottom
        current_loc = st.session_state.current_location
        st.markdown("---")
        st.subheader(f"Current Location: {current_loc['name']}")
        st.write(current_loc.get('description', 'No description available.'))
        
        # Show available exits
        if 'exits' in current_loc and current_loc['exits']:
            st.write("Available exits:")
            exit_cols = st.columns(len(current_loc['exits']))
            for i, exit_info in enumerate(current_loc['exits']):
                exit_loc = db.world.find_one({"id": exit_info['target']})
                if exit_loc:
                    with exit_cols[i]:
                        st.write(f"• {exit_info['direction']}: {exit_loc['name']}")
        else:
            st.write("No available exits.")
    
    except Exception as e:
        st.error(f"Error loading map: {e}")
    
    if st.button("Return to Game", key="map_return_button"):
        st.session_state.page = "game"

# About page
def render_about():
    st.title("About Fantasy RPG")
    
    # Game logo or banner could go here
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="color: #8b5a2b; font-family: 'MedievalSharp', cursive;">🏰 Fantasy RPG Text Adventure 🏰</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Game description
    st.markdown("""
    <div class="game-container">
        <p>Welcome to our fantasy text adventure game combining traditional RPG mechanics with modern technologies.
        Embark on an epic journey through a medieval fantasy world filled with danger, treasure, and adventure!</p>
        
        <h3>🎮 Key Features:</h3>
        <ul>
            <li><strong>Character Creation:</strong> Choose from different classes like Warrior, Mage, and Rogue, each with unique abilities and playstyles.</li>
            <li><strong>Combat System:</strong> Strategic turn-based combat against various enemies including goblins, wolves, bandits, and powerful bosses.</li>
            <li><strong>Quest System:</strong> Complete quests for NPCs to earn rewards and uncover the world's secrets.</li>
            <li><strong>Inventory Management:</strong> Collect, equip, and manage weapons, armor, and consumable items to strengthen your character.</li>
            <li><strong>World Exploration:</strong> Discover diverse locations including towns, forests, ruins, and dungeons.</li>
            <li><strong>Dynamic Content:</strong> AI-powered descriptions and encounters that create a unique experience with each playthrough.</li>
        </ul>
        
        <h3>💻 Technical Details:</h3>
        <ul>
            <li><strong>Front-end:</strong> Built with Python and Streamlit</li>
            <li><strong>Database:</strong> MongoDB for data persistence</li>
            <li><strong>AI Generation:</strong> Google Gemini AI for dynamic content generation</li>
            <li><strong>Theming:</strong> Custom CSS for immersive medieval fantasy styling</li>
        </ul>
        
        <h3>👥 How to Play:</h3>
        <ol>
            <li>Create a new character or load an existing one</li>
            <li>Explore the world by traveling between locations</li>
            <li>Talk to NPCs and accept quests</li>
            <li>Fight enemies to gain experience and gold</li>
            <li>Buy, find, or craft items to strengthen your character</li>
            <li>Level up your character's abilities</li>
        </ol>
        
        <h3>🏆 Game Goals:</h3>
        <p>
            Your ultimate goal is to become a legendary hero by completing all quests, 
            defeating powerful bosses, and collecting rare items while exploring every corner of the world.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Credits
    st.markdown("""
    <div class="game-container" style="margin-top: 20px; text-align: center;">
        <h3>Credits</h3>
        <p>Created for a database management systems project</p>
        <p>Made with ❤️ and MongoDB</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Return to Home", key="about_return_button"):
        st.session_state.page = "home"

# Save and load game functions
def save_game():
    """Save the current game state"""
    if 'player' not in st.session_state:
        st.error("No active game to save")
        return
    
    try:
        player = st.session_state.player
        
        # Create a save_games collection if it doesn't exist
        if 'save_games' not in db.list_collection_names():
            db.create_collection('save_games')
        
        # Save data with timestamp
        save_time = datetime.datetime.now()
        save_name = f"{player['name']}_{save_time.strftime('%Y%m%d_%H%M%S')}"
        
        save_data = {
            "save_id": save_name,
            "player_id": player['_id'],
            "player_name": player['name'],
            "player_class": player['class'],
            "player_level": player['level'],
            "timestamp": save_time,
            "location": st.session_state.current_location['id'],
            "game_text": st.session_state.game_text[-10:] if len(st.session_state.game_text) > 10 else st.session_state.game_text  # Save last 10 messages
        }
        
        db.save_games.insert_one(save_data)
        
        st.success(f"Game saved successfully as '{save_name}'")
        
        # Add message to game text
        st.session_state.game_text.append({
            "type": "system",
            "text": "Game saved successfully."
        })
        
    except Exception as e:
        st.error(f"Error saving game: {e}")

def load_game_ui():
    """UI for loading a saved game"""
    st.title("Load Game")
    
    try:
        # Get all save games
        saves = list(db.save_games.find().sort("timestamp", -1))  # Most recent first
        
        if not saves:
            st.info("No saved games found.")
            if st.button("Return to Home"):
                st.session_state.page = "home"
            return
        
        st.write("Select a saved game to load:")
        
        for save in saves:
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"**{save['player_name']}** (Level {save['player_level']} {save['player_class']})")
            
            with col2:
                save_time = save['timestamp']
                st.write(f"Saved on: {save_time.strftime('%Y-%m-%d %H:%M')}")
            
            with col3:
                if st.button("Load", key=f"load_{save['save_id']}"):
                    load_game(save)
        
        if st.button("Return to Home", key="load_return"):
            st.session_state.page = "home"
    
    except Exception as e:
        st.error(f"Error loading games: {e}")

def load_game(save_data):
    """Load a saved game"""
    try:
        # Get the player data
        player = db.players.find_one({"_id": save_data['player_id']})
        
        if not player:
            st.error("Player data not found.")
            return
        
        # Get the location data
        location = db.world.find_one({"id": save_data['location']})
        
        if not location:
            st.error("Location data not found.")
            return
        
        # Set up session state
        st.session_state.player = player
        st.session_state.current_location = location
        
        # Initialize or restore game text
        if 'game_text' in save_data:
            st.session_state.game_text = save_data['game_text']
        else:
            st.session_state.game_text = []
        
        # Add load message
        st.session_state.game_text.append({
            "type": "system",
            "text": f"Game loaded successfully. Welcome back, {player['name']}!"
        })
        
        # Reset combat state
        st.session_state.in_combat = False
        st.session_state.combat_enemy = None
        
        # Switch to game page
        st.session_state.page = "game"
        st.experimental_rerun()
    
    except Exception as e:
        st.error(f"Error loading game: {e}")

# Main app logic
def main():
    # Render sidebar
    render_sidebar()
    
    # Render appropriate page based on session state
    if st.session_state.page == "home":
        render_home()
    elif st.session_state.page == "create_character":
        render_character_creation()
    elif st.session_state.page == "load_character":
        render_load_character()
    elif st.session_state.page == "game":
        render_game()
    elif st.session_state.page == "inventory":
        render_inventory()
    elif st.session_state.page == "quests":
        render_quests()
    elif st.session_state.page == "character":
        render_character()
    elif st.session_state.page == "map":
        render_map()
    elif st.session_state.page == "about":
        render_about()
    elif st.session_state.page == "save_load":
        load_game_ui()

if __name__ == "__main__":
    main()
