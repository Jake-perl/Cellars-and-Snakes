import pygame
import random
import os


pygame.init()


SCREEN_WIDTH, SCREEN_HEIGHT = 950, 600
fullscreen = False
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cellars and Snakes by Jake Nel v0.0.5")


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


clock = pygame.time.Clock()


player = {
    "HP": 20,
    "MP": 10,
    "EXP": 0,
    "Strength": 3,
    "Dexterity": 2,
    "Constitution": 3,
    "Intelligence": 1,
    "Wisdom": 2,
    "Charisma": 1,
    "Inventory": {}  
}
current_turn = 0
event_log = ["Game Started"]
LOG_FILE = "adventure_log.txt"
enemy = None
player_initiative = 0
enemy_initiative = 0
player_turn = False  


with open(LOG_FILE, "w") as f:
    f.write("=== Adventure Log ===\n")

    

def write_to_log(entry):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"Turn {current_turn}: {entry}\n")



def generate_enemy():
    enemy_hp = random.randint(5, 15)
    enemy_ac = random.randint(10, 15)
    return {"HP": enemy_hp, "AC": enemy_ac, "Name": "Goblin", "Attack": 2}


def generate_item():
    items = ["Health Potion", "Magic Scroll", "Silver Key", "Rusty Sword", "Golden Coin", "Golden Coin", "Golden Coin", "Painting of an old man", "Rusty Sword", "Magic Scroll", "Health Potion", "Silver Key", "Magic Jewel", "A Book about soil", "A Treatise on Dragons", "Magic Theory 101" ]
    return random.choice(items)


def add_to_inventory(item):
    if item in player["Inventory"]:
        player["Inventory"][item] += 1
    else:
        player["Inventory"][item] = 1


def roll_initiative():
    global player_initiative, enemy_initiative, player_turn
    player_initiative = random.randint(1, 20) + player["Dexterity"]
    enemy_initiative = random.randint(1, 20)
    if player_initiative >= enemy_initiative:
        player_turn = True
        return f"You won initiative with {player_initiative} (Enemy rolled {enemy_initiative})."
    else:
        player_turn = False
        return f"The enemy won initiative with {enemy_initiative} (You rolled {player_initiative})."

player["AP"] = 3

def use_ability(ability):
    """Handle the use of special abilities."""
    if ability == "Power Strike" and player["AP"] >= 1:
        player["AP"] -= 1
        return "power_strike"
    elif ability == "Heal" and player["AP"] >= 1:
        player["AP"] -= 1
        player["HP"] = min(player["HP"] + 10, 20)
        event = "You used Heal and restored 10 HP."
        event_log.append(event)
        write_to_log(event)
        return None
    else:
        event = "Not enough Ability Points to use this ability."
        event_log.append(event)
        write_to_log(event)
        return None

def read_book(book_title):
    """Simulate reading a book and display a nine-line story or fact."""
    books = {
        "A Book about soil": [
            "Soil is the foundation of life on Earth.",
            "It hosts billions of microorganisms in a single teaspoon.",
            "There are more soil organisms in one scoop than people on Earth!",
            "Soil acts as a natural filter for water.",
            "Healthy soil stores more carbon than forests.",
            "It can take 1,000 years to form just 1 cm of soil.",
            "There are over 70,000 types of soil in the U.S. alone.",
            "Earthworms are vital for aerating and mixing soil layers.",
            "Protecting soil is crucial for future food security."
        ],
        "A Treatise on Dragons": [
            "Dragons are mythical creatures with vast lore.",
            "They are often depicted as fire-breathing reptiles.",
            "In many cultures, dragons symbolize power and wisdom.",
            "Western dragons are seen as greedy hoarders of gold.",
            "Eastern dragons are often benevolent and wise.",
            "Dragons are said to live for thousands of years.",
            "Legends speak of dragons granting immense power.",
            "Dragon scales are impervious to most weapons.",
            "To slay a dragon is the ultimate heroic feat."
        ],
        "Magic Theory 101": [
            "Magic is the art of altering reality with willpower.",
            "Spells require mental focus and precise gestures.",
            "Elemental magic draws power from nature's forces.",
            "Illusion magic manipulates light and perception.",
            "Runes amplify magic with ancient symbols.",
            "Every spell requires a balance of energy and control.",
            "Some believe magic is connected to the stars.",
            "Powerful magic users often train for decades.",
            "Misuse of magic can lead to catastrophic results."
        ]
    }

    if book_title in books:
        story = books[book_title]
        event_log.extend(story)  # Add the story lines to the event log
        write_to_log(f"You read {book_title}. Here's what you learned:")
        for line in story:
            write_to_log(line)
        return story
    else:
        return ["You open the book, but the pages are blank..."]  # Default for unknown books


