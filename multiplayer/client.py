import os
import socket
import threading
import json
import sys

client = None
current_hand = []
hand_lock = threading.Lock()

COLOR_NAMES = ["Red", "Yellow", "Blue", "Green"]


def print_state(data):
    with hand_lock:
        current_hand.clear()
        current_hand.extend(data.get("your_hand", []))

    os.system('cls' if os.name == 'nt' else 'clear')
    current_color = data.get("current_color", "")
    top_card = data.get("top_card")
    top_card_text = top_card and f"{top_card[0]} {top_card[1]}" or "None"
    print(f"\nCurrent color: {current_color}")
    print(f"Top card: {top_card_text}")
    print(f"Your turn: {'YES' if data.get('your_turn') else 'NO'}")
    print("\nYour hand:")
    for i, c in enumerate(data.get("your_hand", []), 1):
        print(f" {i}: {c[0]} {c[1]}")
    print(f"\nPlayers: " + " | ".join(f"{p['name']} ({p['card_count']})" for p in data.get("players", [])))
    if data.get("your_turn"):
        print("\n→ Your turn! Enter card number or 'draw'")


def receive_thread():
    buffer = ""
    while True:
        try:
            data = client.recv(4096).decode()
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    print(line)
                    continue

                msg_type = message.get("type")
                if msg_type == "state":
                    print_state(message)
                elif msg_type == "error":
                    print(f"Error: {message.get('msg')}")
                elif msg_type == "info":
                    print(message.get('msg'))
                elif msg_type == "chat":
                    print(f"[{message.get('from')}] {message.get('msg')}")
                elif msg_type == "prompt":
                    print(message.get('msg'))
                elif msg_type == "game_over":
                    print(message.get('msg'))
                    print(f"Winner: {message.get('winner')}")
                    sys.exit(0)
                else:
                    print(message)
        except Exception:
            break


def send_message(data):
    try:
        client.sendall((json.dumps(data) + "\n").encode())
    except Exception:
        pass


def choose_color():
    print("Choose a color:")
    for i, color in enumerate(COLOR_NAMES, 1):
        print(f" {i}: {color}")
    while True:
        choice = input("Enter number: ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(COLOR_NAMES):
                return COLOR_NAMES[idx]
        print("Invalid selection, please choose 1-4.")


def main():
    global client
    print("UNO Multiplayer Client by Neo Onyedire")
    host = input("Enter server IP (ask host): ").strip() or "127.0.0.1"
    port_input = input("Enter port (default 55555): ").strip()
    port = int(port_input) if port_input.isdigit() else 55555
    name = input("Enter your name: ").strip() or "Player"

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
    except Exception:
        print("Cannot connect. Is server running?")
        sys.exit(1)

    send_message({"type": "join", "name": name})
    threading.Thread(target=receive_thread, daemon=True).start()

    while True:
        try:
            msg = input("").strip()
            if not msg:
                continue
            if msg.lower() in ["quit", "exit"]:
                break

            if msg.lower() == "draw":
                send_message({"type": "draw"})
                continue

            if msg.isdigit():
                index = int(msg) - 1
                with hand_lock:
                    if 0 <= index < len(current_hand):
                        card = current_hand[index]
                    else:
                        print("Invalid card number.")
                        continue

                payload = {"type": "play_card", "card_index": index}
                if card[0] == "Black":
                    payload["color"] = choose_color()
                send_message(payload)
                continue

            send_message({"type": "chat", "msg": msg})
        except Exception:
            break

    client.close()
    print("Disconnected.")


if __name__ == "__main__":
    main()
