"""
NPC data for the Fantasy RPG text adventure game.
"""

NPCS = {
    "elder": {
        "name": "Village Elder",
        "description": "An elderly man with a long white beard and kind eyes.",
        "location": "village_start",
        "dialogue": {
            "greeting": "Welcome, traveler. Our village is small but peaceful.",
            "quest_offer": "We've been having trouble with rats in the cellar. Could you help us?",
            "quest_active": "Have you dealt with those rats yet? They're becoming quite a nuisance.",
            "quest_complete": "Thank you for your help! The village is in your debt."
        },
        "quests": ["quest_village_rats"]
    },
    "blacksmith": {
        "name": "Gruff Blacksmith",
        "description": "A muscular man with a soot-covered apron and calloused hands.",
        "location": "village_start",
        "dialogue": {
            "greeting": "Need something forged? I'm your man.",
            "quest_offer": "I lost my favorite sword in the forest. Find it for me, and I'll make it worth your while.",
            "quest_active": "Still looking for that sword? It has a distinctive red pommel.",
            "quest_complete": "You found it! As promised, here's your reward."
        },
        "quests": ["quest_lost_sword"],
        "shop": {
            "sword_iron": 50,
            "shield_iron": 40,
            "armor_leather": 35
        }
    },
    "merchant": {
        "name": "Traveling Merchant",
        "description": "A cheerful person with a colorful outfit and a large backpack.",
        "location": "village_market",
        "dialogue": {
            "greeting": "Ah, a potential customer! Take a look at my wares.",
            "farewell": "Come back soon! I'll have new items next time."
        },
        "shop": {
            "potion_health": 15,
            "potion_mana": 20,
            "torch": 5,
            "rope": 10,
            "map_forest": 25
        }
    }
}