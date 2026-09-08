"""
game_engine.py

Core logic and game state for the text-based adventure game
'Beyond the Forest'. Includes player state, movement,
encounters, combat, and inventory management.
"""

import random
#Game State 

player_name = ""
player_health = 100
inventory = []
current_location = "Forest Entrance"

#  Map and Monsters 

locations = {
    "Forest Entrance": {"north": "Deep Forest", "east": "Riverbank"},
    "Deep Forest": {"south": "Forest Entrance"},
    "Riverbank": {"west": "Forest Entrance"},
}

monsters = {
    "Deep Forest": ["Goblin", "Wolf"],
    "Riverbank": ["Giant Spider", "Bandit"],
}

#  Game Functions 

def set_player_name(name):
    """Set the player's name."""
    global player_name
    player_name = name

def get_status():
    """Return current status as a dict."""
    return {
        "location": current_location,
        "health": player_health,
        "inventory": inventory.copy()
    }

def move(direction):
    """Move to a new location if possible."""
    global current_location
    if direction in locations[current_location]:
        current_location = locations[current_location][direction]
        return f"You move {direction} to the {current_location}."
    return "You can't go that way."

def encounter_monster():
    """Return monster name if encountered, else None."""
    if current_location in monsters and random.random() < 0.5:
        return random.choice(monsters[current_location])
    return None

def fight(monster):
    """Handle fighting a monster."""
    global player_health
    if random.random() < 0.6:
        inventory.append("Medkit")
        return f"You defeated the {monster}!\nYou found a Medkit on the {monster}."
    else:
        damage = random.randint(10, 30)
        player_health -= damage
        if player_health <= 0:
            return f"The {monster} attacked! You lost {damage} health and died."
        return f"The {monster} attacked! You lost {damage} health."

def run(monster):
    """Handle attempt to escape from monster."""
    global player_health
    if random.random() < 0.7:
        return "You escaped safely!"
    else:
        damage = random.randint(5, 15)
        player_health -= damage
        if player_health <= 0:
            return f"You failed to escape from the {monster}. Took {damage} damage and died."
        return f"You failed to escape and took {damage} damage."

def use_item(item_name="Medkit"):
    """Use a Medkit to restore health."""
    global player_health
    if item_name in inventory:
        inventory.remove(item_name)
        player_health += 20
        return f"You used a {item_name}. Health restored by 20 points."
    return f"You don't have a {item_name}."

def is_alive():
    """Return True if player is alive."""
    return player_health > 0

def has_won():
    """Return True if player has reached the Riverbank with a Medkit."""
    return current_location == "Riverbank" and "Medkit" in inventory

def reset_game():
    """Reset all game state to default."""
    global player_name, player_health, inventory, current_location
    player_name = ""
    player_health = 100
    inventory.clear()
    current_location = "Forest Entrance"
