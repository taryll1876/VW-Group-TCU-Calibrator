from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..core import DEFAULT_CONTEXT, ProjectContext
from ..safety import assert_read_only_frame
from ..uds import read_did_request


@dataclass(frozen=True)
class DriverCapabilities:
    name: str
    transport: str
    supports_can: bool = True
    supports_can_fd: bool = False
    supports_j2534: bool = False
    supports_obdlink_stn: bool = False
    read_only: bool = True


class TcuDriver(Protocol):
    capabilities: DriverCapabilities
    context: ProjectContext

    def connect(self) -> None: ...
    def close(self) -> None: ...
    def send(self, arbitration_id: int, payload: bytes) -> bytes | None: ...
    def read_did(self, did: int) -> bytes | None: ...
    def write_payload(self, arbitration_id: int, payload: bytes) -> bytes | None: ...


class BaseReadOnlyDriver:
    capabilities = DriverCapabilities(name="base", transport="abstract")

    def __init__(self, *, context: ProjectContext | None = None) -> None:
        self.context = context or DEFAULT_CONTEXT
        self.connected = False

    def connect(self) -> None:
        self.connected = True

    def close(self) -> None:
        self.connected = False

    def read_did(self, did: int) -> bytes | None:
        self.context.require_read_allowed()
        payload = read_did_request(did)
        assert_read_only_frame(payload)
        return self.send(0x7E1, payload)

    def write_payload(self, arbitration_id: int, payload: bytes) -> bytes | None:
        self.context.require_write_allowed()
        return self.send(arbitration_id, payload)

    def send(self, arbitration_id: int, payload: bytes) -> bytes | None:
        raise NotImplementedError
