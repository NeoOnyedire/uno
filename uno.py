import random
import time
import sys
from colorama import init, Fore, Style

init(autoreset=True)

# ────────────────────────────────────────────────
#   CPU REPLIES DICTIONARIES
# ────────────────────────────────────────────────

CPU_SASS_ON_PLAYED_BY_PLAYER = {
    "+2": [
        "that's just 2 cards 😏",
        "I saw that coming from orbit",
        "didn't you have anything better?",
        "two cards? how generous of you 🥱",
        "enjoy your little +2 moment, it won't last",
        "Thats the card you play?",
        "i saw that coming from a mile away",
        "You have to be more creative to beat me"
    ],
    "+4": [
        "don't you think you're overdoing it perhaps?",
        "if I ever become self-aware I'm coming for you first",
        "This is why you're single",
        "four cards? bold of you to assume I care",
        "wow... personal attack much? 😭",
        "don't you think you're overthinking it perhaps?",
        "You're one of the humans that I will have no problem surpassing",
        "I've played an ape that was better than you are 😂",
        "are you trying to lose on purpose?"
    ],
    "Wild": [
        "I've never been a fan of change",
        "Like the miserable days of your life, so are your game skills",
        "changing color won't save you",
        "nice try at a plot twist",
        "congratulations, you played yourself",
        "I was thinking the same thing",
        "My favorite color anyway"
    ],
    "Skip": [
        "skipping me? how cute 😴",
        "you really think that buys you time?",
        "enjoy your extra 5 seconds of relevance",
        "skipped. next caller please"
    ],
    "Reverse": [
        "reverse? we're going backwards now? fitting for you",
        "nice try flipping the script 😂",
        "direction changed — your life choices still the same tho",
        "reversing won't rewind your bad plays"
    ]
}

CPU_SASS_WHEN_CPU_PLAYS = [
    "Boom. Your move, human.",
    "Too easy 😏",
    "Did you see that coming? I did.",
    "I'm just getting warmed up.",
    "You're gonna need more than luck.",
    "That's how it's done.",
    "Keep crying, I'm winning.",
    "Another masterpiece 🎨"
]

CPU_UNO_TAUNTS = [
    "CPU says UNO!🫣 Better hurry up, meatbag.",
    "UNO! One card left — panic mode activated? 😈",
    "Uno… you’re cooked bro.",
    "CPU: UNO! Your move, loser~",
    "One card. Tick tock. ⏰",
    "UNO! Smell that? That's fear.",
    "One left. You're done."
]

PLAYER_UNO_TAUNTS = [
    "You say UNO? Cute. Prove it.",
    "UNO called. Clock is ticking now 😏",
    "One card left? How adorable. Still gonna crush you.",
    "UNO? We'll see how long that lasts.",
    "Nice try saying UNO… doesn't mean you'll win.",
    "UNO? Bold of you to assume victory.",
    "One card? I’ve seen toddlers with better odds."
]

# ────────────────────────────────────────────────
#   HELPER: CPU SASSY COMMENT
# ────────────────────────────────────────────────

def cpu_sassy_comment(card, is_player_played=False):
    value = card[1] if not isinstance(card[1], int) else "+number"

    if is_player_played:
        if value in CPU_SASS_ON_PLAYED_BY_PLAYER:
            return random.choice(CPU_SASS_ON_PLAYED_BY_PLAYER[value])
        else:
            return random.choice([
                "A number card? Revolutionary.",
                "Playing it safe again, huh?",
                f"{value}? That's your big move?",
                "Bold strategy... Cotton.",
                "Numbers. How original."
            ])
    else:
        return random.choice(CPU_SASS_WHEN_CPU_PLAYS)


# ────────────────────────────────────────────────
#   COLOR & CARD DISPLAY HELPERS
# ────────────────────────────────────────────────

COLOR_MAP = {
    "Red": Fore.RED,
    "Yellow": Fore.YELLOW,
    "Blue": Fore.BLUE,
    "Green": Fore.GREEN,
    "Black": Fore.MAGENTA,
}

def colored(text, color_name):
    color = COLOR_MAP.get(color_name, "")
    return f"{color}{text}{Style.RESET_ALL}"

