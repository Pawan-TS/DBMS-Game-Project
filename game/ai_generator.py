"""
AI Generator module for the Fantasy RPG text adventure game.
Uses Google Gemini to generate responses.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

class AIGenerator:
    """Google Gemini AI response generator."""
    
    def __init__(self):
        """Initialize the AI generator."""
        # Set up the model
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Game context to provide to the AI
        self.game_context = """
        You are the narrator for a fantasy RPG text adventure game. The game is set in a 
        medieval fantasy world with magic, monsters, and quests. The player is on a journey 
        to become a hero. Your responses should be descriptive, immersive, and help move 
        the story forward. Keep responses concise (2-3 paragraphs maximum) but vivid.
        """
    
    def generate_location_description(self, location_data, player_data=None):
        """Generate an enhanced description for a location."""
        # Get available NPCs, items, and connections for the location
        available_npcs = location_data.get('npcs', [])
        available_enemies = location_data.get('enemies', [])
        available_connections = location_data.get('connections', [])
        
        # Format the available objects for the prompt
        npcs_str = "None" if not available_npcs else ", ".join(available_npcs)
        enemies_str = "None" if not available_enemies else ", ".join(available_enemies)
        connections_str = "None" if not available_connections else ", ".join(available_connections)
        
        prompt = f"""
        {self.game_context}
        
        Generate a vivid description for this location:
        Name: {location_data['name']}
        Basic Description: {location_data['description']}
        Danger Level: {location_data['danger_level']}
        
        IMPORTANT: Only reference game objects that actually exist in this location:
        - NPCs present: {npcs_str}
        - Enemies present: {enemies_str}
        - Connected locations: {connections_str}
        
        The player is currently exploring this location. Describe what they see, hear, and feel.
        Include atmospheric details and hints about what might be found here.
        
        RULES:
        1. ONLY mention NPCs, enemies, and connected locations that are listed above
        2. DO NOT invent or hallucinate new game elements that aren't in the lists above
        3. Be descriptive but factual about what exists in this location
        """
        
        if player_data and player_data.get('visited_locations', {}).get(location_data['_id']):
            prompt += "\nNote: The player has visited this location before."
        
        return self._generate_response(prompt)
    
    def generate_combat_narrative(self, player_data, enemy_data, combat_result):
        """Generate a narrative for a combat encounter."""
        # Get player's equipment and abilities
        player_inventory = player_data.get('inventory', {})
        player_stats = player_data.get('stats', {})
        
        prompt = f"""
        {self.game_context}
        
        Generate a combat narrative for this encounter:
        Player: {player_data['name']}, a level {player_data['level']} {player_data['class']}
        Player Stats: Health {player_stats.get('health', 'unknown')}, Strength {player_stats.get('strength', 'unknown')}, Defense {player_stats.get('defense', 'unknown')}
        Player Equipment: {', '.join(player_inventory.keys()) or 'Basic equipment'}
        
        Enemy: {enemy_data['name']} - {enemy_data['description']}
        
        Combat Result: {combat_result}
        
        RULES:
        1. ONLY reference equipment and abilities that the player actually has
        2. DO NOT invent or hallucinate new weapons, spells, or abilities
        3. Describe the battle in an exciting way while staying true to the game mechanics
        4. Include details about attacks, defenses, and the outcome
        5. Keep the narrative consistent with the player's class and equipment
        """
        
        return self._generate_response(prompt)
    
    def generate_quest_dialogue(self, quest_data, npc_data, stage="introduction"):
        """Generate dialogue for a quest giver NPC."""
        # Get quest steps and rewards
        quest_steps = quest_data.get('steps', [])
        quest_rewards = quest_data.get('rewards', {})
        
        # Format rewards for the prompt
        rewards_str = []
        if 'xp' in quest_rewards:
            rewards_str.append(f"{quest_rewards['xp']} XP")
        if 'gold' in quest_rewards:
            rewards_str.append(f"{quest_rewards['gold']} gold")
        if 'items' in quest_rewards:
            for item_id, quantity in quest_rewards['items'].items():
                rewards_str.append(f"{quantity} {item_id}")
        
        rewards_text = ", ".join(rewards_str) if rewards_str else "No specific rewards"
        
        prompt = f"""
        {self.game_context}
        
        Generate dialogue for this quest interaction:
        NPC: {npc_data['name']} - {npc_data['description']}
        Quest: {quest_data['name']} - {quest_data['description']}
        Quest Steps: {', '.join(quest_steps)}
        Quest Rewards: {rewards_text}
        Stage: {stage} (introduction, in-progress, or completion)
        
        RULES:
        1. ONLY reference quest steps and rewards that are listed above
        2. DO NOT invent or hallucinate new quest objectives or rewards
        3. Write the NPC's dialogue to the player in a natural and in-character way
        4. Keep the dialogue focused on the actual quest details
        5. If this is an introduction, explain what needs to be done and why
        6. If this is in-progress, ask about progress or provide encouragement
        7. If this is completion, thank the player and mention the specific rewards
        """
        
        return self._generate_response(prompt)
    
    def generate_item_discovery(self, item_data, discovery_context):
        """Generate a narrative for discovering an item."""
        # Get item properties
        item_type = item_data.get('type', 'unknown')
        item_value = item_data.get('value', 0)
        item_effects = item_data.get('effects', {})
        
        # Format item properties
        effects_str = []
        for effect, value in item_effects.items():
            effects_str.append(f"{effect}: {value}")
        
        effects_text = ", ".join(effects_str) if effects_str else "No special effects"
        
        prompt = f"""
        {self.game_context}
        
        Generate a description for finding this item:
        Item: {item_data['name']} - {item_data['description']}
        Type: {item_type}
        Value: {item_value} gold
        Effects: {effects_text}
        Context: {discovery_context}
        
        RULES:
        1. ONLY reference properties of the item that are listed above
        2. DO NOT invent or hallucinate new item properties or effects
        3. Describe how the player finds or receives this item in an interesting way
        4. Keep the description consistent with the item's actual properties
        5. Make the discovery feel rewarding and meaningful
        """
        
        return self._generate_response(prompt)
    
    def generate_response_to_action(self, player_data, action, current_location, game_state):
        """Generate a response to a player's action."""
        # Get available NPCs, items, and connections for the current location
        available_npcs = current_location.get('npcs', [])
        available_enemies = current_location.get('enemies', [])
        available_connections = current_location.get('connections', [])
        
        # Format the available objects for the prompt
        npcs_str = "None" if not available_npcs else ", ".join(available_npcs)
        enemies_str = "None" if not available_enemies else ", ".join(available_enemies)
        connections_str = "None" if not available_connections else ", ".join(available_connections)
        
        prompt = f"""
        {self.game_context}
        
        The player has taken this action: "{action}"
        
        Player: {player_data['name']}, a level {player_data['level']} {player_data['class']}
        Current Location: {current_location['name']} - {current_location['description']}
        
        IMPORTANT: Only reference game objects that actually exist in the current context:
        - Available NPCs in this location: {npcs_str}
        - Available enemies in this location: {enemies_str}
        - Connected locations: {connections_str}
        - Player's inventory: {', '.join(player_data.get('inventory', {}).keys()) or 'Empty'}
        
        Generate a response to the player's action that advances the story and provides 
        feedback on what happened as a result. Be creative but consistent with the game world.
        
        RULES:
        1. ONLY mention NPCs, enemies, items, and locations that are listed above
        2. DO NOT invent or hallucinate new game elements that aren't in the lists above
        3. If the player tries to interact with something that doesn't exist, gently inform them
        4. If the action doesn't make sense, suggest valid commands (go, look, talk, etc.)
        5. Always include a suggestion to type 'help' for a list of commands if the player seems lost
        """
        
        return self._generate_response(prompt)
    
    def _generate_response(self, prompt):
        """Generate a response using the Gemini model."""
        # Add a final reminder to avoid hallucinations
        final_prompt = f"""
        {prompt}
        
        FINAL REMINDER: Your response must ONLY reference game elements that actually exist in the game world.
        DO NOT invent or hallucinate new NPCs, items, locations, or abilities that weren't mentioned in the prompt.
        Keep your response concise (2-3 paragraphs maximum) and focused on the actual game state.
        """
        
        try:
            response = self.model.generate_content(final_prompt)
            if response and hasattr(response, 'text') and response.text:
                return response.text
            else:
                return "I don't understand that command. Type 'help' for a list of available commands."
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return "I don't understand that command. Type 'help' for a list of available commands."