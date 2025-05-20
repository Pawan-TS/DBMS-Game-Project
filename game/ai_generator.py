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
        prompt = f"""
        {self.game_context}
        
        Generate a vivid description for this location:
        Name: {location_data['name']}
        Basic Description: {location_data['description']}
        Danger Level: {location_data['danger_level']}
        
        The player is currently exploring this location. Describe what they see, hear, and feel.
        Include atmospheric details and hints about what might be found here.
        """
        
        if player_data and player_data.get('visited_locations', {}).get(location_data['_id']):
            prompt += "\nNote: The player has visited this location before."
        
        return self._generate_response(prompt)
    
    def generate_combat_narrative(self, player_data, enemy_data, combat_result):
        """Generate a narrative for a combat encounter."""
        prompt = f"""
        {self.game_context}
        
        Generate a combat narrative for this encounter:
        Player: {player_data['name']}, a level {player_data['level']} {player_data['class']}
        Enemy: {enemy_data['name']} - {enemy_data['description']}
        
        Combat Result: {combat_result}
        
        Describe the battle in an exciting way. Include details about attacks, defenses, and the outcome.
        """
        
        return self._generate_response(prompt)
    
    def generate_quest_dialogue(self, quest_data, npc_data, stage="introduction"):
        """Generate dialogue for a quest giver NPC."""
        prompt = f"""
        {self.game_context}
        
        Generate dialogue for this quest interaction:
        NPC: {npc_data['name']} - {npc_data['description']}
        Quest: {quest_data['name']} - {quest_data['description']}
        Stage: {stage} (introduction, in-progress, or completion)
        
        Write the NPC's dialogue to the player. Make it sound natural and in-character.
        """
        
        return self._generate_response(prompt)
    
    def generate_item_discovery(self, item_data, discovery_context):
        """Generate a narrative for discovering an item."""
        prompt = f"""
        {self.game_context}
        
        Generate a description for finding this item:
        Item: {item_data['name']} - {item_data['description']}
        Context: {discovery_context}
        
        Describe how the player finds or receives this item in an interesting way.
        """
        
        return self._generate_response(prompt)
    
    def generate_response_to_action(self, player_data, action, current_location, game_state):
        """Generate a response to a player's action."""
        prompt = f"""
        {self.game_context}
        
        The player has taken this action: "{action}"
        
        Player: {player_data['name']}, a level {player_data['level']} {player_data['class']}
        Current Location: {current_location['name']} - {current_location['description']}
        
        Generate a response to the player's action that advances the story and provides 
        feedback on what happened as a result. Be creative but consistent with the game world.
        """
        
        return self._generate_response(prompt)
    
    def _generate_response(self, prompt):
        """Generate a response using the Gemini model."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return "The narrator pauses for a moment, collecting their thoughts..."