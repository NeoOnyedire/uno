import socket
import threading
import json
import random
from game_logic import create_deck, can_play, card_to_json, json_to_card, card_to_str

clients = []
clients_lock = threading.Lock()
current_turn = 0
deck = []
discard = []
current_color = ""
direction = 1
game_started = False

HOST = "0.0.0.0"
PORT = 55555


def send_json(conn, payload):
    try:
        conn.sendall((json.dumps(payload) + "\n").encode())
    except Exception:
        pass


def broadcast(payload):
    with clients_lock:
        for client in clients:
            send_json(client["conn"], payload)


def send_to_player(idx, payload):
    with clients_lock:
        if 0 <= idx < len(clients):
            send_json(clients[idx]["conn"], payload)


def receive_message(conn):
    try:
        raw = conn.recv(4096)
        if not raw:
            return None
        text = raw.decode().strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
    except Exception:
        return None


def game_state_for_player(idx):
    with clients_lock:
        me = clients[idx]
        top = discard[-1] if discard else None
        state = {
            "type": "state",
            "your_hand": [card_to_json(c) for c in me["hand"]],
            "top_card": card_to_json(top) if top else None,
            "current_color": current_color,
            "your_turn": (idx == current_turn),
            "players": [{"name": c["name"], "card_count": len(c["hand"])} for c in clients],
            "direction": "clockwise" if direction == 1 else "counter-clockwise"
        }
        return state


def broadcast_state():
    with clients_lock:
        for i in range(len(clients)):
            send_to_player(i, game_state_for_player(i))


def refill_deck_if_needed():
    global deck, discard
    if not deck and len(discard) > 1:
        top = discard.pop()
        random.shuffle(discard)
        deck = discard
        discard = [top]


def reset_game():
    global current_turn, deck, discard, current_color, direction, game_started
    current_turn = 0
    deck = []
    discard = []
    current_color = ""
    direction = 1
    game_started = False


def start_game():
    global deck, discard, current_color, current_turn, game_started
    deck = create_deck()
    discard = [deck.pop()]
    top = discard[0]

    if top[0] == "Black":
        current_color = random.choice(["Red", "Yellow", "Blue", "Green"])
    else:
        current_color = top[0]

    with clients_lock:
        for client in clients:
            client["hand"] = [deck.pop() for _ in range(7)]

    game_started = True
    broadcast({"type": "info", "msg": "GAME STARTED!"})
    broadcast_state()


def get_player_index(conn):
    with clients_lock:
        for idx, client in enumerate(clients):
            if client["conn"] == conn:
                return idx
    return None


def handle_client(conn, addr):
    global current_turn, direction, game_started

    send_json(conn, {"type": "prompt", "msg": "Welcome! Enter your name:"})
    incoming = receive_message(conn)
    if incoming is None:
        conn.close()
        return

    if isinstance(incoming, dict) and incoming.get("type") == "join":
        name = str(incoming.get("name", "")).strip() or f"Player{len(clients)+1}"
    else:
        name = str(incoming).strip() or f"Player{len(clients)+1}"

    client_data = {"conn": conn, "addr": addr, "name": name, "hand": []}
    with clients_lock:
        clients.append(client_data)
        broadcast({"type": "info", "msg": f"{name} has joined the game!"})

    if len(clients) == 2 and not game_started:
        start_game()

    while True:
        message = receive_message(conn)
        if message is None:
            break

        if isinstance(message, dict):
            msg_type = message.get("type")
        else:
            msg_type = None

        if msg_type == "play_card":
            player_idx = get_player_index(conn)
            if player_idx is None:
                break
            if not game_started:
                send_to_player(player_idx, {"type": "error", "msg": "Game has not started yet."})
                continue
            if player_idx != current_turn:
                send_to_player(player_idx, {"type": "error", "msg": "Not your turn."})
                continue

            card_index = message.get("card_index")
            if card_index is None or not isinstance(card_index, int):
                send_to_player(player_idx, {"type": "error", "msg": "Invalid card index."})
                continue

            with clients_lock:
                hand = clients[player_idx]["hand"]
                if not 0 <= card_index < len(hand):
                    send_to_player(player_idx, {"type": "error", "msg": "Invalid card index."})
                    continue
                card = hand[card_index]
                top = discard[-1]
                if not can_play(card, top, current_color):
                    send_to_player(player_idx, {"type": "error", "msg": "Illegal card."})
                    continue

                hand.pop(card_index)
                discard.append(card)
                action = card[1] if isinstance(card[1], str) else None
                if card[0] == "Black":
                    chosen = message.get("color")
                    if chosen not in ["Red", "Yellow", "Blue", "Green"]:
                        send_to_player(player_idx, {"type": "error", "msg": "Must choose a valid color for Wild card."})
                        hand.insert(card_index, card)
                        discard.pop()
                        continue
                    current_color = chosen
                else:
                    current_color = card[0]

                broadcast({"type": "info", "msg": f"{name} played {card_to_str(card)}"})

                next_turn_offset = 1
                if action == "Skip":
                    next_turn_offset = 2
                elif action == "Reverse":
                    direction *= -1
                elif action in ["+2", "+4"]:
                    draw_count = 2 if action == "+2" else 4
                    next_idx = (current_turn + direction) % len(clients)
                    refill_deck_if_needed()
                    for _ in range(draw_count):
                        if deck:
                            clients[next_idx]["hand"].append(deck.pop())
                    next_turn_offset = 2

                if len(hand) == 1:
                    broadcast({"type": "info", "msg": f"{name} says UNO!!!"})

                if len(hand) == 0:
                    broadcast({"type": "game_over", "winner": name, "msg": f"{name} WINS!!!"})
                    game_started = False
                    continue

                current_turn = (current_turn + next_turn_offset * direction) % len(clients)
                broadcast_state()

        elif msg_type == "draw":
            player_idx = get_player_index(conn)
            if player_idx is None:
                break
            if not game_started:
                send_to_player(player_idx, {"type": "error", "msg": "Game has not started yet."})
                continue
            if player_idx != current_turn:
                send_to_player(player_idx, {"type": "error", "msg": "Not your turn."})
                continue

            with clients_lock:
                refill_deck_if_needed()
                if deck:
                    clients[player_idx]["hand"].append(deck.pop())
                broadcast({"type": "info", "msg": f"{name} drew a card."})
                current_turn = (current_turn + direction) % len(clients)
                broadcast_state()

        elif msg_type == "chat":
            msg_text = str(message.get("msg", "")).strip()
            if msg_text:
                broadcast({"type": "chat", "from": name, "msg": msg_text})
        else:
            if isinstance(message, str):
                send_json(conn, {"type": "error", "msg": "Use JSON protocol: {\"type\": ...}"})
            else:
                send_json(conn, {"type": "error", "msg": "Unknown message type."})

    with clients_lock:
        idx = get_player_index(conn)
        if idx is not None:
            left_player = clients.pop(idx)
            broadcast({"type": "info", "msg": f"{left_player['name']} left the game."})
            if game_started and len(clients) < 2:
                broadcast({"type": "info", "msg": "Not enough players — game ended."})
                reset_game()
            elif game_started:
                current_turn = current_turn % len(clients) if clients else 0
                broadcast_state()

    conn.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server started → {HOST}:{PORT}")
    print("Waiting for 2 players... (tell your friend your IP and port)")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    print("UNO Multiplayer Server by Neo Onyedire")
    main()
