import random

def card_deck():
    deck = []
    colours = ["Red", "Yellow", "Blue", "Green"]
    colours2 = ["Black"]
    special_card = ["Skip card", "Reverse Card", "Draw +2"]
    special_card2 = 2 * ["wild card", "draw +4"]

    # Normal numbered cards
    for i in colours:
        for j in range(1, 10):
            deck.append((i, j))
    # Special cards (Skip, Reverse, Draw +2)
    for i in colours:
        for j in special_card:
            deck.append((i, j))
    # Wild cards and Draw +4 cards
    for i in colours2:
        for j in special_card2:
            deck.append((i, j))
    deck = deck * 2
    deck.extend([('Red', 0), ('Blue', 0), ('Yellow', 0), ('Green', 0)])  # Add one of each color zero
    return deck

def shuffle_deck(deck):
    random.shuffle(deck)
    return deck

def discard_pile():
    deck = shuffle_deck(card_deck())
    discard = [deck.pop(0)]  # Start with one card in the discard pile
    return discard, deck

def deal_hand():
    player_hand = []
    cpu_hand = []
    deck = discard_pile()[1]
    for i in range(7):  # Deal 7 cards to each player
        player_hand.append(deck.pop())
        cpu_hand.append(deck.pop())
    return player_hand, cpu_hand, deck

def can_play(card, discard):
    """Check if the card can be played on top of the discard pile."""
    return card[0] == discard[-1][0] or card[1] == discard[-1][1]

def player_moves(player_hand, discard):
    """Handle the player's turn."""
    print("Your Hand:", player_hand)
    print("Discard Pile:", discard)

    valid_cards = [card for card in player_hand if can_play(card, discard)]

    if valid_cards:
        print("Which card would you like to play?", valid_cards)
        card_to_play = input(f"Choose a card to play from your hand: {valid_cards} ")

        # Ensure the user picks a valid card from the list
        card_to_play = tuple(card_to_play.split(","))
        card_to_play = (card_to_play[0].strip(), card_to_play[1].strip())

        if card_to_play in valid_cards:
            print(f"You played {card_to_play}")
            discard.append(card_to_play)
            player_hand.remove(card_to_play)
            return player_hand, discard
        else:
            print("Invalid choice. Try again.")
            return player_moves(player_hand, discard)  # Retry the player's move
    else:
        print("You have no playable cards. Drawing a card.")
        return player_hand, discard  # If no valid cards, return the same hand and discard

def cpu_moves(cpu_hand, discard):
    """Handle the CPU's turn."""
    valid_cards = [card for card in cpu_hand if can_play(card, discard)]

    if valid_cards:
        card_to_play = random.choice(valid_cards)
        print(f"CPU plays {card_to_play}")
        discard.append(card_to_play)
        cpu_hand.remove(card_to_play)
        return cpu_hand, discard
    else:
        print("CPU has no valid cards to play. Drawing a card.")
        return cpu_hand, discard  # If CPU can't play, just return hand and discard

def gameplay():
    """Game loop."""
    discard, updated_deck = discard_pile()
    player_hand, cpu_hand, deck = deal_hand()

    while player_hand and cpu_hand:
        print("\n-- Player's turn!")
        player_hand, discard = player_moves(player_hand, discard)
        if not player_hand:  # If player runs out of cards, end game
            print("Player wins!")
            break

        print("\n-- CPU's turn!")
        cpu_hand, discard = cpu_moves(cpu_hand, discard)
        if not cpu_hand:  # If CPU runs out of cards, end game
            print("CPU wins!")
            break
        
        print(f"Updated Discard Pile: {discard}")        

    print("Game Over!")

gameplay()
