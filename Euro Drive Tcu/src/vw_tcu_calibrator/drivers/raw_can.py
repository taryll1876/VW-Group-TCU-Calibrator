from __future__ import annotations

from ..bus import PythonCanBus
from ..models import UdsFrame
from .base import BaseReadOnlyDriver, DriverCapabilities


class RawCanDriver(BaseReadOnlyDriver):
    capabilities = DriverCapabilities(name="raw-can", transport="python-can", supports_can=True)

    def __init__(self, *, bustype: str = "pcan", channel: str = "PCAN_USBBUS1", bitrate: int = 500000, rx_id: int = 0x7E9, **kwargs) -> None:
        super().__init__(**kwargs)
        self.bustype = bustype
        self.channel = channel
        self.bitrate = bitrate
        self.rx_id = rx_id
        self._bus: PythonCanBus | None = None

    def connect(self) -> None:
        self._bus = PythonCanBus(self.bustype, self.channel, self.bitrate)
        self.connected = True

    def close(self) -> None:
        if self._bus:
            self._bus.shutdown()
        self.connected = False

    def send(self, arbitration_id: int, payload: bytes) -> bytes | None:
        if self._bus is None:
            self.connect()
        assert self._bus is not None
        self._bus.send(UdsFrame(arbitration_id, payload))
        frame = self._bus.recv(1.0)
        return frame.data if frame and frame.arbitration_id == self.rx_id else None
