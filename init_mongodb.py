"""
MongoDB Initialization Script for Fantasy RPG Text Adventure Game.
This script initializes the MongoDB database with initial game data.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

from game.data.enemies import ENEMIES
from game.data.npcs import NPCS

# Load environment variables
load_dotenv()

# Get MongoDB connection string from environment variables
MONGODB_URI = os.getenv("MONGODB_URI")

def initialize_database():
    """Initialize the MongoDB database with initial game data."""
    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)
    db = client["fantasy_rpg"]
    
    # Create collections
    players_collection = db["players"]
    items_collection = db["items"]
    quests_collection = db["quests"]
    world_collection = db["world"]
    enemies_collection = db["enemies"]
    npcs_collection = db["npcs"]
    
    # Initialize items
    if items_collection.count_documents({}) == 0:
        items = [
            {
                "_id": "potion_health",
                "name": "Health Potion",
                "type": "consumable",
                "description": "Restores 25 health points when consumed.",
                "value": 10,
                "effects": {"health": 25}
            },
            {
                "_id": "potion_mana",
                "name": "Mana Potion",
                "type": "consumable",
                "description": "Restores 25 mana points when consumed.",
                "value": 15,
                "effects": {"mana": 25}
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
                "_id": "sword_iron",
                "name": "Iron Sword",
                "type": "weapon",
                "description": "A standard iron sword. Reliable and sharp.",
                "value": 50,
                "damage": 5
            },
            {
                "_id": "shield_wooden",
                "name": "Wooden Shield",
                "type": "armor",
                "description": "A simple wooden shield that offers minimal protection.",
                "value": 5,
                "defense": 2
            },
            {
                "_id": "shield_iron",
                "name": "Iron Shield",
                "type": "armor",
                "description": "A sturdy iron shield that provides good protection.",
                "value": 40,
                "defense": 4
            },
            {
                "_id": "armor_leather",
                "name": "Leather Armor",
                "type": "armor",
                "description": "Basic leather armor that provides some protection.",
                "value": 35,
                "defense": 3
            },
            {
                "_id": "torch",
                "name": "Torch",
                "type": "tool",
                "description": "A simple torch that provides light in dark places.",
                "value": 5
            },
            {
                "_id": "rope",
                "name": "Rope",
                "type": "tool",
                "description": "A sturdy rope, useful for climbing or tying things.",
                "value": 10
            },
            {
                "_id": "map_forest",
                "name": "Forest Map",
                "type": "tool",
                "description": "A map of the forest area, revealing paths and landmarks.",
                "value": 25
            }
        ]
        items_collection.insert_many(items)
        print(f"Initialized {len(items)} items")
    
    # Initialize world locations
    if world_collection.count_documents({}) == 0:
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
            },
            {
                "_id": "cave_interior",
                "name": "Cave Interior",
                "description": "The dark interior of the cave, lit only by glowing fungi.",
                "connections": ["cave_entrance", "cave_depths"],
                "enemies": ["goblin", "bat"],
                "danger_level": 4
            },
            {
                "_id": "cave_depths",
                "name": "Cave Depths",
                "description": "The deepest part of the cave, where few have ventured.",
                "connections": ["cave_interior"],
                "enemies": ["troll"],
                "danger_level": 5
            }
        ]
        world_collection.insert_many(locations)
        print(f"Initialized {len(locations)} world locations")
    
    # Initialize quests
    if quests_collection.count_documents({}) == 0:
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
            },
            {
                "_id": "quest_herb_gathering",
                "name": "Medicinal Herbs",
                "description": "The village healer needs specific herbs from the forest clearing.",
                "location": "village_market",
                "giver": "merchant",
                "min_level": 2,
                "rewards": {
                    "xp": 75,
                    "gold": 15,
                    "items": {"potion_health": 2}
                },
                "steps": [
                    "Talk to the merchant about the healer's request",
                    "Gather herbs from the forest clearing",
                    "Return the herbs to the merchant"
                ]
            }
        ]
        quests_collection.insert_many(quests)
        print(f"Initialized {len(quests)} quests")
    
    # Initialize enemies
    if enemies_collection.count_documents({}) == 0:
        enemies_list = []
        for enemy_id, enemy_data in ENEMIES.items():
            enemy_data["_id"] = enemy_id
            enemies_list.append(enemy_data)
        
        enemies_collection.insert_many(enemies_list)
        print(f"Initialized {len(enemies_list)} enemies")
    
    # Initialize NPCs
    if npcs_collection.count_documents({}) == 0:
        npcs_list = []
        for npc_id, npc_data in NPCS.items():
            npc_data["_id"] = npc_id
            npcs_list.append(npc_data)
        
        npcs_collection.insert_many(npcs_list)
        print(f"Initialized {len(npcs_list)} NPCs")
    
    print("Database initialization complete!")

if __name__ == "__main__":
    if not MONGODB_URI:
        print("Error: MongoDB connection string not found in .env file.")
        print("Please set MONGODB_URI in the .env file.")
    else:
        initialize_database()