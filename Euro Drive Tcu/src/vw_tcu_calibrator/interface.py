from __future__ import annotations

from abc import ABC, abstractmethod

from .core import DEFAULT_CONTEXT, ProjectContext
from .safety import assert_project_mode_allows_frame


class GearboxInterface(ABC):
    """Cable-neutral adapter contract.

    Contributors supporting a new cable should fill in connect(), send_hex(),
    and read_hex(). The rest of the toolkit can stay unchanged.
    """

    name = "generic"

    def __init__(self, *, context: ProjectContext | None = None) -> None:
        self.context = context or DEFAULT_CONTEXT

    @abstractmethod
    def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def send_hex(self, arbitration_id: int, hex_payload: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def read_hex(self, timeout: float = 1.0) -> str | None:
        raise NotImplementedError

    def request_hex(self, arbitration_id: int, hex_payload: str, timeout: float = 1.0) -> str | None:
        payload = bytes.fromhex(hex_payload)
        assert_project_mode_allows_frame(self.context, payload)
        self.send_hex(arbitration_id, hex_payload)
        return self.read_hex(timeout=timeout)
