import streamlit as st
from utils.database import save_player_data
from utils.session import get_player, set_player, add_game_text, set_page
from utils.ai_helper import generate_quest_description

def render_quests_ui():
    """
    Render the quests UI.
    """
    st.title("Quest Journal")
    
    player = get_player()
    
    if not player:
        st.error("No player data found.")
        return
    
    # Get active quests
    active_quests = player.get('quests', [])
    
    if not active_quests:
        st.info("You don't have any active quests.")
    else:
        for quest in active_quests:
            # Display quest information
            with st.expander(quest.get('name', 'Unknown Quest'), expanded=True):
                st.markdown(f"""
                <div class="quest-item">
                    <p><strong>Description:</strong> {quest.get('description', '')}</p>
                    <p><strong>Status:</strong> {get_quest_status(quest)}</p>
                    <p><strong>Rewards:</strong> {get_quest_rewards(quest)}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show objectives
                st.subheader("Objectives")
                
                for objective in quest.get('objectives', []):
                    status = "Completed" if objective.get('completed', False) else "In Progress"
                    st.markdown(f"""
                    <div class="quest-item {'quest-complete' if status == 'Completed' else ''}">
                        <p>{objective.get('description', '')}: {status}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # If quest is complete, show complete button
                if get_quest_status(quest) == "Completed" and not quest.get('rewarded', False):
                    if st.button("Claim Rewards", key=f"claim_{quest.get('id', '')}"):
                        claim_quest_rewards(quest)
    
    if st.button("Return to Game"):
        set_page("game")

def get_quest_status(quest):
    """
    Get the status of a quest.
    
    Args:
        quest: Quest data dictionary
        
    Returns:
        str: Status of the quest
    """
    objectives = quest.get('objectives', [])
    completed = sum(1 for obj in objectives if obj.get('completed', False))
    total = len(objectives)
    
    if completed == total:
        return "Completed"
    else:
        return f"In Progress ({completed}/{total})"

def get_quest_rewards(quest):
    """
    Get a string representation of quest rewards.
    
    Args:
        quest: Quest data dictionary
        
    Returns:
        str: String describing the rewards
    """
    rewards = []
    
    if 'xp_reward' in quest:
        rewards.append(f"{quest['xp_reward']} XP")
    
    if 'gold_reward' in quest:
        rewards.append(f"{quest['gold_reward']} Gold")
    
    if 'item_rewards' in quest:
        for item in quest.get('item_rewards', []):
            rewards.append(item.get('name', 'Unknown Item'))
    
    return ", ".join(rewards) if rewards else "None"

def claim_quest_rewards(quest):
    """
    Claim the rewards for a completed quest.
    
    Args:
        quest: Quest data dictionary
    """
    player = get_player()
    
    # Award XP
    if 'xp_reward' in quest:
        player['experience'] += quest['xp_reward']
        add_game_text(f"You gained {quest['xp_reward']} XP from {quest['name']}!")
    
    # Award gold
    if 'gold_reward' in quest:
        player['gold'] += quest['gold_reward']
        add_game_text(f"You gained {quest['gold_reward']} gold from {quest['name']}!")
    
    # Award items
    if 'item_rewards' in quest:
        from components.inventory import add_item_to_inventory
        
        for item in quest.get('item_rewards', []):
            player['inventory'].append(item)
            add_game_text(f"You received {item['name']} from {quest['name']}!")
    
    # Mark quest as rewarded
    for i, player_quest in enumerate(player['quests']):
        if player_quest.get('id') == quest.get('id'):
            player['quests'][i]['rewarded'] = True
            break
    
    # Check for level up
    from components.combat import check_level_up
    level_up = check_level_up(player)
    
    if level_up:
        add_game_text(f"You leveled up to level {player['level']}!")
    
    # Update player in session and database
    set_player(player)
    save_player_data(
        st.session_state.db,
        player["_id"],
        {
            "experience": player['experience'],
            "gold": player['gold'],
            "inventory": player['inventory'],
            "quests": player['quests'],
            "level": player['level']
        }
    )
    
    st.success(f"You claimed the rewards for {quest['name']}!")
    st.experimental_rerun()

def add_quest(quest_id):
    """
    Add a quest to the player's quest log.
    
    Args:
        quest_id: ID of the quest to add
        
    Returns:
        bool: True if quest was added, False otherwise
    """
    player = get_player()
    db = st.session_state.db
    
    # Check if player already has the quest
    for player_quest in player.get('quests', []):
        if player_quest.get('id') == quest_id:
            return False
    
    # Get quest from database
    quest = db.quests.find_one({"id": quest_id})
    
    if not quest:
        return False
    
    # Add quest to player's quest log
    if 'quests' not in player:
        player['quests'] = []
    
    player['quests'].append(quest)
    
    # Update player in session and database
    set_player(player)
    save_player_data(
        db,
        player["_id"],
        {"quests": player['quests']}
    )
    
    # Add quest received message
    add_game_text(f"New quest: {quest['name']}")
    
    # Generate AI quest description
    description = generate_quest_description(quest)
    add_game_text(description, "ai")
    
    return True

def update_quest_objective(quest_id, objective_id, completed=True):
    """
    Update a quest objective's completion status.
    
    Args:
        quest_id: ID of the quest
        objective_id: ID of the objective
        completed: Whether the objective is completed
        
    Returns:
        bool: True if objective was updated, False otherwise
    """
    player = get_player()
    
    # Find the quest
    for i, quest in enumerate(player.get('quests', [])):
        if quest.get('id') == quest_id:
            # Find the objective
            for j, objective in enumerate(quest.get('objectives', [])):
                if objective.get('id') == objective_id:
                    # Update objective
                    player['quests'][i]['objectives'][j]['completed'] = completed
                    
                    # Update player in session and database
                    set_player(player)
                    save_player_data(
                        st.session_state.db,
                        player["_id"],
                        {"quests": player['quests']}
                    )
                    
                    # Add message
                    objective_desc = objective.get('description', 'Objective')
                    if completed:
                        add_game_text(f"Quest objective completed: {objective_desc}")
                    else:
                        add_game_text(f"Quest objective updated: {objective_desc}")
                    
                    # Check if all objectives are complete
                    all_complete = all(obj.get('completed', False) for obj in player['quests'][i]['objectives'])
                    
                    if all_complete:
                        add_game_text(f"Quest completed: {quest['name']}! Return to a quest giver to claim your rewards.")
                    
                    return True
    
    return False
