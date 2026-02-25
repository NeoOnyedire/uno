# multiplayer/game_logic.py
import random
import json
from colorama import init, Fore, Style
init(autoreset=True)

# Reuse your COLOR_MAP and colored() and card_to_str() — copy them here
# (or import from main file if you refactor later)

# Simple color mapping
COLOR_MAP = {
    "Red": Fore.RED,
    "Yellow": Fore.YELLOW,
    "Blue": Fore.BLUE,
    "Green": Fore.GREEN,
    "Black": Fore.MAGENTA, # using magenta for wilds (looks good in most terminals)
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
        val_str = value # Skip, Reverse, +2, Wild, +4
    
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


def create_deck():
    # Almost same as your card_deck()
    deck = []
    colours = ["Red", "Yellow", "Blue", "Green"]
    for color in colours:
        deck.append((color, 0))
        for num in range(1, 10):
            deck.extend([(color, num)] * 2)
        for action in ["Skip", "Reverse", "+2"]:
            deck.extend([(color, action)] * 2)
    for _ in range(4):
        deck.append(("Black", "Wild"))
        deck.append(("Black", "+4"))
    random.shuffle(deck)
    return deck

def can_play(card, top_card, current_color):
    return (
        card[0] == "Black" or
        card[0] == current_color or
        card[1] == top_card[1]
    )

# We'll serialize cards as simple lists or tuples
def card_to_json(card):
    return [card[0], card[1]]

def json_to_card(j):
    return (j[0], j[1] if isinstance(j[1], int) else j[1])