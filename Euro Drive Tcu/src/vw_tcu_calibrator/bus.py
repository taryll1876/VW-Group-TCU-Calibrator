from __future__ import annotations

import time
from collections.abc import Protocol

from .models import UdsFrame


class BusLike(Protocol):
    def send(self, frame: UdsFrame) -> None: ...
    def recv(self, timeout: float) -> UdsFrame | None: ...
    def shutdown(self) -> None: ...


class DryRunBus:
    def __init__(self, rx_id: int) -> None:
        self.rx_id = rx_id
        self.counter = 0

    def send(self, frame: UdsFrame) -> None:
        return None

    def recv(self, timeout: float) -> UdsFrame | None:
        time.sleep(min(timeout, 0.08))
        self.counter += 1
        if self.counter == 1:
            return UdsFrame(self.rx_id, bytes.fromhex("02 50 03 00 00 00 00 00"))
        samples = [
            bytes.fromhex("05 62 19 01 01 6D 00 00"),
            bytes.fromhex("05 62 19 02 01 59 00 00"),
            bytes.fromhex("05 62 19 05 00 58 00 00"),
            bytes.fromhex("05 62 19 01 01 95 00 00"),
            bytes.fromhex("05 62 19 02 01 82 00 00"),
            bytes.fromhex("05 62 19 05 00 5C 00 00"),
        ]
        return UdsFrame(self.rx_id, samples[(self.counter - 2) % len(samples)])

    def shutdown(self) -> None:
        return None


class PythonCanBus:
    def __init__(self, bustype: str, channel: str, bitrate: int) -> None:
        try:
            import can  # type: ignore
        except ImportError as exc:
            raise RuntimeError("python-can is required for hardware mode.") from exc
        self._can = can
        self._bus = can.Bus(interface=bustype, channel=channel, bitrate=bitrate)

    def send(self, frame: UdsFrame) -> None:
        message = self._can.Message(
            arbitration_id=frame.arbitration_id,
            data=frame.data,
            is_extended_id=False,
        )
        self._bus.send(message)

    def recv(self, timeout: float) -> UdsFrame | None:
        msg = self._bus.recv(timeout=timeout)
        if msg is None:
            return None
        return UdsFrame(msg.arbitration_id, bytes(msg.data))

    def shutdown(self) -> None:
        self._bus.shutdown()


def make_bus(*, dry_run: bool, bustype: str, channel: str, bitrate: int, rx_id: int) -> BusLike:
    if dry_run:
        return DryRunBus(rx_id)
    return PythonCanBus(bustype=bustype, channel=channel, bitrate=bitrate)
