from __future__ import annotations

import itertools

from .base import BaseReadOnlyDriver, DriverCapabilities


class SimDriver(BaseReadOnlyDriver):
    capabilities = DriverCapabilities(name="sim", transport="software simulator", supports_can=True)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._counter = itertools.count()

    def send(self, arbitration_id: int, payload: bytes) -> bytes | None:
        did = (payload[2] << 8) | payload[3] if len(payload) >= 4 and payload[1] == 0x22 else 0
        step = next(self._counter)
        values = {
            0x1901: 365 + step * 7,
            0x1902: 345 + step * 6,
            0x1905: 128 + step,
            0x2213: 1900 + step * 20,
        }
        raw = values.get(did)
        if raw is None:
            return bytes([0x03, 0x7F, 0x22, 0x31, 0, 0, 0, 0])
        return bytes([0x05, 0x62, (did >> 8) & 0xFF, did & 0xFF, (raw >> 8) & 0xFF, raw & 0xFF, 0, 0])
