import random

def card_deck():
    deck = []
    colours = ["Red", "Yellow", "Blue", "Green"]
    colours2 = ["Black"]
    special_card = ["Skip", "Reverse", "+2"]
    special_card2 = 2 * ["Wild", "+4"]

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
    while not isinstance(discard_pile[0][1], int):  # Check if the second element is an integer (i.e., a number card)
        updated_deck.append(discard_pile[0])  # Put the special card back into the deck
        random.shuffle(updated_deck)  # Shuffle the deck again to maintain randomness
        discard_pile[0] = updated_deck.pop(0)  # Pop the next card from the shuffled deck

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
    #Allows black cards to be played on any card
    if card[0] == "Black":
        return True

    # Ensure discard contains a valid tuple
    if discard and isinstance(discard[-1], tuple):
        if card[0] == discard[-1][0] or card[1] == discard[-1][1]:
            return True
    return False

def player_moves(player_hand, discard, deck):
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

              # all black cards are wild cards
            if card_to_play[0] == "Black":
                print("You played a Wild card!")
                color_choice = input("Enter the color (Red, Yellow, Blue, Green): ")
                print(f"Next color is {color_choice}.")
                return card_to_play, color_choice, deck
            elif card_to_play[1] == "Skip":
                return card_to_play, "skip", deck
            elif card_to_play[1] == "Reverse":
                return card_to_play, "reverse", deck
            elif card_to_play[1] == "+2":
                return card_to_play, "draw_2", deck
            elif card_to_play[1] == "+4":
                return card_to_play, "draw_4", deck
            else:
                return card_to_play, None, deck
        else:
            print("Invalid choice. Try again.")
            return player_moves(player_hand, discard, deck)
    else:
        print("You have no playable cards. You must draw a card.")
        if deck:
            drawn_card = deck.pop(0)
            player_hand.append(drawn_card)
            print(f"You drew a card: {drawn_card}")
        return None, None, deck

def cpu_moves(cpu_hand, discard, deck):
    valid_cards = [card for card in cpu_hand if can_play(card, discard)]

    if valid_cards:
        card_to_play = random.choice(valid_cards)
        print(f"CPU plays {card_to_play}")
        discard.append(card_to_play)
        cpu_hand.remove(card_to_play)
        
         # special cards and stuff
        if card_to_play[0] == "Black":
            print("CPU played a Wild card!")
            color_choice = random.choice(["Red", "Yellow", "Blue", "Green"])
            print(f"CPU chooses the color {color_choice}.")
            return card_to_play, color_choice, deck
        elif card_to_play[1] == "Skip card":
            return card_to_play, "skip", deck
        elif card_to_play[1] == "Reverse Card":
            return card_to_play, "reverse", deck
        elif card_to_play[1] == "+2":
            return card_to_play, "draw_2", deck
        elif card_to_play[1] == "+4":
            return card_to_play, "draw_4", deck
        else:
            return card_to_play, None, deck
    else:
        print("CPU has no valid cards to play. CPU draws a card.")
        if deck:
            drawn_card = deck.pop(0)
            cpu_hand.append(drawn_card)
            print(f"CPU drew a card: {drawn_card}")
        return None, None, deck


def gameplay():
    discard, updated_deck = discard_pile()
    player_hand, cpu_hand, deck = deal_hand()

    turn_direction = 1  # 1 for player -> cpu, -1 for cpu -> player
    current_color = discard[-1][0]  # Set the current color based on the first card in the discard pile.

    while player_hand and cpu_hand:
        if turn_direction == 1:  # Player's turn
            print("\n-- Player's turn!")
            player_card, action, updated_deck = player_moves(player_hand, discard, updated_deck)
            
            if player_card:
                discard.append(player_card)

            if action == "skip":
                print("Player skips CPU's turn.")
                turn_direction = -1  # Skip CPU's turn

            elif action == "reverse":
                print("Reverse the order of play.")
                turn_direction *= -1  # Reverse the direction

            elif action == "draw_2":
                print("CPU draws 2 cards!")
                for _ in range(2):
                    cpu_hand.append(updated_deck.pop(0))  # CPU draws 2 cards
                turn_direction = -1  # Change turn

            elif action == "draw_4":
                print("CPU draws 4 cards!")
                for _ in range(4):
                    cpu_hand.append(updated_deck.pop(0))  # CPU draws 4 cards
                turn_direction = -1  # Change turn

            elif action == "wild":
                # Wild card: Player chose a color, now update the current color
                print(f"The next color is {action}.")
                current_color = action  # Set the chosen color as the next color

        if turn_direction == -1:  # CPU's turn
            print("\n-- CPU's turn!")
            cpu_card, action, updated_deck = cpu_moves(cpu_hand, discard, updated_deck)
            
            if cpu_card:
                discard = [cpu_card]

            if action == "skip":
                print("CPU skips player's turn.")
                turn_direction = 1  # Skip player's turn

            elif action == "reverse":
                print("Reverse the order of play.")
                turn_direction *= -1  # Reverse the direction

            elif action == "draw_2":
                print("Player draws 2 cards!")
                for _ in range(2):
                    player_hand.append(updated_deck.pop(0))  # Player draws 2 cards
                turn_direction = 1  # Change turn

            elif action == "draw_4":
                print("Player draws 4 cards!")
                for _ in range(4):
                    player_hand.append(updated_deck.pop(0))  # Player draws 4 cards
                turn_direction = 1  # Change turn

            elif action == "wild":
                # Wild card: CPU chose a color, now update the current color
                print(f"The next color is {action}.")
                current_color = action  # Set the chosen color as the next color

        print(f"Updated Discard Pile: {discard}")
        print(f"Current Color: {current_color}")

        if not player_hand:
            print("Congratulations! You win!")
        elif not cpu_hand:
            print("CPU wins! Better luck next time.")
    
    print("Game Over!")

gameplay()