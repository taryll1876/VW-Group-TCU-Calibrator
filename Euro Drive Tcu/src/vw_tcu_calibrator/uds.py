from __future__ import annotations

from enum import IntEnum


class UdsService(IntEnum):
    DIAGNOSTIC_SESSION_CONTROL = 0x10
    ECU_RESET = 0x11
    READ_DATA_BY_IDENTIFIER = 0x22
    SECURITY_ACCESS = 0x27
    TESTER_PRESENT = 0x3E


EXTENDED_SESSION_REQUEST = bytes.fromhex("02 10 03 00 00 00 00 00")
TESTER_PRESENT_REQUEST = bytes.fromhex("02 3E 00 00 00 00 00 00")


def read_did_request(did: int) -> bytes:
    return bytes([0x03, UdsService.READ_DATA_BY_IDENTIFIER, (did >> 8) & 0xFF, did & 0xFF, 0, 0, 0, 0])


def is_positive_session_response(payload: bytes) -> bool:
    return len(payload) >= 3 and payload[1] == 0x50 and payload[2] == 0x03


def is_positive_read_did_response(payload: bytes, did: int) -> bool:
    return (
        len(payload) >= 4
        and payload[1] == 0x62
        and payload[2] == ((did >> 8) & 0xFF)
        and payload[3] == (did & 0xFF)
    )


def negative_response(payload: bytes) -> tuple[int, int] | None:
    if len(payload) >= 4 and payload[1] == 0x7F:
        return payload[2], payload[3]
    return None


def security_access_seed_request(*_args, **_kwargs) -> bytes:
    raise PermissionError(
        "SecurityAccess seed-key unlocking is intentionally not implemented. "
        "Use authorized OEM/vendor tooling for protected functions."
    )