player["Gold"] = 0  # Add gold to the player stats

def generate_shop_items():
    """Generate random items for the shop."""
    return {
        "Health Potion": {"price": 10, "effect": "heal"},
        "Strength Elixir": {"price": 15, "effect": "strength"},
    }

def visit_shop():
    """Simulate visiting a shop."""
    shop_items = generate_shop_items()
    event = "You encounter a traveling shop! Available items:"
    for item, details in shop_items.items():
        event += f"\n- {item}: {details['price']} Gold"
    event += "\nPress B to Buy (type item name after) or L to Leave."
    event_log.append(event)
    write_to_log(event)
    return shop_items

def buy_item(item, shop_items):
    """Buy an item from the shop."""
    if item in shop_items:
        if player["Gold"] >= shop_items[item]["price"]:
            player["Gold"] -= shop_items[item]["price"]
            if shop_items[item]["effect"] == "heal":
                player["HP"] = min(player["HP"] + 10, 20)
                event = f"You bought a {item} and healed 10 HP."
            elif shop_items[item]["effect"] == "strength":
                player["Strength"] += 1
                event = f"You bought a {item} and increased your Strength by 1."
        else:
            event = "You don't have enough gold to buy that!"
    else:
        event = "Invalid item. Try again."
    event_log.append(event)
    write_to_log(event)


def enemy_attack():
    global player
    roll = random.randint(1, 20)
    attack_roll = roll + 2  
    if roll == 20:  
        damage = random.randint(1, 6) * 2
        player["HP"] -= damage
        return f"The enemy landed a critical hit! You took {damage} damage. Your HP: {player['HP']}"
    elif attack_roll >= 10:  
        damage = random.randint(1, 6)
        player["HP"] -= damage
        return f"The enemy attacked and dealt {damage} damage. Your HP: {player['HP']}"
    else:
        return "The enemy attacked and missed!"



# Experience and leveling system
LEVEL_UP_EXP = 100  # EXP required to level up initially
EXP_PER_LEVEL = 50  # Additional EXP needed per level

def calculate_enemy_exp(enemy):
    """Calculate the EXP rewarded for defeating an enemy."""
    base_exp = 10
    difficulty_modifier = (enemy["HP"] + enemy["AC"]) // 2
    return base_exp + difficulty_modifier

def level_up():
    """Handle leveling up the player."""
    global LEVEL_UP_EXP
    player["EXP"] -= LEVEL_UP_EXP
    LEVEL_UP_EXP += EXP_PER_LEVEL
    player["HP"] += 5  
    player["MP"] += 2  
    stat_to_improve = random.choice(["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"])
    player[stat_to_improve] += 1
    event = (f"Congratulations! You leveled up! Your {stat_to_improve} increased by 1. "
             f"HP and MP increased. Next level at {LEVEL_UP_EXP} EXP.")
    event_log.append(event)
    write_to_log(event)

def gain_exp(amount):
    """Add EXP to the player and handle leveling up if applicable."""
    player["EXP"] += amount
    event = f"You gained {amount} EXP! Total EXP: {player['EXP']}/{LEVEL_UP_EXP}"
    event_log.append(event)
    write_to_log(event)
    if player["EXP"] >= LEVEL_UP_EXP:
        level_up()



