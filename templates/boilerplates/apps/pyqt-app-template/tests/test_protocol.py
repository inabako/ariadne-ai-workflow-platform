from __future__ import annotations

import pytest

from network.protocol import decode_message, encode_message


def test_protocol_encode_decode() -> None:
    encoded = encode_message("PING", {"seq": 1})
    decoded = decode_message(encoded)
    assert decoded.command == "PING"
    assert decoded.payload == {"seq": 1}


def test_protocol_rejects_unknown_command() -> None:
    with pytest.raises(ValueError):
        encode_message("UNKNOWN")
