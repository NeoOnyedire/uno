import pytest
from multiplayer import game_logic


def test_create_deck_count():
    deck = game_logic.create_deck()
    # Standard UNO deck: 108 cards
    assert len(deck) == 108


def test_card_serialization_roundtrip():
    card = ("Red", 5)
    j = game_logic.card_to_json(card)
    assert j == ["Red", 5]
    c = game_logic.json_to_card(j)
    assert c == card


def test_can_play_color_match():
    top = ("Red", 3)
    card = ("Red", 7)
    assert game_logic.can_play(card, top, "Red")


def test_can_play_value_match():
    top = ("Blue", 5)
    card = ("Red", 5)
    # Value matches (number or action)
    assert game_logic.can_play(card, top, "Blue")


def test_can_play_wild():
    top = ("Green", "Skip")
    card = ("Black", "Wild")
    assert game_logic.can_play(card, top, "Green")