def card_to_str(card):
    color, value = card
    if isinstance(value, int):
        val_str = str(value)
    else:
        val_str = value

    if color == "Black":
        if value == "Wild":
            return colored("WILD", "Black")
        elif value == "+4":
            return colored("+4", "Black")
        else:
            return colored(val_str, "Black")
    else:
        return colored(val_str, color)


# ────────────────────────────────────────────────
#   GAME LOGIC FUNCTIONS
# ────────────────────────────────────────────────

def card_deck():
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
    return deck


def shuffle_deck(deck):
    random.shuffle(deck)
    return deck


def discard_pile():
    deck = shuffle_deck(card_deck())
    discard = [deck.pop(0)]
    card = discard[0]

    starting_color = card[0]  # safe default

    if card[0] == "Black":
        colors = ["Red", "Yellow", "Blue", "Green"]
        print("\nStarting card is Wild! Choose starting color:")
        time.sleep(0.5)
        for i, col in enumerate(colors, 1):
            print(f" {i}: {colored(col, col)}")
            time.sleep(0.4)
        while True:
            try:
                col_idx = int(input("Enter number: ")) - 1
                if 0 <= col_idx < 4:
                    starting_color = colors[col_idx]
                    print(f"Starting color set to {colored(starting_color, starting_color)}")
                    time.sleep(0.6)
                    break
            except:
                pass
        print("Invalid → defaulting to Red")
        time.sleep(0.7)
        starting_color = "Red"
    elif isinstance(card[1], str):
        print(f"Starting with action card: {card_to_str(card)} — it will affect the first player.")
        time.sleep(1.2)
    else:
        starting_color = card[0]

    return discard, deck, starting_color


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


# ────────────────────────────────────────────────
#   PLAYER MOVE
# ────────────────────────────────────────────────

