# multiplayer/client.py
import os
import socket
import threading
import json
import sys
from game_logic import card_to_str, colored, json_to_card

def receive_thread():
    while True:
        try:
            msg = client.recv(4096).decode()
            if not msg: break

            data = json.loads(msg)
            t = data.get("type")

            if t == "state":
                os.system('cls' if os.name == 'nt' else 'clear')  # clear terminal
                print(f"\nCurrent color: {colored(data['current_color'], data['current_color'])}")
                print(f"Top card: {card_to_str(json_to_card(data['top_card']))}")
                print(f"Your turn: {'YES' if data['your_turn'] else 'NO'}")
                print("\nYour hand:")
                for i, c in enumerate(data["your_hand"]):
                    card = json_to_card(c)
                    print(f" {i+1}: {card_to_str(card)}")
                print(f"\nPlayers: " + " | ".join(f"{p['name']} ({p['card_count']})" for p in data["players"]))
                if data["your_turn"]:
                    print("\n→ Your turn! Enter card number or 'draw'")
            elif t == "error":
                print(f"Error: {data['msg']}")
            else:
                print(msg)
        except:
            break

# ────────────────────────────────
if __name__ == "__main__":
    print("UNO Multiplayer Client by Neo Onyedire")
    host = input("Enter server IP (ask host): ").strip() or "127.0.0.1"
    port = int(input("Enter port (default 55555): ") or 55555)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
    except:
        print("Cannot connect. Is server running?")
        sys.exit(1)

    threading.Thread(target=receive_thread, daemon=True).start()

    while True:
        try:
            msg = input("").strip()
            if msg.lower() in ["quit", "exit"]: break

            if msg.isdigit():
                data = {"type": "play_card", "card_index": int(msg)-1}
            elif msg.lower() == "draw":
                data = {"type": "draw"}
            else:
                # Later: color choice after wild
                data = {"type": "chat", "msg": msg}

            client.send(json.dumps(data).encode())
        except:
            break

    client.close()
    print("Disconnected.")