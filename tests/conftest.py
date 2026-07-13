import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MULTIPLAYER_DIR = os.path.join(REPO_ROOT, "multiplayer")

# uno.py lives at the repo root; game_logic.py / server.py import each other
# with bare `import game_logic`, so both dirs need to be importable.
for path in (REPO_ROOT, MULTIPLAYER_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)


@pytest.fixture(autouse=True)
def _no_real_sleep(monkeypatch):
    """Every module under test calls time.sleep() for dramatic effect.
    Kill it globally so the suite runs in milliseconds, not minutes."""
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


@pytest.fixture
def fixed_deck(monkeypatch):
    """Lets a test hand uno.py a specific deck instead of a shuffled one,
    by patching shuffle_deck to a no-op and card_deck to return a given list."""

    def _apply(cards):
        import uno

        monkeypatch.setattr(uno, "card_deck", lambda: list(cards))
        monkeypatch.setattr(uno, "shuffle_deck", lambda deck: deck)

    return _apply
