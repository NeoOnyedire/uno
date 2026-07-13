import pytest

import server


class FakeConn:
    """Stands in for a socket connection: recv() returns queued byte
    chunks (simulating however TCP happened to fragment/coalesce the
    stream), sendall() is a no-op."""

    def __init__(self, chunks):
        self._chunks = list(chunks)

    def recv(self, _bufsize):
        if self._chunks:
            return self._chunks.pop(0)
        return b""

    def sendall(self, _data):
        pass


# ────────────────────────────────────────────────
#   make_receiver: message framing over the wire
# ────────────────────────────────────────────────

def test_receiver_reassembles_a_message_split_across_recv_calls():
    conn = FakeConn([b'{"type": "j', b'oin", "name": "Bob"}\n'])
    receive = server.make_receiver(conn)
    assert receive() == {"type": "join", "name": "Bob"}


def test_receiver_splits_two_messages_delivered_in_one_recv_call():
    conn = FakeConn([b'{"a": 1}\n{"b": 2}\n'])
    receive = server.make_receiver(conn)
    assert receive() == {"a": 1}
    assert receive() == {"b": 2}


def test_receiver_skips_blank_lines():
    conn = FakeConn([b'\n\n{"x": 1}\n'])
    receive = server.make_receiver(conn)
    assert receive() == {"x": 1}


def test_receiver_returns_none_on_disconnect():
    conn = FakeConn([b""])
    receive = server.make_receiver(conn)
    assert receive() is None


def test_receiver_falls_back_to_raw_string_for_non_json_line():
    conn = FakeConn([b"hello there\n"])
    receive = server.make_receiver(conn)
    assert receive() == "hello there"


def test_receiver_returns_none_when_disconnect_happens_mid_message():
    # Partial data arrives, then the socket closes before a newline shows up.
    conn = FakeConn([b'{"type": "unfinished"', b""])
    receive = server.make_receiver(conn)
    assert receive() is None


# ────────────────────────────────────────────────
#   refill_deck_if_needed
# ────────────────────────────────────────────────

def test_refill_reshuffles_discard_into_deck_when_deck_is_empty(monkeypatch):
    monkeypatch.setattr(server, "deck", [])
    monkeypatch.setattr(server, "discard", [("Red", 1), ("Blue", 2)])
    server.refill_deck_if_needed()
    assert server.discard == [("Blue", 2)]  # top card kept in place
    assert server.deck == [("Red", 1)]      # rest reshuffled into the deck


def test_refill_is_noop_when_deck_still_has_cards(monkeypatch):
    monkeypatch.setattr(server, "deck", [("Red", 1)])
    monkeypatch.setattr(server, "discard", [("Blue", 2), ("Green", 3)])
    server.refill_deck_if_needed()
    assert server.deck == [("Red", 1)]
    assert server.discard == [("Blue", 2), ("Green", 3)]


def test_refill_is_noop_when_discard_pile_too_small(monkeypatch):
    monkeypatch.setattr(server, "deck", [])
    monkeypatch.setattr(server, "discard", [("Blue", 2)])
    server.refill_deck_if_needed()
    assert server.deck == []
    assert server.discard == [("Blue", 2)]


# ────────────────────────────────────────────────
#   reset_game
# ────────────────────────────────────────────────

def test_reset_game_restores_defaults(monkeypatch):
    monkeypatch.setattr(server, "current_turn", 3)
    monkeypatch.setattr(server, "deck", [("Red", 1)])
    monkeypatch.setattr(server, "discard", [("Blue", 2)])
    monkeypatch.setattr(server, "current_color", "Red")
    monkeypatch.setattr(server, "direction", -1)
    monkeypatch.setattr(server, "game_started", True)

    server.reset_game()

    assert server.current_turn == 0
    assert server.deck == []
    assert server.discard == []
    assert server.current_color == ""
    assert server.direction == 1
    assert server.game_started is False


# ────────────────────────────────────────────────
#   get_player_index
# ────────────────────────────────────────────────

def test_get_player_index_finds_matching_connection(monkeypatch):
    conn_a, conn_b = FakeConn([]), FakeConn([])
    monkeypatch.setattr(server, "clients", [{"conn": conn_a}, {"conn": conn_b}])
    assert server.get_player_index(conn_b) == 1


def test_get_player_index_returns_none_when_not_found(monkeypatch):
    conn_a = FakeConn([])
    conn_stranger = FakeConn([])
    monkeypatch.setattr(server, "clients", [{"conn": conn_a}])
    assert server.get_player_index(conn_stranger) is None


def test_get_player_index_checks_waiting_clients_when_asked(monkeypatch):
    conn_a, conn_b = FakeConn([]), FakeConn([])
    monkeypatch.setattr(server, "clients", [{"conn": conn_a}])
    monkeypatch.setattr(server, "waiting_clients", [{"conn": conn_b}])
    assert server.get_player_index(conn_b, from_waiting=True) == 0
    assert server.get_player_index(conn_b, from_waiting=False) is None
