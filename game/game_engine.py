"""
Game Engine module for the Fantasy RPG text adventure game.
Handles core game mechanics and logic.
"""

import random
import time
from datetime import datetime

from game.database import Database
from game.ai_generator import AIGenerator

class GameEngine:
    """Core game engine for the Fantasy RPG text adventure."""
    
    def __init__(self):
        """Initialize the game engine."""
        self.db = Database()
        self.ai = AIGenerator()
        
        # Initialize game data if needed
        self.db.initialize_game_data()
        
        # Current game state
        self.current_player = None
        self.current_location = None
        self.game_state = {
            "active_quests": [],
            "available_quests": [],
            "nearby_enemies": [],
            "last_action": None,
            "last_combat": None,
            "last_command": None
        }
    
    def create_new_player(self, name, player_class):
        """Create a new player character."""
        valid_classes = ["warrior", "mage", "rogue"]
        if player_class.lower() not in valid_classes:
            return False, f"Invalid class. Please choose from: {', '.join(valid_classes)}"
        
        # Check if player name already exists
        existing_player = self.db.get_player_by_name(name)
        if existing_player:
            return False, "A character with that name already exists."
        
        # Create base stats based on class
        stats = self._generate_base_stats(player_class.lower())
        
        # Create player data
        player_data = {
            "name": name,
            "class": player_class.lower(),
            "level": 1,
            "xp": 0,
            "health": stats["max_health"],
            "max_health": stats["max_health"],
            "mana": stats.get("max_mana", 0),
            "max_mana": stats.get("max_mana", 0),
            "stats": stats,
            "gold": 10,
            "inventory": {"potion_health": 2},
            "equipment": {},
            "quests": {},
            "visited_locations": {"village_start": datetime.now()},
            "choices": [],
            "created_at": datetime.now(),
            "last_played": datetime.now()
        }
        
        # Save player to database
        player_id = self.db.create_player(player_data)
        
        # Load the player
        self.load_player(player_id)
        
        return True, f"Created new character: {name} the {player_class}"
    
    def load_player(self, player_id):
        """Load a player character."""
        player_data = self.db.get_player(player_id)
        if not player_data:
            return False, "Player not found."
        
        self.current_player = player_data
        
        # Update last played timestamp
        self.db.update_player(player_id, {"last_played": datetime.now()})
        
        # Load the most recently visited location or default to starting location
        visited_locations = self.current_player.get("visited_locations", {})
        
        if visited_locations:
            # Find the most recently visited location
            most_recent_location = None
            most_recent_time = None
            
            for location_id, visit_time in visited_locations.items():
                if most_recent_time is None or visit_time > most_recent_time:
                    most_recent_location = location_id
                    most_recent_time = visit_time
            
            if most_recent_location:
                self.current_location = self.db.get_location(most_recent_location)
            else:
                # Fallback to default starting location
                self.current_location = self.db.get_location("village_start")
        else:
            # If no visited locations, use default starting location
            self.current_location = self.db.get_location("village_start")
        
        # Update game state
        self._update_game_state()
        
        return True, f"Loaded character: {player_data['name']} (Level {player_data['level']} {player_data['class']})\nYou are currently in {self.current_location['name']}."
    
    def load_player_by_name(self, name):
        """Load a player character by name."""
        player_data = self.db.get_player_by_name(name)
        if not player_data:
            return False, "Player not found."
        
        return self.load_player(player_data["_id"])
        
    def delete_player_by_name(self, name):
        """Delete a player character by name."""
        player_data = self.db.get_player_by_name(name)
        if not player_data:
            return False, "Player not found."
        
        # Delete the player from the database
        result = self.db.delete_player(player_data["_id"])
        
        # Reset current player if it's the one being deleted
        if self.current_player and self.current_player["name"] == name:
            self.current_player = None
            self.current_location = None
            self.game_state = {
                "active_quests": [],
                "available_quests": [],
                "nearby_enemies": [],
                "last_action": None,
                "last_combat": None
            }
        
        if result and result.deleted_count > 0:
            return True, f"Character '{name}' has been deleted."
        else:
            return False, f"Failed to delete character '{name}'."
            
    def list_all_characters(self):
        """Get a list of all characters in the database."""
        players = self.db.get_all_players()
        
        if not players:
            return False, "No characters found in the database."
            
        return True, players
    
    def get_location_description(self):
        """Get the description of the current location."""
        if not self.current_location or not self.current_player:
            return "You are nowhere. The void surrounds you."
        
        # Mark location as visited
        if self.current_location["_id"] not in self.current_player.get("visited_locations", {}):
            self.db.update_player(
                self.current_player["_id"],
                {f"visited_locations.{self.current_location['_id']}": datetime.now()}
            )
            self.current_player["visited_locations"][self.current_location["_id"]] = datetime.now()
        
        # Generate AI description
        description = self.ai.generate_location_description(
            self.current_location,
            self.current_player
        )
        
        # Add available connections
        connections = []
        for conn_id in self.current_location.get("connections", []):
            conn_location = self.db.get_location(conn_id)
            if conn_location:
                connections.append(f"- {conn_location['name']}")
        
        if connections:
            description += "\n\nPaths lead to:\n" + "\n".join(connections)
        
        # Add available quests
        if self.game_state["available_quests"]:
            quest_givers = []
            for quest in self.game_state["available_quests"]:
                quest_givers.append(f"- {quest['name']} (from {quest['giver']})")
            
            description += "\n\nAvailable quests:\n" + "\n".join(quest_givers)
        
        return description
    
    def move_to_location(self, location_name):
        """Move the player to a new location."""
        if not self.current_player or not self.current_location:
            return False, "No active player or location."
        
        # Find the location by name
        target_location = None
        for conn_id in self.current_location.get("connections", []):
            conn_location = self.db.get_location(conn_id)
            if conn_location and conn_location["name"].lower() == location_name.lower():
                target_location = conn_location
                break
        
        if not target_location:
            return False, f"Cannot find a path to {location_name} from your current location."
        
        # Check for random encounter
        encounter = self._check_for_encounter(target_location)
        
        # Update current location
        self.current_location = target_location
        
        # Update visited locations with current timestamp
        current_time = datetime.now()
        self.db.update_player(
            self.current_player["_id"],
            {f"visited_locations.{target_location['_id']}": current_time}
        )
        
        # Also update the in-memory player data
        if "visited_locations" not in self.current_player:
            self.current_player["visited_locations"] = {}
        self.current_player["visited_locations"][target_location["_id"]] = current_time
        
        # Update game state
        self._update_game_state()
        
        if encounter:
            return True, f"You travel to {target_location['name']}.\n\n{encounter}"
        
        return True, f"You travel to {target_location['name']}."
    
    def process_command(self, command):
        """Process a player command."""
        if not self.current_player:
            return "No active player. Please create or load a character first."
        
        # Check if command is None or empty
        if command is None:
            return "Please enter a command."
            
        # Split the command into parts
        parts = command.lower().split()
        if not parts:
            return "Please enter a command."
        
        # Process the command based on the first word
        action = parts[0]
        
        # Movement commands
        if action in ["go", "move", "travel"]:
            if len(parts) < 2:
                return "Go where? Please specify a location."
            
            location_name = " ".join(parts[1:])
            success, message = self.move_to_location(location_name)
            return message
        
        # Look command
        elif action in ["look", "examine", "inspect"]:
            if len(parts) == 1:
                return self.get_location_description()
            
            target = " ".join(parts[1:])
            return self._examine_target(target)
        
        # Inventory command
        elif action in ["inventory", "items", "i"]:
            return self._show_inventory()
        
        # Status command
        elif action in ["status", "stats", "character"]:
            return self._show_character_status()
        
        # Quest command
        elif action in ["quest", "quests"]:
            return self._show_quests()
        
        # Talk command
        elif action in ["talk", "speak"]:
            if len(parts) < 2:
                return "Talk to whom? Please specify an NPC."
            
            npc_name = " ".join(parts[1:])
            return self._talk_to_npc(npc_name)
        
        # Use item command
        elif action in ["use", "consume"]:
            if len(parts) < 2:
                return "Use what? Please specify an item."
            
            item_name = " ".join(parts[1:])
            return self._use_item(item_name)
        
        # Attack command
        elif action in ["attack", "fight"]:
            if len(parts) < 2:
                return "Attack what? Please specify a target."
            
            target_name = " ".join(parts[1:])
            return self._initiate_combat(target_name)
        
        # Map command
        elif action in ["map", "routes", "where"]:
            return self._show_map()
            
        # Help command
        elif action in ["help", "commands"]:
            return self._show_help()
        
        # If no specific command is recognized, check if it's a repeat command
        last_command = self.game_state.get("last_command", "")
        if last_command and command.lower() == last_command.lower():
            # If it's a repeat command, suggest help
            return "I'm not sure how to process that command. Try something different or type 'help' for a list of commands."
        
        # Store the current command to check for loops in future calls
        self.game_state["last_command"] = command
        
        # Get available items in the current location
        available_items = []
        if hasattr(self.current_location, 'items'):
            available_items = self.current_location.get('items', [])
        
        # Enrich the player data with more context
        enriched_player = self.current_player.copy()
        
        # Add visited locations if not present
        if 'visited_locations' not in enriched_player:
            enriched_player['visited_locations'] = {}
        
        # Add current location to visited locations
        if self.current_location and '_id' in self.current_location:
            enriched_player['visited_locations'][self.current_location['_id']] = True
        
        # Use AI to generate a response for unrecognized commands
        try:
            ai_response = self.ai.generate_response_to_action(
                enriched_player,
                command,
                self.current_location,
                self.game_state
            )
            return ai_response
        except Exception as e:
            # Fallback if AI fails
            print(f"AI response generation failed: {e}")
            return "I don't understand that command. Type 'help' for a list of available commands."
    
    def _generate_base_stats(self, player_class):
        """Generate base stats for a new character based on class."""
        if player_class == "warrior":
            return {
                "strength": 5,
                "dexterity": 3,
                "intelligence": 2,
                "max_health": 100,
                "attack": 5,
                "defense": 5
            }
        elif player_class == "mage":
            return {
                "strength": 2,
                "dexterity": 3,
                "intelligence": 5,
                "max_health": 70,
                "max_mana": 100,
                "attack": 3,
                "defense": 2,
                "magic": 5
            }
        elif player_class == "rogue":
            return {
                "strength": 3,
                "dexterity": 5,
                "intelligence": 3,
                "max_health": 80,
                "attack": 4,
                "defense": 3,
                "stealth": 5
            }
        
        # Default stats if class is not recognized
        return {
            "strength": 3,
            "dexterity": 3,
            "intelligence": 3,
            "max_health": 80,
            "attack": 3,
            "defense": 3
        }
    
    def _update_game_state(self):
        """Update the current game state based on location and player."""
        if not self.current_player or not self.current_location:
            return
        
        # Update available quests
        self.game_state["available_quests"] = self.db.get_available_quests(
            self.current_location["_id"],
            self.current_player["level"]
        )
        
        # Update nearby enemies based on location
        self.game_state["nearby_enemies"] = self.current_location.get("enemies", [])
    
    def _check_for_encounter(self, location):
        """Check for random encounters when moving to a new location."""
        if location.get("danger_level", 0) == 0:
            return None  # Safe location, no encounters
        
        # Chance of encounter based on danger level
        encounter_chance = location.get("danger_level", 0) * 10
        if random.randint(1, 100) <= encounter_chance:
            # Random encounter!
            if "enemies" in location and location["enemies"]:
                enemy_type = random.choice(location["enemies"])
                return f"As you travel, you encounter a {enemy_type}!"
        
        return None
    
    def _examine_target(self, target):
        """Examine a specific target in the current location."""
        # This is a placeholder - in a full implementation, you would check
        # for NPCs, items, or features in the current location
        return f"You examine the {target}, but don't notice anything special."
    
    def _show_inventory(self):
        """Show the player's inventory."""
        if not self.current_player:
            return "No active player."
        
        inventory = self.current_player.get("inventory", {})
        if not inventory:
            return "Your inventory is empty."
        
        result = "Inventory:\n"
        for item_id, quantity in inventory.items():
            item_data = self.db.get_item(item_id)
            if item_data:
                result += f"- {item_data['name']} (x{quantity}): {item_data['description']}\n"
            else:
                result += f"- Unknown item (x{quantity})\n"
        
        result += f"\nGold: {self.current_player.get('gold', 0)}"
        return result
    
    def _show_character_status(self):
        """Show the player's character status."""
        if not self.current_player:
            return "No active player."
        
        player = self.current_player
        result = f"Character: {player['name']} (Level {player['level']} {player['class']})\n"
        result += f"Health: {player['health']}/{player['max_health']}\n"
        
        if "max_mana" in player:
            result += f"Mana: {player.get('mana', 0)}/{player['max_mana']}\n"
        
        result += f"XP: {player.get('xp', 0)}\n"
        result += "\nStats:\n"
        
        for stat, value in player.get("stats", {}).items():
            if stat not in ["max_health", "max_mana"]:
                result += f"- {stat.capitalize()}: {value}\n"
        
        return result
    
    def _show_quests(self):
        """Show the player's active quests."""
        if not self.current_player:
            return "No active player."
        
        active_quests = self.current_player.get("quests", {})
        if not active_quests:
            return "You don't have any active quests."
        
        result = "Active Quests:\n"
        for quest_id, status in active_quests.items():
            quest_data = self.db.get_quest(quest_id)
            if quest_data:
                result += f"- {quest_data['name']}: {status}\n"
                result += f"  {quest_data['description']}\n"
        
        return result
    
    def _talk_to_npc(self, npc_name):
        """Talk to an NPC in the current location."""
        # This is a placeholder - in a full implementation, you would check
        # for NPCs in the current location and generate dialogue
        return f"You try to talk to {npc_name}, but they don't seem to be here."
    
    def _use_item(self, item_name):
        """Use an item from the player's inventory."""
        # This is a placeholder - in a full implementation, you would check
        # the player's inventory and apply item effects
        return f"You try to use {item_name}, but nothing happens."
    
    def _initiate_combat(self, target_name):
        """Initiate combat with a target."""
        # This is a placeholder - in a full implementation, you would check
        # for enemies in the current location and start combat
        return f"You prepare to fight {target_name}, but they're not here."
    
    def _show_map(self):
        """Show current location and available routes."""
        if not self.current_location or not self.current_player:
            return "You are nowhere. The void surrounds you."
        
        # Get current location name
        location_name = self.current_location.get("name", "Unknown")
        
        # Build the response
        response = f"You are currently in: {location_name}\n"
        
        # Add available connections
        connections = []
        for conn_id in self.current_location.get("connections", []):
            conn_location = self.db.get_location(conn_id)
            if conn_location:
                connections.append(f"- {conn_location['name']}")
        
        if connections:
            response += "\nAvailable routes:\n" + "\n".join(connections)
        else:
            response += "\nThere are no obvious exits from here."
            
        return response
        
    def _show_help(self):
        """Show available commands."""
        help_text = """
Available Commands:
- go/move/travel [location]: Move to a new location
- look/examine/inspect [target]: Look around or examine something specific
- map/routes/where: Show your current location and available routes
- inventory/items/i: Check your inventory
- status/stats/character: Check your character status
- quest/quests: Check your active quests
- talk/speak [npc]: Talk to an NPC
- use/consume [item]: Use an item from your inventory
- attack/fight [target]: Initiate combat with an enemy
- help/commands: Show this help message
- quit/exit/menu: Return to the main menu

Examples:
- "go town square"
- "look around"
- "examine chest"
- "talk to merchant"
- "use health potion"
- attack/fight [target]: Attack a target
- help/commands: Show this help message

You can also try other actions not listed here, and the game will respond accordingly.
"""
        return help_text