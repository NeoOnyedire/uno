# multiplayer/server.py
import socket
import threading
import json
import time
from game_logic import create_deck, can_play, card_to_json, json_to_card, card_to_str, colored

HOST = "0.0.0.0"          # Listen on all interfaces
PORT = 55555              # Choose any free port > 1024

clients = []              # list of (conn, addr, name, hand)
current_turn = 0
deck = []
discard = []
current_color = ""
direction = 1
skip_next = False

def broadcast(message):
    for conn, _, _, _ in clients:
        try:
            conn.send((message + "\n").encode())
        except:
            pass

def send_to_player(idx, message):
    if 0 <= idx < len(clients):
        try:
            clients[idx][0].send((message + "\n").encode())
        except:
            pass

def game_state_for_player(idx):
    me = clients[idx]
    top = discard[-1] if discard else None
    state = {
        "your_hand": [card_to_json(c) for c in me[3]],
        "top_card": card_to_json(top) if top else None,
        "current_color": current_color,
        "your_turn": (idx == current_turn),
        "players": [{"name": n, "card_count": len(h)} for _,_,n,h in clients],
        "direction": "clockwise" if direction == 1 else "counter-clockwise"
    }
    return json.dumps({"type": "state", **state})

def start_game():
    global deck, discard, current_color, current_turn
    deck = create_deck()
    discard = [deck.pop()]
    top = discard[0]

    if top[0] == "Black":
        current_color = random.choice(["Red","Yellow","Blue","Green"])
    else:
        current_color = top[0]

    # Deal hands
    for _,_,_,hand in clients:
        hand[:] = [deck.pop() for _ in range(7)]

    broadcast("GAME STARTED!")
    broadcast_state()

def broadcast_state():
    for i in range(len(clients)):
        send_to_player(i, game_state_for_player(i))

def handle_client(conn, addr):
    conn.send("Welcome! Enter your name: ".encode())
    name = conn.recv(1024).decode().strip() or f"Player{len(clients)+1}"
    
    hand = []
    clients.append((conn, addr, name, hand))
    broadcast(f"{name} has joined the game!")

    if len(clients) == 2:
        start_game()
        threading.Thread(target=game_loop, daemon=True).start()

    while True:
        try:
            data = conn.recv(1024).decode().strip()
            if not data: break

            msg = json.loads(data)
            msg_type = msg.get("type")

            if msg_type == "play_card":
                player_idx = [c[2] for c in clients].index(name)
                if player_idx != current_turn:
                    send_to_player(player_idx, json.dumps({"type":"error", "msg":"Not your turn"}))
                    continue

                card_idx = msg["card_index"]
                if 0 <= card_idx < len(hand):
                    card = hand[card_idx]
                    top = discard[-1]
                    if can_play(card, top, current_color):
                        hand.pop(card_idx)
                        discard.append(card)
                        broadcast(f"{name} played {card_to_str(card)}")

                        if card[0] != "Black":
                            current_color = card[0]

                        # Handle actions (very simplified here — expand as needed)
                        action = card[1] if isinstance(card[1], str) else None
                        global skip_next, direction, current_turn

                        if action == "Skip":
                            skip_next = True
                        elif action == "Reverse":
                            direction *= -1
                        elif action in ["+2", "+4"]:
                            next_p = (current_turn + direction) % len(clients)
                            count = 2 if action == "+2" else 4
                            for _ in range(count):
                                if deck: clients[next_p][3].append(deck.pop())
                            skip_next = True

                        if card[0] == "Black":
                            current_color = msg.get("color", "Red")

                        # UNO check
                        if len(hand) == 1:
                            broadcast(f"{name} says UNO!!!")

                        if len(hand) == 0:
                            broadcast(f"{name} WINS!!!")
                            # end game logic here...

                        current_turn = (current_turn + (2 if skip_next else 1)) % len(clients)
                        if skip_next: skip_next = False
                        broadcast_state()
                    else:
                        send_to_player(player_idx, json.dumps({"type":"error", "msg":"Illegal card"}))
        except:
            break

    # Cleanup
    clients.remove((conn,addr,name,hand))
    conn.close()
    broadcast(f"{name} left the game.")

def game_loop():
    while True:
        time.sleep(0.3)  # prevent cpu hog
        # You can add timeout/draw logic here if needed

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server started →  {HOST}:{PORT}")
    print("Waiting for 2 players... (tell your friend your IP and port)")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    print("UNO Multiplayer Server by Neo Onyedire")
    main()