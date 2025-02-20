import random

def card_deck():
    deck = []
    colours = ["Red", "Yellow", "Blue", "Green"]
    colours2 = ["Black"]
    special_card = ["Skip card", "Reverse Card", "Draw +2"]
    special_card2 = 2 * ["wild card", "draw +4"]

    for i in colours:
        for j in range(1, 10):
            deck.append((i, j))
    for i in colours:
        for j in special_card:
            deck.append((i, j))
    for i in colours2:
        for j in special_card2:
            deck.append((i, j))
    deck = deck * 2
    deck.extend([('Red', 0), ('Blue', 0), ('Yellow', 0), ('Green', 0)])
    return deck
    
def shuffle_deck(x):
    random.shuffle(x)
    return x

def discard_pile():
    updated_deck = shuffle_deck(card_deck())
    discard_pile = [updated_deck.pop(0)]
    return discard_pile, updated_deck

def deal_hand():
    player_hand = []
    cpu_hand = []
    deck = discard_pile()[1]
    for i in range(7):
        player_hand.append(deck.pop())
        cpu_hand.append(deck.pop())
    return player_hand, cpu_hand, deck

def can_play(card, discard):
    # Ensure discard contains a valid tuple
    if discard and isinstance(discard[-1], tuple):
        if card[0] == discard[-1][0] or card[1] == discard[-1][1]:
            return True
    return False

def player_moves(player_hand, discard):
    print("Your Hand:", player_hand)
    print("Discard Pile:", discard)

    valid_cards = [card for card in player_hand if can_play(card, discard)]

    if valid_cards:
        print("Which card would you like to play:")
        for i in range(len(valid_cards)):
            print(f"{i+1}: {valid_cards[i]}")

        userChoice = input(f"Choose a card to play from your hand: ")
        card_index = int(userChoice) - 1
        if 0 <= card_index < len(valid_cards):
            card_to_play = valid_cards[card_index]
            print(f"You played {card_to_play}")
            discard.append(card_to_play)
            player_hand.remove(card_to_play)
            return card_to_play
        else:
            print("Invalid choice. Try again.")
            return player_moves(player_hand, discard)  # Let player try again
    else:
        print("You have no playable cards.")
        return player_hand, discard

def cpu_moves(cpu_hand, discard):
    valid_cards = [card for card in cpu_hand if can_play(card, discard)]

    if valid_cards:
        card_to_play = random.choice(valid_cards)
        print(f"CPU plays {card_to_play}")
        discard.append(card_to_play)
        cpu_hand.remove(card_to_play)
        return card_to_play
    else:
        print("CPU has no valid cards to play")
        return None

def gameplay():
    discard, updated_deck = discard_pile()
    player_hand, cpu_hand, deck = deal_hand()

    while player_hand and cpu_hand:
        print("\n-- Player's turn!")
        player_card = player_moves(player_hand, discard)
        if player_card:
            discard = [player_card]  

        print("\n-- CPU's turn! --")
        cpu_card = cpu_moves(cpu_hand, discard)
        if cpu_card:
            discard = [cpu_card] 
            
        print(f"Updated Discard Pile: {discard}")

    print("Game Over!")

gameplay()