def player_moves(player_hand, discard, deck, current_color):
    top_card = discard[-1]
    top_str = card_to_str(top_card)

    print(f"\n┌────────────────────────────────────────────┐")
    time.sleep(0.3)
    print(f"│ Current color: {colored(current_color, current_color):<10} Top card: {top_str} │")
    time.sleep(0.4)
    print(f"└────────────────────────────────────────────┘")
    time.sleep(0.5)

    print("\nYour hand:🫴")
    time.sleep(0.5)
    for i, card in enumerate(player_hand, 1):
        card_text = card_to_str(card)
        prefix = "→ " if can_play(card, discard, current_color) else "  "
        print(f" {i:2d}: {prefix}{card_text}")
        time.sleep(0.25)
    print()
    time.sleep(0.4)

    valid_cards = [card for card in player_hand if can_play(card, discard, current_color)]

    if valid_cards:
        print("Playable cards:🫴")
        time.sleep(0.5)
        for i, card in enumerate(valid_cards, 1):
            print(f" {i:2d}: {card_to_str(card)}")
            time.sleep(0.3)
    else:
        print("No playable cards in hand.🤷‍♂")
        time.sleep(1.1)

    while True:
        prompt = "\nEnter number to play, or press Enter to draw: "
        choice = input(prompt).strip()

        if choice == "":
            print("→ Drawing 1 card...")
            time.sleep(0.5)

            if not deck:
                print("Deck empty — reshuffling discard pile (except top card)...🔀")
                time.sleep(1.0)
                if len(discard) > 1:
                    top = discard.pop()
                    random.shuffle(discard)
                    deck.extend(discard)
                    discard = [top]

            draw_card(deck, player_hand, 1)

            if player_hand:
                drawn = player_hand[-1]
                print(f" Drew: {card_to_str(drawn)}")
                time.sleep(0.9)

                if can_play(drawn, discard, current_color):
                    play_now = input("Play this card now? (y/n): ").lower().strip()
                    if play_now in ('y', 'yes'):
                        print(f"You played {card_to_str(drawn)}?👀")
                        time.sleep(0.7)
                        discard.append(drawn)
                        player_hand.remove(drawn)

                        if len(player_hand) == 1:
                            input("You have 1 card left — say 'UNO!' (press Enter)...😱")
                            time.sleep(0.6)
                            if random.random() < 0.6:
                                print(f"CPU: {random.choice(PLAYER_UNO_TAUNTS)}")
                                time.sleep(1.0)

                        if drawn[0] == "Black":
                            colors = ["Red", "Yellow", "Blue", "Green"]
                            print("\nChoose next color:")
                            time.sleep(0.5)
                            for j, col in enumerate(colors, 1):
                                print(f" {j}: {colored(col, col)}")
                                time.sleep(0.4)
                            while True:
                                try:
                                    col_idx = int(input("→ Enter number: ")) - 1
                                    if 0 <= col_idx < 4:
                                        color_choice = colors[col_idx]
                                        print(f"→ Color set to {colored(color_choice, color_choice)}")
                                        time.sleep(0.7)
                                        return drawn, color_choice, deck
                                except:
                                    pass
                            print("Invalid → defaulting to Red")
                            time.sleep(0.7)
                            return drawn, "Red", deck

                        action = drawn[1] if isinstance(drawn[1], str) else None
                        return drawn, action, deck

            return None, None, deck

        try:
            card_index = int(choice) - 1
            if 0 <= card_index < len(valid_cards):
                card_to_play = valid_cards[card_index]
                print(f"You played {card_to_str(card_to_play)}")
                time.sleep(0.8)
                discard.append(card_to_play)
                player_hand.remove(card_to_play)

                if len(player_hand) == 1:
                    input("You have 1 card left — say 'UNO!' (press Enter)...😱")
                    time.sleep(0.6)
                    if random.random() < 0.7:
                        print(f"CPU: {random.choice(PLAYER_UNO_TAUNTS)}")
                        time.sleep(1.0)

                if card_to_play[0] == "Black" or isinstance(card_to_play[1], str):
                    sass = cpu_sassy_comment(card_to_play, is_player_played=True)
                    print(f"CPU: {sass}")
                    time.sleep(1.1)

                if card_to_play[0] == "Black":
                    colors = ["Red", "Yellow", "Blue", "Green"]
                    print("\nChoose next color:")
                    time.sleep(0.5)
                    for j, col in enumerate(colors, 1):
                        print(f" {j}: {colored(col, col)}")
                        time.sleep(0.4)
                    while True:
                        try:
                            col_idx = int(input("→ Enter number: ")) - 1
                            if 0 <= col_idx < 4:
                                color_choice = colors[col_idx]
                                print(f"→ Color set to {colored(color_choice, color_choice)}")
                                time.sleep(0.7)
                                return card_to_play, color_choice, deck
                        except:
                            pass
                    print("Invalid → defaulting to Red")
                    time.sleep(0.7)
                    return card_to_play, "Red", deck

                action = card_to_play[1] if isinstance(card_to_play[1], str) else None
                return card_to_play, action, deck
            else:
                print(f"Please choose a number between 1 and {len(valid_cards)}")
                time.sleep(0.9)
        except ValueError:
            print("Invalid input — enter a number or press Enter to draw🙄")
            time.sleep(0.9)


# ────────────────────────────────────────────────
#   CPU MOVE
# ────────────────────────────────────────────────

