import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import game modules
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

# Import game database module
from game.database import connect_to_mongodb

def init_database():
    """
    Initialize the database connection and return the database object.
    Uses the MongoDB connection from the main game module.
    """
    try:
        # Load environment variables
        load_dotenv()
        
        # Connect to MongoDB
        db = connect_to_mongodb()
        return db
    except Exception as e:
        raise Exception(f"Failed to connect to MongoDB: {str(e)}")

def get_player_data(db, player_id):
    """
    Retrieve player data from the database.
    
    Args:
        db: MongoDB database connection
        player_id: MongoDB ObjectId of the player
        
    Returns:
        dict: Player data document
    """
    try:
        return db.players.find_one({"_id": player_id})
    except Exception as e:
        raise Exception(f"Failed to retrieve player data: {str(e)}")

def save_player_data(db, player_id, data):
    """
    Save player data to the database.
    
    Args:
        db: MongoDB database connection
        player_id: MongoDB ObjectId of the player
        data: Dictionary of data to update
    """
    try:
        db.players.update_one({"_id": player_id}, {"$set": data})
    except Exception as e:
        raise Exception(f"Failed to save player data: {str(e)}")

def get_world_location(db, location_id):
    """
    Get location data from the world collection.
    
    Args:
        db: MongoDB database connection
        location_id: Location ID string
        
    Returns:
        dict: Location data document
    """
    try:
        return db.world.find_one({"id": location_id})
    except Exception as e:
        raise Exception(f"Failed to retrieve location data: {str(e)}")

def get_all_locations(db):
    """
    Get all locations from the world collection.
    
    Args:
        db: MongoDB database connection
        
    Returns:
        list: List of all location documents
    """
    try:
        return list(db.world.find())
    except Exception as e:
        raise Exception(f"Failed to retrieve all locations: {str(e)}")

def get_random_enemy(db):
    """
    Get a random enemy from the enemies collection.
    
    Args:
        db: MongoDB database connection
        
    Returns:
        dict: Random enemy document
    """
    import random
    
    try:
        enemies = list(db.enemies.find())
        if not enemies:
            return None
        return random.choice(enemies)
    except Exception as e:
        raise Exception(f"Failed to retrieve random enemy: {str(e)}")

def get_quest_data(db, quest_id):
    """
    Get quest data from the quests collection.
    
    Args:
        db: MongoDB database connection
        quest_id: Quest ID string
        
    Returns:
        dict: Quest data document
    """
    try:
        return db.quests.find_one({"id": quest_id})
    except Exception as e:
        raise Exception(f"Failed to retrieve quest data: {str(e)}")

def get_item_data(db, item_id):
    """
    Get item data from the items collection.
    
    Args:
        db: MongoDB database connection
        item_id: Item ID string
        
    Returns:
        dict: Item data document
    """
    try:
        return db.items.find_one({"id": item_id})
    except Exception as e:
        raise Exception(f"Failed to retrieve item data: {str(e)}")
