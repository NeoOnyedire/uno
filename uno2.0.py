import random
from colorama import init, Fore, Style

# Initialize colorama (works on Windows, Linux, macOS)
init(autoreset=True)

# Simple color mapping
COLOR_MAP = {
    "Red": Fore.RED,
    "Yellow": Fore.YELLOW,
    "Blue": Fore.BLUE,
    "Green": Fore.GREEN,
    "Black": Fore.MAGENTA,   # using magenta for wilds (looks good in most terminals)
}

def colored(text, color_name):
    """Return colored text if color_name exists, otherwise plain text"""
    color = COLOR_MAP.get(color_name, "")
    return f"{color}{text}{Style.RESET_ALL}"

def card_to_str(card):
    """Convert a card tuple to a nicely colored string"""
    color, value = card
    if isinstance(value, int):
        val_str = str(value)
    else:
        val_str = value  # Skip, Reverse, +2, Wild, +4

    if color == "Black":
        # Wild and +4 get special bright treatment
        if value == "Wild":
            return colored("WILD", "Black")
        elif value == "+4":
            return colored("+4", "Black")
        else:
            return colored(val_str, "Black")
    else:
        return colored(val_str, color)

def card_deck():
    deck = []
    colours = ["Red", "Yellow", "Blue", "Green"]
    
    for color in colours:
        deck.append((color, 0))                      # 1 zero per color
        for num in range(1, 10):
            deck.extend([(color, num)] * 2)          # 2 of each 1-9
        for action in ["Skip", "Reverse", "+2"]:
            deck.extend([(color, action)] * 2)       # 2 of each action per color
    
    for _ in range(4):
        deck.append(("Black", "Wild"))
        deck.append(("Black", "+4"))
    
    return deck

def shuffle_deck(deck):
    random.shuffle(deck)
    return deck

def discard_pile():
    deck = shuffle_deck(card_deck())
    discard = [deck.pop(0)]
    
    card = discard[0]
    if card[0] == "Black":
      
        colors = ["Red", "Yellow", "Blue", "Green"]
        print("\nStarting card is Wild! Choose starting color:")
        for i, col in enumerate(colors, 1):
            print(f"  {i}: {colored(col, col)}")
        while True:
            try:
                col_idx = int(input("Enter number: ")) - 1
                if 0 <= col_idx < 4:
                    starting_color = colors[col_idx]
                    print(f"Starting color set to {colored(starting_color, starting_color)}")
                    break
            except:
                pass
        print("Invalid → defaulting to Red")
        starting_color = "Red"
        
    elif isinstance(card[1], str):
        print(f"Starting with action card: {card_to_str(card)} — it will affect the first player.")
    else:
        starting_color = card[0]
    
    return discard, deck, starting_color  # return starting_color too

def deal_hand():
    discard, deck, starting_color = discard_pile()
    player_hand = [deck.pop(0) for _ in range(7)]
    cpu_hand = [deck.pop(0) for _ in range(7)]
    return player_hand, cpu_hand, deck, discard, starting_color

def can_play(card, discard, current_color):
    return card[0] == "Black" or card[0] == current_color or card[1] == discard[-1][1]

def draw_card(deck, hand, count=1):
    for _ in range(count):
        if deck:
            hand.append(deck.pop(0))

