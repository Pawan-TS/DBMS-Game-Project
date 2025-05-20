"""
Database module for the Fantasy RPG text adventure game.
Handles all MongoDB operations.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId

# Load environment variables
load_dotenv()

# Get MongoDB connection string from environment variables
MONGODB_URI = os.getenv("MONGODB_URI")

class Database:
    """MongoDB database connection and operations."""
    
    def __init__(self):
        """Initialize database connection."""
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client["fantasy_rpg"]
        
        # Collections
        self.players = self.db["players"]
        self.items = self.db["items"]
        self.quests = self.db["quests"]
        self.world = self.db["world"]
        
    def create_player(self, player_data):
        """Create a new player in the database."""
        return self.players.insert_one(player_data).inserted_id
    
    def get_player(self, player_id):
        """Get player data by ID."""
        return self.players.find_one({"_id": ObjectId(player_id)})
    
    def get_player_by_name(self, name):
        """Get player data by name."""
        return self.players.find_one({"name": name})
    
    def update_player(self, player_id, update_data):
        """Update player data."""
        return self.players.update_one(
            {"_id": ObjectId(player_id)},
            {"$set": update_data}
        )
    
    def update_player_inventory(self, player_id, item_id, quantity=1, remove=False):
        """Add or remove items from player inventory."""
        if remove:
            return self.players.update_one(
                {"_id": ObjectId(player_id)},
                {"$inc": {f"inventory.{item_id}": -quantity}}
            )
        else:
            return self.players.update_one(
                {"_id": ObjectId(player_id)},
                {"$inc": {f"inventory.{item_id}": quantity}}
            )
    
    def update_player_progress(self, player_id, quest_id, status):
        """Update player quest progress."""
        return self.players.update_one(
            {"_id": ObjectId(player_id)},
            {"$set": {f"quests.{quest_id}": status}}
        )
    
    def add_player_choice(self, player_id, choice_data):
        """Add player choice to history."""
        return self.players.update_one(
            {"_id": ObjectId(player_id)},
            {"$push": {"choices": choice_data}}
        )
    
    def get_item(self, item_id):
        """Get item data by ID."""
        if isinstance(item_id, str) and len(item_id) == 24:
            return self.items.find_one({"_id": ObjectId(item_id)})
        return self.items.find_one({"_id": item_id})
    
    def get_items_by_type(self, item_type):
        """Get items by type."""
        return list(self.items.find({"type": item_type}))
    
    def get_quest(self, quest_id):
        """Get quest data by ID."""
        if isinstance(quest_id, str) and len(quest_id) == 24:
            return self.quests.find_one({"_id": ObjectId(quest_id)})
        return self.quests.find_one({"_id": quest_id})
    
    def get_location(self, location_id):
        """Get location data by ID."""
        return self.world.find_one({"_id": location_id})
    
    def get_available_quests(self, location_id, player_level):
        """Get available quests for a location and player level."""
        return list(self.quests.find({
            "location": location_id,
            "min_level": {"$lte": player_level}
        }))
    
    def initialize_game_data(self):
        """Initialize game data if collections are empty."""
        # Check if items collection is empty
        if self.items.count_documents({}) == 0:
            self._initialize_items()
        
        # Check if world collection is empty
        if self.world.count_documents({}) == 0:
            self._initialize_world()
        
        # Check if quests collection is empty
        if self.quests.count_documents({}) == 0:
            self._initialize_quests()
    
    def _initialize_items(self):
        """Initialize basic items in the database."""
        basic_items = [
            {
                "_id": "potion_health",
                "name": "Health Potion",
                "type": "consumable",
                "description": "Restores 25 health points when consumed.",
                "value": 10,
                "effects": {"health": 25}
            },
            {
                "_id": "sword_rusty",
                "name": "Rusty Sword",
                "type": "weapon",
                "description": "An old rusty sword. Better than nothing.",
                "value": 5,
                "damage": 3
            },
            {
                "_id": "shield_wooden",
                "name": "Wooden Shield",
                "type": "armor",
                "description": "A simple wooden shield that offers minimal protection.",
                "value": 5,
                "defense": 2
            }
        ]
        self.items.insert_many(basic_items)
    
    def _initialize_world(self):
        """Initialize world locations in the database."""
        locations = [
            {
                "_id": "village_start",
                "name": "Starting Village",
                "description": "A small peaceful village surrounded by farmland.",
                "connections": ["forest_path", "village_market"],
                "npcs": ["elder", "blacksmith"],
                "danger_level": 0
            },
            {
                "_id": "village_market",
                "name": "Village Market",
                "description": "A bustling marketplace where villagers trade goods.",
                "connections": ["village_start"],
                "npcs": ["merchant"],
                "danger_level": 0
            },
            {
                "_id": "forest_path",
                "name": "Forest Path",
                "description": "A winding path through the dense forest.",
                "connections": ["village_start", "forest_clearing"],
                "enemies": ["wolf", "bandit"],
                "danger_level": 1
            },
            {
                "_id": "forest_clearing",
                "name": "Forest Clearing",
                "description": "A peaceful clearing in the middle of the forest.",
                "connections": ["forest_path", "cave_entrance"],
                "enemies": ["wolf", "bear"],
                "danger_level": 2
            },
            {
                "_id": "cave_entrance",
                "name": "Cave Entrance",
                "description": "A dark, foreboding cave entrance carved into the mountainside.",
                "connections": ["forest_clearing", "cave_interior"],
                "enemies": ["goblin"],
                "danger_level": 3
            }
        ]
        self.world.insert_many(locations)
    
    def _initialize_quests(self):
        """Initialize basic quests in the database."""
        quests = [
            {
                "_id": "quest_village_rats",
                "name": "Rat Problem",
                "description": "The village elder needs help clearing rats from the cellar.",
                "location": "village_start",
                "giver": "elder",
                "min_level": 1,
                "rewards": {
                    "xp": 50,
                    "gold": 10,
                    "items": {"potion_health": 1}
                },
                "steps": [
                    "Talk to the village elder",
                    "Clear the rats from the cellar",
                    "Return to the elder for your reward"
                ]
            },
            {
                "_id": "quest_lost_sword",
                "name": "The Blacksmith's Lost Sword",
                "description": "The blacksmith has lost a valuable sword in the forest.",
                "location": "village_start",
                "giver": "blacksmith",
                "min_level": 2,
                "rewards": {
                    "xp": 100,
                    "gold": 25,
                    "items": {"sword_rusty": 1}
                },
                "steps": [
                    "Speak with the blacksmith",
                    "Search the forest path for the lost sword",
                    "Return the sword to the blacksmith"
                ]
            }
        ]
        self.quests.insert_many(quests)