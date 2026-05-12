from __future__ import annotations

from .base import DriverCapabilities
from .j2534 import J2534Driver


class OpenPort2Driver(J2534Driver):
    """Tactrix OpenPort 2.0 read-only J2534 wrapper."""

    capabilities = DriverCapabilities(
        name="openport2",
        transport="Tactrix OpenPort 2.0 J2534",
        supports_can=True,
        supports_j2534=True,
    )