# Perform an action for the turn
def perform_action(action):
    global current_turn, enemy, player, player_turn
    current_turn += 1

    if action == "explore":
        if random.random() < 0.3:  # 30% chance to encounter an enemy
            enemy = generate_enemy()
            event = f"You encountered a {enemy['Name']}! HP: {enemy['HP']}, AC: {enemy['AC']}"
            event_log.append(event)
            write_to_log(event)
            initiative_event = roll_initiative()
            event_log.append(initiative_event)
            write_to_log(initiative_event)
        elif random.random() < 0.3:  # 30% chance to find an item
            item = generate_item()
            add_to_inventory(item)
            event = f"You found a {item}!"
            event_log.append(event)
            write_to_log(event)
        else:
            event = "You explore the area but find nothing."
            event_log.append(event)
            write_to_log(event)

    elif action == "rest":
        player["HP"] = min(player["HP"] + 5, 20)
        player["AP"] = min(player["AP"] + 1, 3)  # Regenerate 1 AP
        event = "You rested, regained 5 HP, and recovered 1 AP."
        event_log.append(event)
        write_to_log(event)


    elif action == "status":
        event = (f"Status: HP = {player['HP']}, MP = {player['MP']}, EXP = {player['EXP']}/{LEVEL_UP_EXP}, "
                 f"STR = {player['Strength']}, DEX = {player['Dexterity']}, CON = {player['Constitution']}, "
                 f"INT = {player['Intelligence']}, WIS = {player['Wisdom']}, CHA = {player['Charisma']}")
        event_log.append(event)
        write_to_log(event)

    elif action == "inventory":
        if player["Inventory"]:
            inventory_list = [f"{count}x {item}" for item, count in player["Inventory"].items()]
            event = f"Inventory: {', '.join(inventory_list)}"
        else:
            event = "Your inventory is empty."
        event_log.append(event)
        write_to_log(event)

    elif action == "attack" and enemy:
        if player_turn:
            roll = random.randint(1, 20)
            attack_roll = roll + player["Strength"]
            damage = random.randint(1, 6) + player["Strength"]

        if roll == 20:  # Critical hit
            exp_gain = calculate_enemy_exp(enemy)
            gain_exp(exp_gain)
            enemy["HP"] = 0
            event = f"Critical hit! You rolled a 20 and defeated the {enemy['Name']} instantly! Gained {exp_gain} EXP."
            event_log.append(event)
            write_to_log(event)
        elif attack_roll >= enemy["AC"]:
            enemy["HP"] -= damage
            if enemy["HP"] <= 0:
                exp_gain = calculate_enemy_exp(enemy)
                gain_exp(exp_gain)
                player["Gold"] += random.randint(5, 10)  # Gold drop
                event = (f"You hit the {enemy['Name']} for {damage} damage and defeated it! "
                         f"Gained {exp_gain} EXP and found {player['Gold']} Gold.")
            else:
                event = f"You hit the {enemy['Name']} for {damage} damage. It has {enemy['HP']} HP left."
            event_log.append(event)
            write_to_log(event)
        else:
            event = f"You rolled a {roll} (with modifier: {attack_roll}) and missed the {enemy['Name']}."
            event_log.append(event)
            write_to_log(event)

        # After the player's turn, allow the enemy to attack if it is still alive
        if enemy["HP"] > 0:
            enemy_event = enemy_attack()
            event_log.append(enemy_event)
            write_to_log(enemy_event)

        else:
            # Player tried to attack out of turn
            event = "It's not your turn! Wait for the enemy to act."
            event_log.append(event)
            write_to_log(event)

    elif action == "read":
        story_lines = read_book("A Book about soil")
        y_offset = 10
        for line in story_lines:
            text = font.render(line, True, WHITE)
            screen.blit(text, (10, y_offset))
            y_offset += 20

    elif action == "attack" and not enemy:
        event = "There is no enemy to attack."
        event_log.append(event)
        write_to_log(event)

    else:
        event = "Unknown action."
        event_log.append(event)
        write_to_log(event)

    # Check if the player is dead
    if player["HP"] <= 0:
        handle_player_death()


def handle_player_death():
    global game_running
    event_log.append("You have died. Game over!")
    write_to_log("You have died. Game over!")
    save_log_to_file()
    game_running = False


def save_log_to_file():
    file_path = os.path.join(os.getcwd(), LOG_FILE)
    print(f"\nGame log saved to: {file_path}")
    print("You can download the file from this path.")



game_running = True
while game_running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:  # 'E' for explore
                perform_action("explore")
            elif event.key == pygame.K_r:  # 'R' for rest
                perform_action("rest")
            elif event.key == pygame.K_s:  # 'S' for status
                perform_action("status")
            elif event.key == pygame.K_i:  # 'I' for inventory
                perform_action("inventory")
            elif event.key == pygame.K_d:  # 'D' to attack
                perform_action("attack")
            elif event.key == pygame.K_q:  # 'Q' to quit
                save_log_to_file()
                pygame.quit()
                exit()
            elif event.key == pygame.K_f:  # 'F' for fullscreen toggle
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Render the event log on-screen
    font = pygame.font.Font(None, 30)
    y_offset = 10
    for log in event_log[-10:]:  
        text = font.render(log, True, WHITE)
        screen.blit(text, (10, y_offset))
        y_offset += 20

    
    instructions = [
        "Press E to Explore",
        "Press R to Rest",
        "Press S to Check Status",
        "Press I to View Inventory",
        "Press D to Attack",
        "Press F to Toggle Fullscreen",
        "Press Q to Quit"
    ]
    y_offset = SCREEN_HEIGHT - len(instructions) * 20 - 10
    for instruction in instructions:
        text = font.render(instruction, True, WHITE)
        screen.blit(text, (10, y_offset))
        y_offset += 20

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
