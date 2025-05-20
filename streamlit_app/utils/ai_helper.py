import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import game modules
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

# Import AI generator module
from game.ai_generator import generate_response

def generate_location_description(location_data):
    """
    Generate an enhanced description for a location using AI.
    
    Args:
        location_data: Location data dictionary
        
    Returns:
        str: AI-generated location description
    """
    try:
        context = f"Location: {location_data.get('name', 'Unknown location')}. {location_data.get('description', '')}"
        prompt = "Describe this fantasy location in rich, evocative detail. Include sights, sounds, and atmosphere."
        
        return generate_response(context=context, prompt=prompt)
    except Exception as e:
        return f"Error generating location description: {str(e)}"

def generate_combat_narrative(player_data, enemy_data, action, result):
    """
    Generate a narrative description of a combat action using AI.
    
    Args:
        player_data: Player data dictionary
        enemy_data: Enemy data dictionary
        action: String describing the action (attack, defend, etc.)
        result: String describing the result of the action
        
    Returns:
        str: AI-generated combat narrative
    """
    try:
        context = (
            f"Player: {player_data.get('name', 'Hero')} the {player_data.get('class', 'Adventurer')}. "
            f"Enemy: {enemy_data.get('name', 'Monster')}. "
            f"Action: {action}. Result: {result}."
        )
        prompt = "Describe this combat action in an exciting, narrative style."
        
        return generate_response(context=context, prompt=prompt)
    except Exception as e:
        return f"Error generating combat narrative: {str(e)}"

def generate_npc_dialogue(npc_data, dialogue_context):
    """
    Generate dialogue for an NPC using AI.
    
    Args:
        npc_data: NPC data dictionary
        dialogue_context: Context for the dialogue (quest, greeting, etc.)
        
    Returns:
        str: AI-generated NPC dialogue
    """
    try:
        context = (
            f"NPC: {npc_data.get('name', 'Stranger')}. Role: {npc_data.get('role', 'Unknown')}. "
            f"Personality: {npc_data.get('personality', 'Neutral')}. Context: {dialogue_context}"
        )
        prompt = "Generate dialogue for this NPC that reflects their personality and role."
        
        return generate_response(context=context, prompt=prompt)
    except Exception as e:
        return f"Error generating NPC dialogue: {str(e)}"

def generate_quest_description(quest_data):
    """
    Generate an enhanced description for a quest using AI.
    
    Args:
        quest_data: Quest data dictionary
        
    Returns:
        str: AI-generated quest description
    """
    try:
        context = (
            f"Quest: {quest_data.get('name', 'Unknown quest')}. "
            f"Description: {quest_data.get('description', '')}. "
            f"Objectives: {', '.join([obj.get('description', '') for obj in quest_data.get('objectives', [])])}."
        )
        prompt = "Create an engaging and detailed description for this quest that motivates the player to complete it."
        
        return generate_response(context=context, prompt=prompt)
    except Exception as e:
        return f"Error generating quest description: {str(e)}"

def generate_item_discovery(item_data):
    """
    Generate text for discovering an item using AI.
    
    Args:
        item_data: Item data dictionary
        
    Returns:
        str: AI-generated item discovery text
    """
    try:
        context = (
            f"Item: {item_data.get('name', 'Unknown item')}. "
            f"Type: {item_data.get('type', 'misc')}. "
            f"Description: {item_data.get('description', '')}."
        )
        prompt = "Describe the player finding or receiving this item in an interesting way."
        
        return generate_response(context=context, prompt=prompt)
    except Exception as e:
        return f"Error generating item discovery text: {str(e)}"

def generate_command_response(player_data, location_data, command):
    """
    Generate a response to a player command using AI.
    
    Args:
        player_data: Player data dictionary
        location_data: Current location data dictionary
        command: The command entered by the player
        
    Returns:
        str: AI-generated response to the command
    """
    try:
        context = (
            f"Player: {player_data.get('name', 'Hero')} the {player_data.get('class', 'Adventurer')}. "
            f"Location: {location_data.get('name', 'Unknown location')}. "
            f"Command: {command}"
        )
        prompt = "Respond to the player's command in the context of this fantasy RPG game."
        
        return generate_response(context=context, prompt=prompt)
    except Exception as e:
        return f"Error generating command response: {str(e)}"
