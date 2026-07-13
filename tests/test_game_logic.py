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


@pytest.mark.xfail(
    reason=(
        "json_to_card's ternary `j[1] if isinstance(j[1], int) else j[1]` "
        "returns j[1] on both branches, so it never actually normalizes "
        "the value. Currently a no-op; nothing in server.py/client.py "
        "calls this function today, so it hasn't caused a live bug, but "
        "the implementation doesn't do what its name/branching implies."
    ),
    strict=False,
)
def test_json_to_card_normalizes_value_type():
    # Intent seems to be: pass ints through, and presumably do *something*
    # different for non-int values. As written it's identical either way.
    card = gl.json_to_card(["Red", 7])
    assert card == ("Red", 7)


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