def player_moves(player_hand, discard, deck, current_color):
    top_card = discard[-1]
    top_str = card_to_str(top_card)
    
    print(f"\n┌────────────────────────────────────────────┐")
    print(f"│ Current color: {colored(current_color, current_color):<10}  Top card: {top_str} │")
    print(f"└────────────────────────────────────────────┘")
    
    # Always show FULL hand with indices
    print("\nYour hand:")
    playable_indices = []  # track which positions are playable
    for i, card in enumerate(player_hand, 1):
        card_text = card_to_str(card)
        prefix = "→ " if can_play(card, discard, current_color) else "  "
        if prefix == "→ ":
            playable_indices.append(i)
        print(f"  {i:2d}: {prefix}{card_text}")
    
    print()  # small spacing
    
    valid_cards = [card for card in player_hand if can_play(card, discard, current_color)]
    
    if valid_cards:
        print("You can play these cards:")
        for i, card in enumerate(valid_cards, 1):
            print(f"  {i:2d}: {card_to_str(card)}")
        
        while True:
            try:
                choice = input("\nEnter number to play (or press Enter to draw): ").strip()
                if choice == "":
                    print("→ Drawing 1 card...")
                    draw_card(deck, player_hand)
                    # Official: after draw 1, you can play it if it matches
                    new_card = player_hand[-1]
                    if can_play(new_card, discard, current_color):
                        play_now = input(f"Drew {card_to_str(new_card)} — play it now? (y/n): ").lower()
                        if play_now == 'y':
                            print(f"You played {card_to_str(new_card)}")
                            discard.append(new_card)
                            player_hand.remove(new_card)
                            if new_card[0] == "Black":
                                colors = ["Red", "Yellow", "Blue", "Green"]
                                print("\nChoose next color:")
                                for j, col in enumerate(colors, 1):
                                    print(f"  {j}: {colored(col, col)}")
                                while True:
                                    try:
                                        col_idx = int(input("→ Enter number: ")) - 1
                                        if 0 <= col_idx < 4:
                                            color_choice = colors[col_idx]
                                            print(f"→ Color set to {colored(color_choice, color_choice)}")
                                            return new_card, color_choice, deck
                                    except:
                                        pass
                                print("Invalid → defaulting to Red")
                                return new_card, "Red", deck
                            action = new_card[1] if isinstance(new_card[1], str) else None
                            return new_card, action, deck
                    return None, None, deck
                
                card_index = int(choice) - 1
                if 0 <= card_index < len(valid_cards):
                    card_to_play = valid_cards[card_index]
                    print(f"You played {card_to_str(card_to_play)}")
                    discard.append(card_to_play)
                    player_hand.remove(card_to_play)
                    
                    # UNO! check
                    if len(player_hand) == 1:
                        input("You have 1 card left — say 'UNO!' (press Enter)...")
                    
                    if card_to_play[0] == "Black":
                        colors = ["Red", "Yellow", "Blue", "Green"]
                        print("\nChoose next color:")
                        for j, col in enumerate(colors, 1):
                            print(f"  {j}: {colored(col, col)}")
                        while True:
                            try:
                                col_idx = int(input("→ Enter number: ")) - 1
                                if 0 <= col_idx < 4:
                                    color_choice = colors[col_idx]
                                    print(f"→ Color set to {colored(color_choice, color_choice)}")
                                    return card_to_play, color_choice, deck
                            except:
                                pass
                        print("Invalid → defaulting to Red")
                        return card_to_play, "Red", deck
                    
                    action = card_to_play[1] if isinstance(card_to_play[1], str) else None
                    return card_to_play, action, deck
                else:
                    print(f"Number must be between 1 and {len(valid_cards)}")
            except ValueError:
                print("Please enter a number (or press Enter to draw)")
    else:
        print("No playable cards → drawing 1 card...")
        draw_card(deck, player_hand)
        if player_hand:
            new_card = player_hand[-1]
            print(f"  Drew: {card_to_str(new_card)}")
            # Official: check if drawable card can be played
            if can_play(new_card, discard, current_color):
                play_now = input("Play it now? (y/n): ").lower()
                if play_now == 'y':
                    print(f"You played {card_to_str(new_card)}")
                    discard.append(new_card)
                    player_hand.remove(new_card)
                    # UNO! check
                    if len(player_hand) == 1:
                        input("You have 1 card left — say 'UNO!' (press Enter)...")
                    if new_card[0] == "Black":
                        colors = ["Red", "Yellow", "Blue", "Green"]
                        print("\nChoose next color:")
                        for j, col in enumerate(colors, 1):
                            print(f"  {j}: {colored(col, col)}")
                        while True:
                            try:
                                col_idx = int(input("→ Enter number: ")) - 1
                                if 0 <= col_idx < 4:
                                    color_choice = colors[col_idx]
                                    print(f"→ Color set to {colored(color_choice, color_choice)}")
                                    return new_card, color_choice, deck
                            except:
                                pass
                        print("Invalid → defaulting to Red")
                        return new_card, "Red", deck
                    action = new_card[1] if isinstance(new_card[1], str) else None
                    return new_card, action, deck
        return None, None, deck

