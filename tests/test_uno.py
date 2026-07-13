import pytest

import uno


# ────────────────────────────────────────────────
#   DECK STRUCTURE
#   (uno.py duplicates game_logic.py's deck-building code; these tests
#   guard against the two implementations silently drifting apart.)
# ────────────────────────────────────────────────

def test_card_deck_has_108_cards():
    assert len(uno.card_deck()) == 108


def test_card_deck_color_counts():
    deck = uno.card_deck()
    for color in ["Red", "Yellow", "Blue", "Green"]:
        assert len([c for c in deck if c[0] == color]) == 25


def test_card_deck_wild_counts():
    deck = uno.card_deck()
    wilds = [c for c in deck if c[0] == "Black"]
    assert wilds.count(("Black", "Wild")) == 4
    assert wilds.count(("Black", "+4")) == 4


# ────────────────────────────────────────────────
#   can_play / draw_card
# ────────────────────────────────────────────────

@pytest.mark.parametrize(
    "card,discard,current_color,expected",
    [
        (("Red", 5), [("Blue", 9), ("Blue", 5)], "Blue", True),   # value match
        (("Red", 5), [("Blue", 9)], "Red", True),                  # color match
        (("Black", "+4"), [("Blue", 9)], "Green", True),           # wild always OK
        (("Red", 5), [("Blue", 9)], "Green", False),               # no match
    ],
)
def test_can_play(card, discard, current_color, expected):
    assert uno.can_play(card, discard, current_color) is expected


def test_draw_card_moves_cards_from_deck_to_hand_in_order():
    deck = [1, 2, 3, 4, 5]
    hand = []
    uno.draw_card(deck, hand, count=3)
    assert hand == [1, 2, 3]
    assert deck == [4, 5]


def test_draw_card_stops_gracefully_when_deck_runs_out():
    deck = [1, 2]
    hand = []
    uno.draw_card(deck, hand, count=5)
    assert hand == [1, 2]
    assert deck == []


def test_draw_card_default_count_is_one():
    deck = [1, 2, 3]
    hand = []
    uno.draw_card(deck, hand)
    assert hand == [1]
    assert deck == [2, 3]


# ────────────────────────────────────────────────
#   reshuffle_if_needed / draw_card(..., discard=)
#
#   Regression coverage for a bug where forced draws (+2/+4 penalties,
#   and the CPU's "no valid cards" draw) never reshuffled the discard
#   pile back into an empty deck, silently under-dealing cards. Also
#   covers a related bug where the original manual-draw reshuffle
#   rebound `discard` to a brand-new list instead of mutating it in
#   place, so any other code still holding the old `discard` reference
#   (e.g. the main game loop) never saw the reshuffle happen.
# ────────────────────────────────────────────────

def test_reshuffle_if_needed_moves_all_but_top_card_into_deck():
    deck = []
    discard = [("Red", 1), ("Blue", 2), ("Green", 3)]
    uno.reshuffle_if_needed(deck, discard)
    assert discard == [("Green", 3)]
    assert set(deck) == {("Red", 1), ("Blue", 2)}


def test_reshuffle_if_needed_is_noop_when_deck_has_cards():
    deck = [("Red", 9)]
    discard = [("Red", 1), ("Blue", 2), ("Green", 3)]
    uno.reshuffle_if_needed(deck, discard)
    assert deck == [("Red", 9)]
    assert discard == [("Red", 1), ("Blue", 2), ("Green", 3)]


def test_reshuffle_if_needed_is_noop_when_discard_too_short():
    deck = []
    discard = [("Red", 1)]
    uno.reshuffle_if_needed(deck, discard)
    assert deck == []
    assert discard == [("Red", 1)]


def test_draw_card_reshuffles_via_discard_kwarg_when_deck_empty():
    deck = []
    hand = []
    discard = [("Red", 1), ("Blue", 2), ("Green", 3)]
    uno.draw_card(deck, hand, count=1, discard=discard)
    assert len(hand) == 1
    assert discard == [("Green", 3)]


