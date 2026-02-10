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
    special_card = ["Skip", "Reverse", "+2"]
    special_card2 = 2 * ["Wild", "+4"]
    for color in colours:
        for num in range(1, 10):
            deck.append((color, num))
        for special in special_card:
            deck.append((color, special))
    for special in special_card2:
        deck.append(("Black", special))
    deck = deck * 2
    deck.extend([(color, 0) for color in colours])
    return deck


def shuffle_deck(deck):
    random.shuffle(deck)
    return deck


def discard_pile():
    deck = shuffle_deck(card_deck())
    discard = [deck.pop(0)]
    while not isinstance(discard[0][1], int):
        deck.append(discard.pop(0))
        random.shuffle(deck)
        discard.append(deck.pop(0))
    return discard, deck


def deal_hand():
    discard, deck = discard_pile()
    return [deck.pop() for _ in range(7)], [deck.pop() for _ in range(7)], deck, discard


def can_play(card, discard, current_color):
    return card[0] == "Black" or card[0] == current_color or card[1] == discard[-1][1]


def draw_card(deck, hand, count=1):
    for _ in range(count):
        if deck:
            hand.append(deck.pop(0))


def player_moves(player_hand, discard, deck, current_color):
    print("\nYour Hand:")
    for i, card in enumerate(player_hand, 1):
        print(f"  {i:2d}: {card_to_str(card)}", end="")
        if i % 5 == 0:
            print()
    if len(player_hand) % 5 != 0:
        print()

    print(f"\nDiscard Pile: {card_to_str(discard[-1])}")

    valid_cards = [card for card in player_hand if can_play(card, discard, current_color)]
    
    if valid_cards:
        print("\nWhich card would you like to play:")
        for i, card in enumerate(valid_cards, 1):
            print(f"  {i}: {card_to_str(card)}")
        
        try:
            card_index = int(input("\nChoose a card to play (number): ")) - 1
            if 0 <= card_index < len(valid_cards):
                card_to_play = valid_cards[card_index]
                print(f"You played {card_to_str(card_to_play)}")
                discard.append(card_to_play)
                player_hand.remove(card_to_play)

                if card_to_play[0] == "Black":
                    colors = ["Red", "Yellow", "Blue", "Green"]
                    print("\nChoose a color:")
                    for i, col in enumerate(colors, 1):
                        print(f"  {i}: {colored(col, col)}")
                    try:
                        color_choice = colors[int(input("Enter number: ")) - 1]
                        print(f"→ Next color is {colored(color_choice, color_choice)}")
                        return card_to_play, color_choice, deck
                    except:
                        print("Invalid color choice → defaulting to Red")
                        return card_to_play, "Red", deck
                else:
                    action = card_to_play[1] if isinstance(card_to_play[1], str) else None
                    return card_to_play, action, deck
        except ValueError:
            print("Invalid input.")
    
    print("You have no playable cards. Drawing 1 card.")
    draw_card(deck, player_hand)
    return None, None, deck


def cpu_moves(cpu_hand, discard, deck, current_color):
    valid_cards = [card for card in cpu_hand if can_play(card, discard, current_color)]
    if valid_cards:
        card_to_play = random.choice(valid_cards)
        print(f"CPU plays {card_to_str(card_to_play)}")
        discard.append(card_to_play)
        cpu_hand.remove(card_to_play)

        if card_to_play[0] == "Black":
            color_choice = random.choice(["Red", "Yellow", "Blue", "Green"])
            print(f"CPU chooses {colored(color_choice, color_choice)}")
            return card_to_play, color_choice, deck
        else:
            action = card_to_play[1] if isinstance(card_to_play[1], str) else None
            return card_to_play, action, deck
    
    print("CPU has no valid cards → draws 1 card.")
    draw_card(deck, cpu_hand)
    return None, None, deck


def gameplay():
    player_hand, cpu_hand, deck, discard = deal_hand()
    turn_direction = 1
    current_color = discard[-1][0]

    print("\n" + "="*50)
    print("               UNO GAME STARTED")
    print("="*50)

    while player_hand and cpu_hand:
        if turn_direction == 1:
            print(f"\n{colored('PLAYER TURN', 'Yellow')}")
            player_card, action, deck = player_moves(player_hand, discard, deck, current_color)
            if player_card:
                current_color = player_card[0] if player_card[0] != "Black" else action
                if action in ["Skip", "Reverse"]:
                    turn_direction *= -1
                elif action in ["+2", "+4"]:
                    draw_card(deck, cpu_hand, int(action[1:]))
                    turn_direction = -1
        else:
            print(f"\n{colored('CPU TURN', 'Magenta')}")
            cpu_card, action, deck = cpu_moves(cpu_hand, discard, deck, current_color)
            if cpu_card:
                current_color = cpu_card[0] if cpu_card[0] != "Black" else action
                if action in ["Skip", "Reverse"]:
                    turn_direction *= -1
                elif action in ["+2", "+4"]:
                    draw_card(deck, player_hand, int(action[1:]))
                    turn_direction = 1

        print(f"Current color: {colored(current_color, current_color)}")
        print(f"  Player cards left: {len(player_hand)}")
        print(f"  CPU cards left:    {len(cpu_hand)}")

    print("\n" + "="*50)
    if not player_hand:
        print(colored("  YOU WIN!  ", "Green", bright=True))
    else:
        print(colored("  CPU WINS!  ", "Red", bright=True))
    print("="*50)


if __name__ == "__main__":
    gameplay()