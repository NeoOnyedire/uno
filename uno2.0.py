import random

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
    print("Your Hand:", player_hand)
    print("Discard Pile:", discard[-1])
    
    valid_cards = [card for card in player_hand if can_play(card, discard, current_color)]
    
    if valid_cards:
        print("Which card would you like to play:")
        for i, card in enumerate(valid_cards, 1):
            print(f"{i}: {card}")
        
        try:
            card_index = int(input("Choose a card to play from your hand: ")) - 1
            if 0 <= card_index < len(valid_cards):
                card_to_play = valid_cards[card_index]
                print(f"You played {card_to_play}")
                discard.append(card_to_play)
                player_hand.remove(card_to_play)
                
                if card_to_play[0] == "Black":
                    colors = ["Red", "Yellow", "Blue", "Green"]
                    print("Choose a color:")
                    for i, color in enumerate(colors, 1):
                        print(f"{i}: {color}")
                    color_choice = colors[int(input("Enter the number of your color choice: ")) - 1]
                    print(f"Next color is {color_choice}.")
                    return card_to_play, color_choice, deck
                return card_to_play, card_to_play[1] if isinstance(card_to_play[1], str) else None, deck
        except ValueError:
            print("Invalid input. Try again.")
    
    print("You have no playable cards. You must draw a card.")
    draw_card(deck, player_hand)
    return None, None, deck


def cpu_moves(cpu_hand, discard, deck, current_color):
    valid_cards = [card for card in cpu_hand if can_play(card, discard, current_color)]
    
    if valid_cards:
        card_to_play = random.choice(valid_cards)
        print(f"CPU plays {card_to_play}")
        discard.append(card_to_play)
        cpu_hand.remove(card_to_play)
        
        if card_to_play[0] == "Black":
            color_choice = random.choice(["Red", "Yellow", "Blue", "Green"])
            print(f"CPU chooses the color {color_choice}.")
            return card_to_play, color_choice, deck
        return card_to_play, card_to_play[1] if isinstance(card_to_play[1], str) else None, deck
    
    print("CPU has no valid cards to play. CPU draws a card.")
    draw_card(deck, cpu_hand)
    return None, None, deck


def gameplay():
    player_hand, cpu_hand, deck, discard = deal_hand()
    turn_direction = 1
    current_color = discard[-1][0]
    
    while player_hand and cpu_hand:
        if turn_direction == 1:
            print("\n-- Player's turn!")
            player_card, action, deck = player_moves(player_hand, discard, deck, current_color)
            if player_card:
                current_color = player_card[0] if player_card[0] != "Black" else action
            if action in ["Skip", "Reverse"]:
                turn_direction *= -1
            elif action in ["+2", "+4"]:
                draw_card(deck, cpu_hand, int(action[1]))
                turn_direction = -1
        else:
            print("\n-- CPU's turn!")
            cpu_card, action, deck = cpu_moves(cpu_hand, discard, deck, current_color)
            if cpu_card:
                current_color = cpu_card[0] if cpu_card[0] != "Black" else action
            if action in ["Skip", "Reverse"]:
                turn_direction *= -1
            elif action in ["+2", "+4"]:
                draw_card(deck, player_hand, int(action[1]))
                turn_direction = 1
        print(f"Current Color: {current_color}")
    
    print("Game Over!", "You win!" if not player_hand else "CPU wins!")

gameplay()
