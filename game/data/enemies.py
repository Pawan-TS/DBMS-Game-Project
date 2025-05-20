"""
Enemy data for the Fantasy RPG text adventure game.
"""

ENEMIES = {
    "rat": {
        "name": "Giant Rat",
        "description": "A large, mangy rat with sharp teeth.",
        "level": 1,
        "health": 15,
        "attack": 2,
        "defense": 0,
        "xp_reward": 10,
        "gold_reward": (1, 3),  # (min, max)
        "loot_table": {
            "rat_tail": 0.5,  # 50% chance
            "rat_fur": 0.3    # 30% chance
        }
    },
    "wolf": {
        "name": "Forest Wolf",
        "description": "A lean, hungry wolf with piercing yellow eyes.",
        "level": 2,
        "health": 30,
        "attack": 4,
        "defense": 1,
        "xp_reward": 25,
        "gold_reward": (2, 5),
        "loot_table": {
            "wolf_fang": 0.4,
            "wolf_pelt": 0.3
        }
    },
    "bandit": {
        "name": "Forest Bandit",
        "description": "A rough-looking human wielding a crude weapon.",
        "level": 3,
        "health": 40,
        "attack": 5,
        "defense": 2,
        "xp_reward": 35,
        "gold_reward": (5, 15),
        "loot_table": {
            "potion_health": 0.3,
            "dagger_rusty": 0.2
        }
    },
    "bear": {
        "name": "Brown Bear",
        "description": "A massive brown bear with powerful claws.",
        "level": 4,
        "health": 60,
        "attack": 7,
        "defense": 3,
        "xp_reward": 50,
        "gold_reward": (0, 0),  # Bears don't carry gold
        "loot_table": {
            "bear_claw": 0.6,
            "bear_pelt": 0.4
        }
    },
    "goblin": {
        "name": "Cave Goblin",
        "description": "A small, green-skinned creature with a wicked grin.",
        "level": 3,
        "health": 35,
        "attack": 4,
        "defense": 1,
        "xp_reward": 30,
        "gold_reward": (3, 8),
        "loot_table": {
            "goblin_ear": 0.5,
            "crude_dagger": 0.3,
            "potion_health": 0.2
        }
    }
}