def test_draw_card_without_discard_kwarg_is_unchanged_when_deck_empty():
    # Backward compatibility: existing call sites that don't pass
    # discard= should behave exactly as before (no reshuffle, no crash).
    deck = []
    hand = []
    uno.draw_card(deck, hand, count=1)
    assert hand == []
    assert deck == []


def test_draw_card_reshuffle_is_visible_to_a_caller_holding_the_old_discard_reference():
    # This is the crux of the bug: some *other* piece of code (the game
    # loop) holds its own reference to the same discard list. A correct
    # fix has to mutate that list in place, not swap in a new one.
    outer_discard = [("Red", 1), ("Blue", 2), ("Green", 3)]

    def simulate_forced_draw(discard):
        deck = []
        hand = []
        uno.draw_card(deck, hand, count=1, discard=discard)
        return hand

    drawn = simulate_forced_draw(outer_discard)
    assert len(drawn) == 1
    # The caller's own reference must reflect the reshuffle: just the
    # original top card remains, not the untouched 3-card pile.
    assert outer_discard == [("Green", 3)]


# ────────────────────────────────────────────────
#   cpu_sassy_comment
# ────────────────────────────────────────────────

def test_cpu_sassy_comment_for_known_action_uses_that_actions_lines():
    comment = uno.cpu_sassy_comment(("Red", "+2"), is_player_played=True)
    assert comment in uno.CPU_SASS_ON_PLAYED_BY_PLAYER["+2"]


def test_cpu_sassy_comment_for_number_card_uses_generic_lines():
    # Numeric values map to "+number", which isn't a key in
    # CPU_SASS_ON_PLAYED_BY_PLAYER, so this should fall through
    # to the generic reply list rather than KeyError.
    comment = uno.cpu_sassy_comment(("Red", 5), is_player_played=True)
    assert isinstance(comment, str) and comment


def test_cpu_sassy_comment_when_cpu_plays_uses_cpu_lines():
    comment = uno.cpu_sassy_comment(("Red", 5), is_player_played=False)
    assert comment in uno.CPU_SASS_WHEN_CPU_PLAYS


# ────────────────────────────────────────────────
#   discard_pile
# ────────────────────────────────────────────────

def test_discard_pile_with_colored_top_card_needs_no_input(fixed_deck):
    fixed_deck([("Blue", 7), ("Red", 3), ("Green", 1)])
    discard, deck, starting_color = uno.discard_pile()
    assert discard == [("Blue", 7)]
    assert deck == [("Red", 3), ("Green", 1)]
    assert starting_color == "Blue"


def test_discard_pile_with_wild_top_card_uses_valid_input(fixed_deck, monkeypatch):
    fixed_deck([("Black", "Wild"), ("Red", 3), ("Green", 1)])
    # colors offered are ["Red", "Yellow", "Blue", "Green"]; "2" -> Yellow
    monkeypatch.setattr("builtins.input", lambda *_: "2")
    discard, deck, starting_color = uno.discard_pile()
    assert discard == [("Black", "Wild")]
    assert starting_color == "Yellow"


def test_discard_pile_with_wild_top_card_reprompts_on_bad_input(fixed_deck, monkeypatch):
    fixed_deck([("Black", "+4"), ("Red", 3), ("Green", 1)])
    # "x" -> not a number (ValueError, caught); "9" -> parses but out of
    # range (index 8, not 0<=idx<4); "1" -> finally valid -> Red.
    responses = iter(["x", "9", "1"])
    monkeypatch.setattr("builtins.input", lambda *_: next(responses))
    discard, deck, starting_color = uno.discard_pile()
    assert starting_color == "Red"


def test_discard_pile_with_action_card_needs_no_input(fixed_deck):
    fixed_deck([("Green", "Skip"), ("Red", 3), ("Blue", 1)])
    discard, deck, starting_color = uno.discard_pile()
    assert discard == [("Green", "Skip")]
    assert starting_color == "Green"
