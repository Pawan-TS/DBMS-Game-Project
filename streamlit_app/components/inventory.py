import streamlit as st
import time
from utils.database import save_player_data
from utils.session import get_player, set_player, add_game_text, set_page
from utils.ai_helper import generate_item_discovery

def render_inventory_ui():
    """
    Render the inventory UI.
    """
    st.title("Inventory")
    
    player = get_player()
    
    if not player:
        st.error("No player data found.")
        return
    
    # Show gold
    st.subheader(f"Gold: {player.get('gold', 0)}")
    
    # Get inventory items
    inventory = player.get('inventory', [])
    
    if not inventory:
        st.info("Your inventory is empty.")
    else:
        # Group items by type
        weapons = [item for item in inventory if item.get('type') == 'weapon']
        armor = [item for item in inventory if item.get('type') == 'armor']
        consumables = [item for item in inventory if item.get('type') == 'consumable']
        other = [item for item in inventory if item.get('type') not in ['weapon', 'armor', 'consumable']]
        
        # Create tabs for item categories
        tabs = st.tabs(["All Items", "Weapons", "Armor", "Consumables", "Other"])
        
        with tabs[0]:
            render_item_list(inventory, "all")
        
        with tabs[1]:
            render_item_list(weapons, "weapon")
        
        with tabs[2]:
            render_item_list(armor, "armor")
        
        with tabs[3]:
            render_item_list(consumables, "consumable")
        
        with tabs[4]:
            render_item_list(other, "other")
    
    if st.button("Return to Game"):
        set_page("game")

def render_item_list(items, item_type):
    """
    Render a list of items.
    
    Args:
        items: List of item dictionaries
        item_type: Type of items being displayed
    """
    if not items:
        st.info(f"No {item_type} items in inventory.")
        return
    
    for item in items:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div class="item-card">
                <h3>{item.get('name', 'Unknown Item')}</h3>
                <p>{item.get('description', '')}</p>
                <p><small>{item_type_description(item)}</small></p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if item.get('type') == 'weapon' or item.get('type') == 'armor':
                if st.button("Equip", key=f"equip_{item.get('id', '')}"):
                    equip_item(item)
            
            if item.get('type') == 'consumable':
                if st.button("Use", key=f"use_{item.get('id', '')}"):
                    use_item(item)
            
            if st.button("Drop", key=f"drop_{item.get('id', '')}"):
                drop_item(item)

def item_type_description(item):
    """
    Get a description of an item based on its type.
    
    Args:
        item: Item data dictionary
        
    Returns:
        str: Description of the item
    """
    item_type = item.get('type', 'item')
    
    if item_type == 'weapon':
        return f"Weapon | Attack: +{item.get('attack_bonus', 0)}"
    elif item_type == 'armor':
        return f"Armor | Defense: +{item.get('defense_bonus', 0)}"
    elif item_type == 'consumable':
        effects = []
        if 'health_restore' in item:
            effects.append(f"Restores {item['health_restore']} health")
        
        return f"Consumable | {', '.join(effects)}"
    else:
        return "Miscellaneous item"

def equip_item(item):
    """
    Equip an item.
    
    Args:
        item: Item data dictionary
    """
    player = get_player()
    
    # Update equipped items
    if 'equipped' not in player:
        player['equipped'] = {}
    
    item_type = item.get('type')
    
    # If something is already equipped in this slot, unequip it first
    if item_type in player['equipped']:
        old_item = player['equipped'][item_type]
        player['attack'] -= old_item.get('attack_bonus', 0)
        player['defense'] -= old_item.get('defense_bonus', 0)
    
    player['equipped'][item_type] = item
    
    # Update stats
    if item_type == 'weapon':
        player['attack'] += item.get('attack_bonus', 0)
    elif item_type == 'armor':
        player['defense'] += item.get('defense_bonus', 0)
    
    # Update player in session and database
    set_player(player)
    save_player_data(
        st.session_state.db,
        player["_id"],
        {
            "equipped": player['equipped'],
            "attack": player['attack'],
            "defense": player['defense']
        }
    )
    
    # Add message to game text
    add_game_text(f"You equipped {item.get('name')}.", "system")
    
    st.success(f"You equipped {item.get('name')}!")
    time.sleep(1)
    st.experimental_rerun()

def use_item(item):
    """
    Use a consumable item.
    
    Args:
        item: Item data dictionary
    """
    player = get_player()
    
    # Apply item effects
    if 'health_restore' in item:
        player['current_health'] = min(player['max_health'], player['current_health'] + item['health_restore'])
        
        # Add message to game text
        add_game_text(f"You used {item.get('name')} and restored {item['health_restore']} health.", "system")
    
    # Remove item from inventory
    player['inventory'].remove(item)
    
    # Update player in session and database
    set_player(player)
    save_player_data(
        st.session_state.db,
        player["_id"],
        {
            "current_health": player['current_health'],
            "inventory": player['inventory']
        }
    )
    
    st.success(f"You used {item.get('name')}!")
    time.sleep(1)
    st.experimental_rerun()

def drop_item(item):
    """
    Drop an item from inventory.
    
    Args:
        item: Item data dictionary
    """
    player = get_player()
    
    # Remove item from inventory
    player['inventory'].remove(item)
    
    # Update player in session and database
    set_player(player)
    save_player_data(
        st.session_state.db,
        player["_id"],
        {"inventory": player['inventory']}
    )
    
    # Add message to game text
    add_game_text(f"You dropped {item.get('name')}.", "system")
    
    st.success(f"You dropped {item.get('name')}!")
    time.sleep(1)
    st.experimental_rerun()

def add_item_to_inventory(item):
    """
    Add an item to the player's inventory.
    
    Args:
        item: Item data dictionary
    """
    player = get_player()
    
    # Add item to inventory
    if 'inventory' not in player:
        player['inventory'] = []
    
    player['inventory'].append(item)
    
    # Update player in session and database
    set_player(player)
    save_player_data(
        st.session_state.db,
        player["_id"],
        {"inventory": player['inventory']}
    )
    
    # Add message to game text
    add_game_text(f"You acquired {item.get('name')}!", "system")
    
    # Generate AI description
    description = generate_item_discovery(item)
    add_game_text(description, "ai")
    
    return True
