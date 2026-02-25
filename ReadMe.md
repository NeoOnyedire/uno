# Terminal UNO 🎴

A colorful, single-player **UNO** game that runs entirely in your terminal using Python and `colorama`.

Play against a simple (but cheeky) CPU opponent — complete with Wild cards, +2/+4 stacking punishment, Skip, Reverse, and the classic "UNO!" moment.

![Terminal UNO gameplay screenshot](https://via.placeholder.com/800x450/111827/ffffff?text=Terminal+UNO+Gameplay+Example)  
*(Add your own screenshot here later 😄)*

## Features

- Classic UNO rules (mostly 😏)
- Colored cards using terminal ANSI colors
- Wild & +4 color selection (player chooses, CPU picks randomly)
- Draw 1 → optional immediate play (like real UNO)
- Deck reshuffles when empty (using discard pile except top card)
- "UNO!" reminder when you have 1 card left
- Skip, Reverse, +2, +4 handling
- Very sassy CPU opponent

## Requirements

- Python 3.6+
- `colorama` (for cross-platform colored terminal output)

```bash
pip install colorama

## Multiplayer Mode (Local Network / LAN)

Added basic **2-player online multiplayer** over sockets.

### How to play with a friend on different PCs

1. **One player runs the server**:
   ```bash
   cd multiplayer
   python server.py