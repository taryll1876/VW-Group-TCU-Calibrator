from __future__ import annotations

from .models import DidSignal
from .uds import is_positive_read_did_response, negative_response


def hex_bytes(data: bytes) -> str:
    return " ".join(f"{byte:02X}" for byte in data)


def parse_can_id(value: str | int) -> int:
    if isinstance(value, int):
        return value
    return int(value, 16 if value.lower().startswith("0x") else 10)


def decode_first_u16(payload: bytes, signal: DidSignal) -> float | None:
    if not is_positive_read_did_response(payload, signal.did):
        return None
    if len(payload) < 6:
        return None
    raw = (payload[4] << 8) | payload[5]
    return raw * signal.scale + signal.offset


def describe_response(payload: bytes, signal: DidSignal | None = None) -> str:
    if signal is not None:
        value = decode_first_u16(payload, signal)
        if value is not None:
            return f"{signal.name}={value:.2f} {signal.unit}"

    negative = negative_response(payload)
    if negative:
        service, code = negative
        return f"negative_response service=0x{service:02X} nrc=0x{code:02X}"

    return "unparsed"
