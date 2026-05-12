from __future__ import annotations

from .base import BaseReadOnlyDriver, DriverCapabilities


class J2534Driver(BaseReadOnlyDriver):
    """Read-only placeholder for a vendor J2534 DLL adapter."""

    capabilities = DriverCapabilities(
        name="j2534",
        transport="SAE J2534 pass-thru",
        supports_can=True,
        supports_can_fd=True,
        supports_j2534=True,
    )

    def __init__(self, *, dll_path: str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.dll_path = dll_path

    def send(self, arbitration_id: int, payload: bytes) -> bytes | None:
        raise NotImplementedError("J2534 vendor DLL binding is not configured yet.")
