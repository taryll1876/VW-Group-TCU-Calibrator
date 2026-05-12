from __future__ import annotations

from .base import BaseReadOnlyDriver, DriverCapabilities


class OBDLinkDriver(BaseReadOnlyDriver):
    """Read-only OBDLink/STN serial wrapper skeleton."""

    capabilities = DriverCapabilities(
        name="obdlink",
        transport="OBDLink STN serial",
        supports_can=True,
        supports_obdlink_stn=True,
    )

    def __init__(self, *, port: str = "COM3", baudrate: int = 115200, **kwargs) -> None:
        super().__init__(**kwargs)
        self.port = port
        self.baudrate = baudrate
        self._serial = None

    def connect(self) -> None:
        try:
            import serial  # type: ignore
        except ImportError as exc:
            raise RuntimeError("pyserial is required for OBDLink serial mode.") from exc
        self._serial = serial.Serial(self.port, self.baudrate, timeout=1)
        self.connected = True

    def close(self) -> None:
        if self._serial is not None:
            self._serial.close()
        self.connected = False

    def send(self, arbitration_id: int, payload: bytes) -> bytes | None:
        raise NotImplementedError("OBDLink STN CAN frame mode is not wired yet.")
