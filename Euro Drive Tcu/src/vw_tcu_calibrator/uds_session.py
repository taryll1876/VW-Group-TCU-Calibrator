from __future__ import annotations

import threading
import time
from dataclasses import dataclass

from .interface import GearboxInterface


@dataclass
class UdsSessionConfig:
    request_id: int = 0x7E1
    response_id: int = 0x7E9
    timeout_seconds: float = 1.0
    tester_present_interval_seconds: float = 2.0


class UdsProtocolWrapper:
    """Handles UDS session boilerplate for contributor drivers.

    It opens the underlying interface, starts extended diagnostic session,
    maintains tester-present, and centralizes timeout handling. It is read-only
    guarded by GearboxInterface.request_hex().
    """

    def __init__(self, interface: GearboxInterface, config: UdsSessionConfig | None = None) -> None:
        self.interface = interface
        self.config = config or UdsSessionConfig()
        self._stop = threading.Event()
        self._tester_thread: threading.Thread | None = None

    def open(self) -> None:
        self.interface.connect()
        response = self.interface.request_hex(
            self.config.request_id,
            "02 10 03 00 00 00 00 00",
            timeout=self.config.timeout_seconds,
        )
        if response is None or "50 03" not in response.replace("0x", "").upper():
            raise TimeoutError("Extended diagnostic session did not return positive response 50 03.")
        self.start_tester_present()

    def start_tester_present(self) -> None:
        if self._tester_thread and self._tester_thread.is_alive():
            return
        self._stop.clear()
        self._tester_thread = threading.Thread(target=self._tester_loop, daemon=True)
        self._tester_thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._tester_thread:
            self._tester_thread.join(timeout=1.0)

    def read_did(self, did: int) -> str | None:
        request = f"03 22 {(did >> 8) & 0xFF:02X} {did & 0xFF:02X} 00 00 00 00"
        return self.interface.request_hex(self.config.request_id, request, timeout=self.config.timeout_seconds)

    def _tester_loop(self) -> None:
        while not self._stop.wait(self.config.tester_present_interval_seconds):
            try:
                self.interface.request_hex(self.config.request_id, "02 3E 00 00 00 00 00 00", timeout=0.25)
            except Exception:
                # Keepalive failures are logged by concrete integrations; avoid killing the session thread.
                pass
