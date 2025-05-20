import streamlit as st
import random
from utils.database import save_player_data
from utils.session import get_player, set_player, add_game_text, set_combat_state
from utils.ai_helper import generate_combat_narrative

def render_combat_ui():
    """
    Render the combat UI.
    """
    player = get_player()
    enemy = st.session_state.combat_enemy
    
    if not player or not enemy:
        st.error("Combat data not found.")
        return
    
    st.subheader(f"Combat: {enemy['name']}")
    
    # Display enemy image (placeholder)
    st.image("https://via.placeholder.com/150?text=Enemy", width=150)
    
    # Enemy stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Enemy Health", f"{enemy['current_health']}/{enemy['max_health']}")
    with col2:
        st.metric("Enemy Attack", enemy['attack'])
    with col3:
        st.metric("Enemy Defense", enemy['defense'])
    
    # Combat log
    with st.expander("Combat Log", expanded=True):
        combat_log = [entry for entry in st.session_state.game_text if entry.get('type') == 'combat']
        for entry in combat_log[-5:]:  # Show last 5 combat entries
            st.warning(entry.get('text', ''))
    
    # Combat actions
    st.subheader("Combat Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Attack"):
            combat_round("attack")
    
    with col2:
        if st.button("Defend"):
            combat_round("defend")
    
    with col3:
        if st.button("Use Item"):
            st.session_state.page = "combat_item"
    
    with col4:
        if st.button("Flee"):
            attempt_flee()

def trigger_combat(enemy=None):
    """
    Start combat with an enemy.
    
    Args:
        enemy: Enemy data dictionary or None to get a random enemy
    """
    if not enemy:
        # Get a random enemy
        db = st.session_state.db
        enemies = list(db.enemies.find())
        if not enemies:
            add_game_text("You sense danger, but nothing appears.", "system")
            return
        
        enemy = random.choice(enemies)
    
    # Initialize enemy health
    enemy['current_health'] = enemy['max_health']
    
    # Set combat state
    set_combat_state(True, enemy)
    
    # Add combat start message
    add_game_text(f"You encounter a {enemy['name']}!", "system")
    
    # AI generated combat intro
    player = get_player()
    
    from game.ai_generator import generate_response
    ai_message = generate_response(
        context=f"The player {player['name']} the {player['class']} has encountered a {enemy['name']}.",
        prompt=f"Describe the encounter with the {enemy['name']}."
    )
    
    add_game_text(ai_message, "ai")

