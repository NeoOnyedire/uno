# Terminal UNO 🃏

A colorful, sassy **UNO** game that runs directly in your terminal.

Play solo against a cheeky CPU opponent, or challenge a friend over your local network (LAN).

![Terminal UNO gameplay example](https://via.placeholder.com/800x450/111827/ffffff?text=Terminal+UNO+Gameplay+Example)  
*(Replace this placeholder with a real screenshot later – it makes the README much more attractive!)*

## Features

- Classic UNO rules (Skip, Reverse, +2, +4, Wild)
- Beautiful colored cards using `colorama`
- Randomized, savage CPU taunts
- Correct 2-player skip / draw-&-skip logic
- Clean output — no redundant lines
- Draw 1 card → option to play it immediately
- Automatic reshuffle of discard pile when deck is empty
- "UNO!" reminder when you have one card left
- Basic 2-player multiplayer over local network (TCP sockets)

## Requirements

- Python 3.8 or newer
- `colorama` library (for colored terminal output)

### Install colorama (one-time setup)

**Windows (PowerShell / CMD):**
```powershell
py -m pip install colorama
Linux / macOS:
Bashpip3 install colorama
# or
python3 -m pip install colorama
How to Play
Option 1: Single-player vs Computer (recommended for quick fun)

Open a terminal / PowerShell in the project folder
Run:Bashpython uno.pyor (Windows):PowerShellpy uno.py
Controls:
Enter a number → play that card
Press Enter (empty input) → draw 1 card
After Wild or +4 → choose color by typing 1–4


Option 2: Play with a friend (2-player over LAN)
Both computers must be on the same Wi-Fi / local network.
Step-by-step
Player 1 – Host (runs the server)

Open terminal in the project folder
Go to the multiplayer directory:Bashcd multiplayer
Start the server:Bashpython server.pyorPowerShellpy server.pyYou should see:textServer started → 0.0.0.0:55555
Waiting for 2 players...
Find your local IP address
Windows: run ipconfig → look for "IPv4 Address" (usually 192.168.x.x)
macOS/Linux: run ifconfig or ip addr show → look for inet under Wi-Fi interface
→ Tell this IP to Player 2


Both players (including the host) – Join as client

Open terminal in the project folder
Go to multiplayer:Bashcd multiplayer
Start the client:Bashpython client.pyorPowerShellpy client.py
When asked:
Server IP → enter the host's IP address
Port → just press Enter (default: 55555)
Your name → type anything (or press Enter for default)

Once two players connect, the game starts automatically!

Controls (multiplayer):

Type a number → play that card
Type draw or press Enter → draw one card
Follow prompts for Wild / +4 color choice

Notes:

The server window must stay open.
Currently supports exactly 2 players.
Firewall might block port 55555 — allow it if needed.

Project Structure
textuno/
├── uno.py                  # Single-player vs CPU (main game)
├── multiplayer/
│   ├── server.py           # Host / game server
│   ├── client.py           # Player client
│   └── game_logic.py       # Shared card & logic functions
└── README.md
Troubleshooting





























ProblemSolutionNo colors in terminalReinstall colorama: py -m pip install colorama"Connection refused" / can't connectCheck IP address, same network, firewall (allow port 55555)pip / py not recognizedUse full path: python -m pip install coloramaServer doesn't startChange PORT in server.py if 55555 is in useClient hangs after nameMake sure server is running first
Credits
Made with love (and too much coffee) by Neo Onyedire
Enjoy the game — and may your +4 always land on your opponent 😈
Feedback, forks, and savage CPU reply suggestions welcome!