def cpu_moves(cpu_hand, discard, deck, current_color):
    valid_cards = [card for card in cpu_hand if can_play(card, discard, current_color)]
    if valid_cards:
        card_to_play = random.choice(valid_cards)
        print(f"CPU plays {card_to_str(card_to_play)}")
        discard.append(card_to_play)
        cpu_hand.remove(card_to_play)
        
        # UNO! for CPU
        if len(cpu_hand) == 1:
            print("CPU says UNO!")
        
        if card_to_play[0] == "Black":
            color_choice = random.choice(["Red", "Yellow", "Blue", "Green"])
            print(f"CPU chooses {colored(color_choice, color_choice)}")
            return card_to_play, color_choice, deck
        else:
            action = card_to_play[1] if isinstance(card_to_play[1], str) else None
            return card_to_play, action, deck
    
    print("CPU has no valid cards → draws 1 card.")
    draw_card(deck, cpu_hand)

    if cpu_hand:
        new_card = cpu_hand[-1]
        if can_play(new_card, discard, current_color):
            print(f"CPU drew {card_to_str(new_card)} and plays it!")
            discard.append(new_card)
            cpu_hand.remove(new_card)
            if len(cpu_hand) == 1:
                print("CPU says UNO!")
            if new_card[0] == "Black":
                color_choice = random.choice(["Red", "Yellow", "Blue", "Green"])
                print(f"CPU chooses {colored(color_choice, color_choice)}")
                return new_card, color_choice, deck
            else:
                action = new_card[1] if isinstance(new_card[1], str) else None
                return new_card, action, deck
    return None, None, deck

def gameplay():
    player_hand, cpu_hand, deck, discard, current_color = deal_hand()  # updated call
    turn_direction = 1
    skip_next = False  # for Skip / +2 / +4

    print("\n" + "="*50)
    print("               UNO GAME STARTED")
    print("="*50)

    while player_hand and cpu_hand:
        if skip_next:
            skip_next = False
            continue  # skip this turn

        if turn_direction == 1:
            print(f"\n{colored('PLAYER TURN', 'Yellow')}")
            player_card, action, deck = player_moves(player_hand, discard, deck, current_color)
            if player_card:
                current_color = player_card[0] if player_card[0] != "Black" else action
                if action == "Skip":
                    skip_next = True
                elif action == "Reverse":
                    turn_direction *= -1
                elif action in ["+2", "+4"]:
                    draw_count = 2 if action == "+2" else 4
                    draw_card(deck, cpu_hand, draw_count)
                    skip_next = True
        else:
            print(f"\n{colored('CPU TURN', 'Magenta')}")
            cpu_card, action, deck = cpu_moves(cpu_hand, discard, deck, current_color)
            if cpu_card:
                current_color = cpu_card[0] if cpu_card[0] != "Black" else action
                if action == "Skip":
                    skip_next = True
                elif action == "Reverse":
                    turn_direction *= -1
                elif action in ["+2", "+4"]:
                    draw_count = 2 if action == "+2" else 4
                    draw_card(deck, player_hand, draw_count)
                    skip_next = True

        print(f"Current color: {colored(current_color, current_color)}")
        print(f"  Player cards left: {len(player_hand)}")
        print(f"  CPU cards left:    {len(cpu_hand)}")

    print("\n" + "="*50)
    if not player_hand:
        print(colored("  YOU WIN!  ", "Green"))
    else:
        print(colored("  CPU WINS!  ", "Red"))
    print("="*50)

if __name__ == "__main__":
    gameplay()