import pytest

import game_logic as gl


def test_create_deck_has_108_cards():
    assert len(gl.create_deck()) == 108


def test_create_deck_color_counts():
    deck = gl.create_deck()
    for color in ["Red", "Yellow", "Blue", "Green"]:
        color_cards = [c for c in deck if c[0] == color]
        # one 0, two each of 1-9, two each of Skip/Reverse/+2 = 1 + 18 + 6 = 25
        assert len(color_cards) == 25


def test_create_deck_wild_counts():
    deck = gl.create_deck()
    wilds = [c for c in deck if c[0] == "Black"]
    assert len(wilds) == 8
    assert wilds.count(("Black", "Wild")) == 4
    assert wilds.count(("Black", "+4")) == 4


def test_create_deck_is_shuffled_not_in_creation_order():
    # Not a strict correctness requirement, but a sanity check that
    # random.shuffle is actually being invoked and not silently skipped.
    decks = [tuple(gl.create_deck()) for _ in range(5)]
    assert len(set(decks)) > 1


@pytest.mark.parametrize(
    "card,top_card,current_color,expected",
    [
        (("Red", 5), ("Blue", 5), "Blue", True),      # matches value
        (("Red", 5), ("Blue", 9), "Red", True),        # matches color
        (("Black", "Wild"), ("Blue", 9), "Green", True),  # wild always playable
        (("Red", 5), ("Blue", 9), "Green", False),     # matches neither
        (("Green", "Skip"), ("Red", "Skip"), "Red", True),  # action matches action
    ],
)
def test_can_play(card, top_card, current_color, expected):
    assert gl.can_play(card, top_card, current_color) is expected


def test_card_to_json_round_trips_shape():
    assert gl.card_to_json(("Red", 7)) == ["Red", 7]
    assert gl.card_to_json(("Black", "Wild")) == ["Black", "Wild"]


def test_json_to_card_converts_number_card():
    assert gl.json_to_card(["Red", 7]) == ("Red", 7)


def test_json_to_card_converts_action_card():
    assert gl.json_to_card(["Green", "Skip"]) == ("Green", "Skip")


def test_json_to_card_converts_wild_card():
    assert gl.json_to_card(["Black", "Wild"]) == ("Black", "Wild")


def test_json_to_card_round_trips_with_card_to_json():
    for card in [("Red", 7), ("Blue", "Reverse"), ("Black", "+4")]:
        assert gl.json_to_card(gl.card_to_json(card)) == card


def test_colored_wraps_known_color():
    text = gl.colored("5", "Red")
    assert "5" in text
    assert text != "5"  # ANSI codes should have been added


def test_colored_unknown_color_returns_plain_text():
    text = gl.colored("5", "Purple")
    # COLOR_MAP.get() falls back to "", so no color code is prefixed,
    # but Style.RESET_ALL is still appended by colored().
    assert text.startswith("5")


def test_card_to_str_number_card_contains_value():
    assert "7" in gl.card_to_str(("Blue", 7))


def test_card_to_str_wild_card():
    assert "WILD" in gl.card_to_str(("Black", "Wild"))


def test_card_to_str_plus4_card():
    assert "+4" in gl.card_to_str(("Black", "+4"))
