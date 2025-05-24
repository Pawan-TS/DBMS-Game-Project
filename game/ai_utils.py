"""
AI utilities for the Fantasy RPG text adventure game.
Provides a wrapper around the AIGenerator class.
"""

from game.ai_generator import AIGenerator

# Create a global instance of the AIGenerator
ai_generator = AIGenerator()

def generate_response(context, prompt):
    """
    Generate a response using the AI generator.
    
    Args:
        context: Context information for the AI
        prompt: The prompt to send to the AI
    
    Returns:
        str: AI-generated response
    """
    combined_prompt = f"""
    Context: {context}
    
    {prompt}
    """
    
    return ai_generator._generate_response(combined_prompt)