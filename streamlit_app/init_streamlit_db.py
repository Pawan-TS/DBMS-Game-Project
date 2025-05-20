"""
MongoDB Initialization Script for Fantasy RPG Game

This script initializes the MongoDB database with sample data for the game.
It creates collections for:
- world locations
- items
- enemies
- quests
- NPCs
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId

# Load environment variables
load_dotenv()

# MongoDB connection string
MONGODB_URI = os.getenv("MONGODB_URI")

def init_mongodb():
    """Initialize MongoDB with sample game data."""
    if not MONGODB_URI:
        print("Error: MONGODB_URI environment variable not set.")
        return
    
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI)
        db = client.fantasy_rpg
        
        # Clear existing collections
        db.world.drop()
        db.items.drop()
        db.enemies.drop()
        db.quests.drop()
        db.npcs.drop()
        
        # Initialize world locations
        init_world_locations(db)
        
        # Initialize items
        init_items(db)
        
        # Initialize enemies
        init_enemies(db)
        
        # Initialize quests
        init_quests(db)
        
        # Initialize NPCs
        init_npcs(db)
        
        # Create indexes
        create_indexes(db)
        
        print("MongoDB initialization completed successfully!")
        
    except Exception as e:
        print(f"Error initializing MongoDB: {e}")

def init_world_locations(db):
    """Initialize world locations collection."""
    world_locations = [
        {
            "id": "town_square",
            "name": "Town Square",
            "description": "The bustling heart of the town. People are milling about, merchants are selling their wares, and there's a fountain in the center.",
            "exits": [
                {"name": "Town Gate", "target": "town_gate"},
                {"name": "Tavern", "target": "tavern"},
                {"name": "Blacksmith", "target": "blacksmith"},
                {"name": "Potion Shop", "target": "potion_shop"}
            ]
        },
        {
            "id": "town_gate",
            "name": "Town Gate",
            "description": "The massive wooden gates that protect the town. Guards stand vigilant, watching for threats.",
            "exits": [
                {"name": "Town Square", "target": "town_square"},
                {"name": "Forest Path", "target": "forest_path"}
            ]
        },
        {
            "id": "forest_path",
            "name": "Forest Path",
            "description": "A winding dirt path through the dense forest. Sunlight filters through the canopy, casting dappled shadows.",
            "exits": [
                {"name": "Town Gate", "target": "town_gate"},
                {"name": "Forest Clearing", "target": "forest_clearing"},
                {"name": "Dark Woods", "target": "dark_woods"}
            ]
        },
        {
            "id": "forest_clearing",
            "name": "Forest Clearing",
            "description": "A peaceful clearing in the forest. Wildflowers grow here, and you can see the sky clearly above.",
            "exits": [
                {"name": "Forest Path", "target": "forest_path"},
                {"name": "Hunter's Cabin", "target": "hunters_cabin"}
            ]
        },
        {
            "id": "dark_woods",
            "name": "Dark Woods",
            "description": "The deeper part of the forest where the trees grow close together. It's difficult to see far, and strange sounds echo around you.",
            "exits": [
                {"name": "Forest Path", "target": "forest_path"},
                {"name": "Ancient Ruins", "target": "ancient_ruins"}
            ]
        },
        {
            "id": "ancient_ruins",
            "name": "Ancient Ruins",
            "description": "The crumbling remains of a once-great structure. Moss-covered stones are scattered about, and there's an eerie silence.",
            "exits": [
                {"name": "Dark Woods", "target": "dark_woods"},
                {"name": "Ruin Entrance", "target": "ruin_entrance"}
            ]
        },
        {
            "id": "ruin_entrance",
            "name": "Ruin Entrance",
            "description": "A massive stone doorway leads into the underground complex of the ruins. Ancient symbols are carved around the arch.",
            "exits": [
                {"name": "Ancient Ruins", "target": "ancient_ruins"},
                {"name": "Ruin Corridor", "target": "ruin_corridor"}
            ]
        },
        {
            "id": "ruin_corridor",
            "name": "Ruin Corridor",
            "description": "A long, dark corridor lined with stone pillars. Your footsteps echo ominously as you walk.",
            "exits": [
                {"name": "Ruin Entrance", "target": "ruin_entrance"},
                {"name": "Treasure Chamber", "target": "treasure_chamber"}
            ]
        },
        {
            "id": "treasure_chamber",
            "name": "Treasure Chamber",
            "description": "A vast chamber filled with ancient artifacts and treasures. Gold coins litter the floor, and jewels glint in the dim light.",
            "exits": [
                {"name": "Ruin Corridor", "target": "ruin_corridor"}
            ]
        },
        {
            "id": "tavern",
            "name": "The Dragon's Rest Tavern",
            "description": "A warm, inviting tavern filled with the sounds of laughter and music. The smell of food and ale fills the air.",
            "exits": [
                {"name": "Town Square", "target": "town_square"}
            ]
        },
        {
            "id": "blacksmith",
            "name": "Blacksmith's Forge",
            "description": "The heat from the forge hits you as you enter. The blacksmith is hard at work, hammering a piece of glowing metal.",
            "exits": [
                {"name": "Town Square", "target": "town_square"}
            ]
        },
        {
            "id": "potion_shop",
            "name": "Potion Shop",
            "description": "Shelves lined with colorful bottles and strange ingredients. A cauldron bubbles in the corner, filling the air with an odd smell.",
            "exits": [
                {"name": "Town Square", "target": "town_square"}
            ]
        },
        {
            "id": "hunters_cabin",
            "name": "Hunter's Cabin",
            "description": "A small, cozy cabin made of logs. Animal pelts hang on the walls, and hunting trophies are displayed proudly.",
            "exits": [
                {"name": "Forest Clearing", "target": "forest_clearing"}
            ]
        }
    ]
    
    db.world.insert_many(world_locations)
    print(f"Added {len(world_locations)} world locations.")

def init_items(db):
    """Initialize items collection."""
    items = [
        {
            "id": "rusty_sword",
            "name": "Rusty Sword",
            "description": "An old, rusty sword. It's not much, but it's better than nothing.",
            "type": "weapon",
            "attack_bonus": 5,
            "value": 5
        },
        {
            "id": "iron_sword",
            "name": "Iron Sword",
            "description": "A standard iron sword. Well-balanced and reliable.",
            "type": "weapon",
            "attack_bonus": 10,
            "value": 25
        },
        {
            "id": "steel_sword",
            "name": "Steel Sword",
            "description": "A finely crafted steel sword. The edge is sharp and deadly.",
            "type": "weapon",
            "attack_bonus": 15,
            "value": 50
        },
        {
            "id": "enchanted_blade",
            "name": "Enchanted Blade",
            "description": "A sword glowing with magical energy. It seems to cut through the air with unusual ease.",
            "type": "weapon",
            "attack_bonus": 25,
            "value": 200
        },
        {
            "id": "leather_armor",
            "name": "Leather Armor",
            "description": "Basic armor made from tanned hides. Offers minimal protection.",
            "type": "armor",
            "defense_bonus": 5,
            "value": 15
        },
        {
            "id": "chainmail",
            "name": "Chainmail",
            "description": "Armor made from interlocking metal rings. Good protection against cuts and slashes.",
            "type": "armor",
            "defense_bonus": 10,
            "value": 40
        },
        {
            "id": "plate_armor",
            "name": "Plate Armor",
            "description": "Heavy armor made from solid metal plates. Excellent protection.",
            "type": "armor",
            "defense_bonus": 20,
            "value": 100
        },
        {
            "id": "health_potion_small",
            "name": "Small Health Potion",
            "description": "A small vial of red liquid. Restores a small amount of health when consumed.",
            "type": "consumable",
            "health_restore": 20,
            "value": 10
        },
        {
            "id": "health_potion_medium",
            "name": "Medium Health Potion",
            "description": "A flask of red liquid. Restores a moderate amount of health when consumed.",
            "type": "consumable",
            "health_restore": 50,
            "value": 25
        },
        {
            "id": "health_potion_large",
            "name": "Large Health Potion",
            "description": "A large bottle of vibrant red liquid. Restores a significant amount of health when consumed.",
            "type": "consumable",
            "health_restore": 100,
            "value": 50
        },
        {
            "id": "ancient_coin",
            "name": "Ancient Coin",
            "description": "A coin from a long-lost civilization. It might be valuable to a collector.",
            "type": "misc",
            "value": 5
        },
        {
            "id": "mysterious_key",
            "name": "Mysterious Key",
            "description": "An ornate key made of a strange metal. What could it open?",
            "type": "key",
            "value": 0
        },
        {
            "id": "wolf_pelt",
            "name": "Wolf Pelt",
            "description": "The fur of a wolf. Could be sold or used for crafting.",
            "type": "misc",
            "value": 8
        },
        {
            "id": "healing_herbs",
            "name": "Healing Herbs",
            "description": "A bundle of medicinal herbs. Used in potion making.",
            "type": "material",
            "value": 5
        }
    ]
    
    db.items.insert_many(items)
    print(f"Added {len(items)} items.")

def init_enemies(db):
    """Initialize enemies collection."""
    enemies = [
        {
            "id": "wolf",
            "name": "Wolf",
            "description": "A wild wolf with sharp teeth and keen senses.",
            "max_health": 30,
            "attack": 8,
            "defense": 3,
            "xp_reward": 10,
            "gold_reward": 2,
            "possible_drops": ["wolf_pelt"]
        },
        {
            "id": "bandit",
            "name": "Bandit",
            "description": "A rough-looking person armed with a crude weapon.",
            "max_health": 40,
            "attack": 10,
            "defense": 5,
            "xp_reward": 15,
            "gold_reward": 10,
            "possible_drops": ["rusty_sword", "health_potion_small"]
        },
        {
            "id": "giant_spider",
            "name": "Giant Spider",
            "description": "A spider the size of a dog, with venomous fangs and eight gleaming eyes.",
            "max_health": 35,
            "attack": 12,
            "defense": 4,
            "xp_reward": 20,
            "gold_reward": 5,
            "possible_drops": ["health_potion_small"]
        },
        {
            "id": "skeleton",
            "name": "Skeleton",
            "description": "An animated skeleton, clacking and rattling as it moves.",
            "max_health": 25,
            "attack": 15,
            "defense": 2,
            "xp_reward": 25,
            "gold_reward": 8,
            "possible_drops": ["ancient_coin"]
        },
        {
            "id": "goblin",
            "name": "Goblin",
            "description": "A small, green-skinned creature with sharp teeth and claws.",
            "max_health": 20,
            "attack": 7,
            "defense": 3,
            "xp_reward": 8,
            "gold_reward": 5,
            "possible_drops": []
        },
        {
            "id": "troll",
            "name": "Troll",
            "description": "A large, lumbering creature with tough skin and incredible strength.",
            "max_health": 100,
            "attack": 20,
            "defense": 15,
            "xp_reward": 50,
            "gold_reward": 30,
            "possible_drops": ["health_potion_large"]
        },
        {
            "id": "ghost",
            "name": "Ghost",
            "description": "A translucent apparition that floats eerily in the air.",
            "max_health": 30,
            "attack": 15,
            "defense": 10,
            "xp_reward": 35,
            "gold_reward": 0,
            "possible_drops": ["mysterious_key"]
        },
        {
            "id": "ancient_guardian",
            "name": "Ancient Guardian",
            "description": "A stone construct animated by ancient magic. It guards the ruins with unwavering loyalty.",
            "max_health": 150,
            "attack": 25,
            "defense": 20,
            "xp_reward": 100,
            "gold_reward": 50,
            "possible_drops": ["enchanted_blade"]
        }
    ]
    
    db.enemies.insert_many(enemies)
    print(f"Added {len(enemies)} enemies.")

def init_quests(db):
    """Initialize quests collection."""
    quests = [
        {
            "id": "wolf_hunt",
            "name": "Wolf Hunt",
            "description": "The local hunter needs help controlling the wolf population in the forest.",
            "giver": "hunter",
            "objectives": [
                {
                    "id": "wolf_kill",
                    "description": "Defeat 3 wolves",
                    "target": "wolf",
                    "count": 3,
                    "completed": False
                },
                {
                    "id": "wolf_pelt",
                    "description": "Collect 2 wolf pelts",
                    "item": "wolf_pelt",
                    "count": 2,
                    "completed": False
                }
            ],
            "xp_reward": 50,
            "gold_reward": 20,
            "item_rewards": [
                {
                    "id": "leather_armor",
                    "name": "Leather Armor",
                    "description": "Basic armor made from tanned hides. Offers minimal protection.",
                    "type": "armor",
                    "defense_bonus": 5,
                    "value": 15
                }
            ]
        },
        {
            "id": "bandit_trouble",
            "name": "Bandit Trouble",
            "description": "Bandits have been harassing travelers on the road. The town guard captain wants them dealt with.",
            "giver": "guard_captain",
            "objectives": [
                {
                    "id": "bandit_defeat",
                    "description": "Defeat the bandit leader",
                    "target": "bandit_leader",
                    "count": 1,
                    "completed": False
                },
                {
                    "id": "stolen_goods",
                    "description": "Recover the stolen goods",
                    "item": "stolen_goods",
                    "count": 1,
                    "completed": False
                }
            ],
            "xp_reward": 100,
            "gold_reward": 50,
            "item_rewards": [
                {
                    "id": "iron_sword",
                    "name": "Iron Sword",
                    "description": "A standard iron sword. Well-balanced and reliable.",
                    "type": "weapon",
                    "attack_bonus": 10,
                    "value": 25
                }
            ]
        },
        {
            "id": "herbalist_request",
            "name": "Herbalist's Request",
            "description": "The town's herbalist needs specific herbs from the forest for her potions.",
            "giver": "herbalist",
            "objectives": [
                {
                    "id": "gather_herbs",
                    "description": "Collect 5 healing herbs",
                    "item": "healing_herbs",
                    "count": 5,
                    "completed": False
                }
            ],
            "xp_reward": 30,
            "gold_reward": 15,
            "item_rewards": [
                {
                    "id": "health_potion_medium",
                    "name": "Medium Health Potion",
                    "description": "A flask of red liquid. Restores a moderate amount of health when consumed.",
                    "type": "consumable",
                    "health_restore": 50,
                    "value": 25
                }
            ]
        },
        {
            "id": "ancient_secret",
            "name": "Ancient Secret",
            "description": "A historian in town believes there's a valuable artifact hidden in the ancient ruins.",
            "giver": "historian",
            "objectives": [
                {
                    "id": "find_entrance",
                    "description": "Find the entrance to the ancient ruins",
                    "location": "ruin_entrance",
                    "completed": False
                },
                {
                    "id": "defeat_guardian",
                    "description": "Defeat the ancient guardian",
                    "target": "ancient_guardian",
                    "count": 1,
                    "completed": False
                },
                {
                    "id": "retrieve_artifact",
                    "description": "Retrieve the ancient artifact",
                    "item": "ancient_artifact",
                    "count": 1,
                    "completed": False
                }
            ],
            "xp_reward": 200,
            "gold_reward": 100,
            "item_rewards": [
                {
                    "id": "enchanted_blade",
                    "name": "Enchanted Blade",
                    "description": "A sword glowing with magical energy. It seems to cut through the air with unusual ease.",
                    "type": "weapon",
                    "attack_bonus": 25,
                    "value": 200
                }
            ]
        }
    ]
    
    db.quests.insert_many(quests)
    print(f"Added {len(quests)} quests.")

def init_npcs(db):
    """Initialize NPCs collection."""
    npcs = [
        {
            "id": "hunter",
            "name": "Galen the Hunter",
            "role": "Hunter",
            "location": "hunters_cabin",
            "personality": "Gruff but fair",
            "quests": ["wolf_hunt"],
            "dialogue": {
                "greeting": "Well met, traveler. I don't get many visitors out here.",
                "quest_offer": "The wolves in these parts are getting bold. Too many of them, if you ask me. I could use some help thinning their numbers.",
                "quest_active": "How's the hunt going? Those wolves won't kill themselves, you know.",
                "quest_complete": "Good work! The forest will be safer for travelers now."
            }
        },
        {
            "id": "guard_captain",
            "name": "Captain Thorne",
            "role": "Town Guard Captain",
            "location": "town_gate",
            "personality": "Dutiful and stern",
            "quests": ["bandit_trouble"],
            "dialogue": {
                "greeting": "Halt, citizen. State your business.",
                "quest_offer": "Bandits have been causing trouble on the roads. I'd handle it myself, but I can't leave my post. Could use someone like you.",
                "quest_active": "Those bandits need to be dealt with soon. Travelers aren't safe while they're around.",
                "quest_complete": "Justice served! The roads will be safer now. You have my thanks."
            }
        },
        {
            "id": "herbalist",
            "name": "Willow",
            "role": "Herbalist",
            "location": "potion_shop",
            "personality": "Kind and knowledgeable",
            "quests": ["herbalist_request"],
            "dialogue": {
                "greeting": "Welcome to my shop. Looking for something to cure what ails you?",
                "quest_offer": "I'm running low on healing herbs. If you're heading into the forest, could you gather some for me?",
                "quest_active": "Those healing herbs grow near water. Look for plants with red berries.",
                "quest_complete": "These are perfect! I'll make good use of these in my potions."
            }
        },
        {
            "id": "historian",
            "name": "Professor Aldrich",
            "role": "Historian",
            "location": "tavern",
            "personality": "Excitable and scholarly",
            "quests": ["ancient_secret"],
            "dialogue": {
                "greeting": "Oh! Hello there! Are you interested in history? The ruins nearby are fascinating!",
                "quest_offer": "My research suggests there's an artifact of immense value in those ruins. Would you consider retrieving it? For academic purposes, of course!",
                "quest_active": "The guardian of the ruins is formidable, but I believe in you! The artifact should be in the treasure chamber.",
                "quest_complete": "Extraordinary! This artifact confirms my theories! The academic community will be thrilled!"
            }
        },
        {
            "id": "blacksmith",
            "name": "Gorrick",
            "role": "Blacksmith",
            "location": "blacksmith",
            "personality": "Straightforward and proud of his work",
            "dialogue": {
                "greeting": "Need something forged? You've come to the right place.",
                "shop": "Take a look at my wares. Quality guaranteed."
            }
        },
        {
            "id": "innkeeper",
            "name": "Marta",
            "role": "Innkeeper",
            "location": "tavern",
            "personality": "Friendly and gossipy",
            "dialogue": {
                "greeting": "Welcome to the Dragon's Rest! Can I get you something to drink?",
                "gossip": "Have you heard about the ancient ruins to the east? They say there's treasure there, but no one who's gone looking has returned..."
            }
        }
    ]
    
    db.npcs.insert_many(npcs)
    print(f"Added {len(npcs)} NPCs.")

def create_indexes(db):
    """Create indexes for faster queries."""
    db.world.create_index([("id", ASCENDING)])
    db.items.create_index([("id", ASCENDING)])
    db.enemies.create_index([("id", ASCENDING)])
    db.quests.create_index([("id", ASCENDING)])
    db.npcs.create_index([("id", ASCENDING)])
    print("Created indexes.")

if __name__ == "__main__":
    init_mongodb()