def combat_round(player_action):
    """
    Process a round of combat.
    
    Args:
        player_action: String indicating the player's action (attack, defend, etc.)
    """
    player = get_player()
    enemy = st.session_state.combat_enemy
    
    temp_defense_boost = 0
    
    # Player action
    if player_action == "attack":
        # Calculate damage
        damage = max(1, player['attack'] - enemy['defense'] // 2)
        enemy['current_health'] -= damage
        
        # Add combat message
        combat_text = f"You hit the {enemy['name']} for {damage} damage!"
        add_game_text(combat_text, "combat")
        
        # AI narrative
        narrative = generate_combat_narrative(
            player, 
            enemy, 
            "attack", 
            f"dealt {damage} damage"
        )
        add_game_text(narrative, "ai")
    
    elif player_action == "defend":
        # Boost defense for this round
        temp_defense_boost = player['defense'] // 2
        
        # Add combat message
        add_game_text(f"You take a defensive stance, increasing your defense by {temp_defense_boost}.", "system")
    
    # Check if enemy is defeated
    if enemy['current_health'] <= 0:
        handle_enemy_defeat(enemy)
        return
    
    # Enemy action - always attack for simplicity
    # Check for evasion
    if random.random() * 100 < player['evasion']:
        add_game_text(f"You dodged the {enemy['name']}'s attack!", "system")
    else:
        # Calculate damage
        damage = max(1, enemy['attack'] - (player['defense'] + temp_defense_boost))
        player['current_health'] -= damage
        
        # Add combat message
        combat_text = f"The {enemy['name']} hits you for {damage} damage!"
        add_game_text(combat_text, "combat")
        
        # AI narrative
        narrative = generate_combat_narrative(
            player, 
            enemy, 
            "defend", 
            f"took {damage} damage"
        )
        add_game_text(narrative, "ai")
        
        # Update player in session and database
        set_player(player)
        save_player_data(st.session_state.db, player["_id"], {"current_health": player['current_health']})
        
        # Check if player died
        check_player_death()

def handle_enemy_defeat(enemy):
    """
    Handle the defeat of an enemy.
    
    Args:
        enemy: Enemy data dictionary
    """
    player = get_player()
    
    # Calculate rewards
    xp_reward = enemy.get('xp_reward', 10)
    gold_reward = enemy.get('gold_reward', 5)
    
    # Update player
    player['experience'] += xp_reward
    player['gold'] += gold_reward
    
    # Check for level up
    level_up = check_level_up(player)
    
    # Update database
    update_data = {
        "experience": player['experience'],
        "gold": player['gold'],
        "level": player['level']
    }
    
    if level_up:
        # Update the additional stats from level up
        update_data.update({
            "max_health": player['max_health'],
            "current_health": player['current_health'],
            "attack": player['attack'],
            "defense": player['defense']
        })
    
    save_player_data(st.session_state.db, player["_id"], update_data)
    
    # Add victory message
    add_game_text(f"You defeated the {enemy['name']} and gained {xp_reward} XP and {gold_reward} gold!", "system")
    
    if level_up:
        add_game_text(f"You leveled up to level {player['level']}!", "system")
    
    # Reset combat state
    set_combat_state(False, None)
    
    # AI generated victory message
    from game.ai_generator import generate_response
    ai_message = generate_response(
        context=f"The player {player['name']} the {player['class']} has defeated a {enemy['name']} and gained {xp_reward} XP and {gold_reward} gold.",
        prompt=f"Describe the victory over the {enemy['name']}."
    )
    
    add_game_text(ai_message, "ai")

def check_player_death():
    """
    Check if the player has died and handle accordingly.
    """
    player = get_player()
    
    if player['current_health'] <= 0:
        player['current_health'] = 0
        
        # Add death message
        add_game_text("You have been defeated!", "system")
        
        # Respawn at town square with penalty
        player['current_health'] = player['max_health'] // 2
        player['gold'] = max(0, player['gold'] - player['gold'] // 4)  # Lose 25% of gold
        
        # Update database
        save_player_data(
            st.session_state.db,
            player["_id"],
            {
                "current_health": player['current_health'],
                "gold": player['gold'],
                "location": "town_square"
            }
        )
        
        # Update game state
        db = st.session_state.db
        st.session_state.current_location = db.world.find_one({"id": "town_square"})
        set_combat_state(False, None)
        
        # Add respawn message
        add_game_text("You wake up at the town square with half health and have lost some gold.", "system")
        
        # Update player in session
        set_player(player)
        
        return True
    
    return False

def check_level_up(player):
    """
    Check if the player has enough XP to level up and handle if so.
    
    Args:
        player: Player data dictionary
        
    Returns:
        bool: True if player leveled up, False otherwise
    """
    # Simple level up formula: level * 100 XP needed
    xp_needed = player['level'] * 100
    
    if player['experience'] >= xp_needed:
        player['level'] += 1
        
        # Improve stats
        player['max_health'] += 10
        player['current_health'] = player['max_health']  # Heal on level up
        player['attack'] += 3
        player['defense'] += 2
        
        # Update player in session
        set_player(player)
        
        return True
    
    return False

def attempt_flee():
    """
    Attempt to flee from combat.
    """
    player = get_player()
    enemy = st.session_state.combat_enemy
    
    # 50% chance to flee
    if random.random() < 0.5:
        set_combat_state(False, None)
        add_game_text("You successfully fled from combat!", "system")
    else:
        add_game_text("You failed to flee and the enemy attacks!", "system")
        
        # Enemy gets a free attack
        damage = max(1, enemy['attack'] - player['defense'] // 2)
        player['current_health'] -= damage
        
        add_game_text(f"The {enemy['name']} hits you for {damage} damage!", "combat")
        
        # Update player in session and database
        set_player(player)
        save_player_data(st.session_state.db, player["_id"], {"current_health": player['current_health']})
        
        # Check if player died
        check_player_death()
