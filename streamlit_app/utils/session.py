import streamlit as st

def init_session_state():
    """
    Initialize the session state variables if they don't exist.
    """
    if "initialized" not in st.session_state:
        st.session_state.initialized = False
        st.session_state.player = None
        st.session_state.current_location = None
        st.session_state.game_text = []
        st.session_state.inventory = []
        st.session_state.quests = []
        st.session_state.in_combat = False
        st.session_state.combat_enemy = None
        st.session_state.page = "home"

def get_player():
    """
    Get the current player from session state.
    
    Returns:
        dict: Player data or None if no player is loaded
    """
    return st.session_state.player

def set_player(player_data):
    """
    Set the current player in session state.
    
    Args:
        player_data: Player data dictionary
    """
    st.session_state.player = player_data

def get_current_location():
    """
    Get the current location from session state.
    
    Returns:
        dict: Location data or None if no location is set
    """
    return st.session_state.current_location

def set_current_location(location_data):
    """
    Set the current location in session state.
    
    Args:
        location_data: Location data dictionary
    """
    st.session_state.current_location = location_data

def add_game_text(text, text_type="system"):
    """
    Add text to the game text history.
    
    Args:
        text: Text to add
        text_type: Type of text (system, player, ai, combat)
    """
    st.session_state.game_text.append({
        "type": text_type,
        "text": text
    })

def get_game_text():
    """
    Get the game text history.
    
    Returns:
        list: List of game text entries
    """
    return st.session_state.game_text

def clear_game_text():
    """
    Clear the game text history.
    """
    st.session_state.game_text = []

def set_page(page_name):
    """
    Set the current page in the app.
    
    Args:
        page_name: Name of the page to display
    """
    st.session_state.page = page_name

def get_page():
    """
    Get the current page name.
    
    Returns:
        str: Current page name
    """
    return st.session_state.page

def set_combat_state(in_combat, enemy=None):
    """
    Set the combat state.
    
    Args:
        in_combat: Boolean indicating if in combat
        enemy: Enemy data dictionary or None
    """
    st.session_state.in_combat = in_combat
    st.session_state.combat_enemy = enemy

def is_in_combat():
    """
    Check if player is in combat.
    
    Returns:
        bool: True if in combat, False otherwise
    """
    return st.session_state.in_combat

def get_combat_enemy():
    """
    Get the current combat enemy.
    
    Returns:
        dict: Enemy data or None if not in combat
    """
    return st.session_state.combat_enemy