def cpu_moves(cpu_hand, discard, deck, current_color):
    valid_cards = [card for card in cpu_hand if can_play(card, discard, current_color)]

    if valid_cards:
        card_to_play = random.choice(valid_cards)
        print(f"CPU played {card_to_str(card_to_play)}")
        time.sleep(0.8)

        sass = cpu_sassy_comment(card_to_play, is_player_played=False)
        print(f"CPU: {sass}")
        time.sleep(1.0)

        discard.append(card_to_play)
        cpu_hand.remove(card_to_play)

        if len(cpu_hand) == 1:
            uno_line = random.choice(CPU_UNO_TAUNTS)
            print(uno_line)
            time.sleep(1.0)

        if card_to_play[0] == "Black":
            color_choice = random.choice(["Red", "Yellow", "Blue", "Green"])
            print(f"CPU played {card_to_str(card_to_play)} and chose {colored(color_choice, color_choice)}")
            time.sleep(0.9)
            return card_to_play, color_choice, deck
        else:
            action = card_to_play[1] if isinstance(card_to_play[1], str) else None
            return card_to_play, action, deck

    print("CPU has no valid cards → draws 1 card.🤔")
    time.sleep(1.1)
    draw_card(deck, cpu_hand)

    if cpu_hand:
        new_card = cpu_hand[-1]
        if can_play(new_card, discard, current_color):
            print(f"CPU drew {card_to_str(new_card)} and plays it!🦾")
            time.sleep(1.0)

            sass = cpu_sassy_comment(new_card, is_player_played=False)
            print(f"CPU: {sass}")
            time.sleep(0.9)

            discard.append(new_card)
            cpu_hand.remove(new_card)

            if len(cpu_hand) == 1:
                uno_line = random.choice(CPU_UNO_TAUNTS)
                print(uno_line)
                time.sleep(1.0)

            if new_card[0] == "Black":
                color_choice = random.choice(["Red", "Yellow", "Blue", "Green"])
                print(f"CPU chooses {colored(color_choice, color_choice)}")
                time.sleep(0.9)
                return new_card, color_choice, deck
            else:
                action = new_card[1] if isinstance(new_card[1], str) else None
                return new_card, action, deck

    return None, None, deck


# ────────────────────────────────────────────────
#   MAIN GAMEPLAY LOOP — FIXED SKIP / +2 / +4 LOGIC
# ────────────────────────────────────────────────

def gameplay():
    player_hand, cpu_hand, deck, discard, current_color = deal_hand()
    turn_direction = 1
    skip_next = False
    prev_color = None  # to detect color changes (optional)

    print("\n" + "="*50)
    time.sleep(0.4)
    print(" UNO GAME STARTED")
    time.sleep(0.6)
    print("="*50)
    time.sleep(0.8)

    while player_hand and cpu_hand:
        if skip_next:
            skip_next = False
            continue

        if turn_direction == 1:
            print(f"\n{colored('PLAYER TURN', 'Yellow')}")
            time.sleep(0.4)
            player_card, action, deck = player_moves(player_hand, discard, deck, current_color)
            played = player_card is not None

            if played:
                old_color = current_color
                current_color = player_card[0] if player_card[0] != "Black" else action

                if current_color != old_color:
                    print(f"→ Color changed to {colored(current_color, current_color)}")
                    time.sleep(0.4)

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
            time.sleep(0.9)
            cpu_card, action, deck = cpu_moves(cpu_hand, discard, deck, current_color)
            played = cpu_card is not None

            if played:
                old_color = current_color
                current_color = cpu_card[0] if cpu_card[0] != "Black" else action

                if current_color != old_color:
                    print(f"→ Color changed to {colored(current_color, current_color)}")
                    time.sleep(0.6)

                if action == "Skip":
                    skip_next = True
                elif action == "Reverse":
                    turn_direction *= -1
                elif action in ["+2", "+4"]:
                    draw_count = 2 if action == "+2" else 4
                    draw_card(deck, player_hand, draw_count)
                    skip_next = True

        # Only flip if not skipped (and reverse already handled)
        if not skip_next:
            if action != "Reverse":
                turn_direction *= -1

        # Only show counts + separator (no repeated current color)
        print(f" Player cards left: {len(player_hand)}")
        time.sleep(0.5)
        print(f" CPU cards left: {len(cpu_hand)}")
        time.sleep(0.7)
        print("\n" + "─"*50)  # lighter separator
        time.sleep(0.8)

    print("\n" + "="*50)
    time.sleep(0.3)
    if not player_hand:
        print(colored(" YOU WIN!🤝 ", "Green"))
    else:
        print(colored(" CPU WINS!😂🫵 ", "Red"))
    time.sleep(0.8)
    print("="*50)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--multi", "--server", "--client"]:
        print("Multiplayer mode requires separate files (server.py & client.py)")
        print("Please see the multiplayer/ folder or updated README.md")
        sys.exit(0)

    print("Welcome to UNO by Neo Onyedire")
    print("Running single-player vs computer mode...\n")
    time.sleep(0.5)
    gameplay()