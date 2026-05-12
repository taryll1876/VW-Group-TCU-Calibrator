from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DidSignal:
    name: str
    did: int
    unit: str
    scale: float = 1.0
    offset: float = 0.0
    description: str = ""


@dataclass(frozen=True)
class BusConfig:
    bustype: str = "pcan"
    channel: str = "PCAN_USBBUS1"
    bitrate: int = 500000
    tx_id: int = 0x7E1
    rx_id: int = 0x7E9
    timeout_seconds: float = 1.0
    interval_seconds: float = 0.35


@dataclass(frozen=True)
class TcuProfile:
    name: str
    mechatronic: str
    gearbox_family: str
    clutch_architecture: dict[str, list[str]]
    solenoids: list[str]
    bus: BusConfig
    dids: list[DidSignal] = field(default_factory=list)


@dataclass(frozen=True)
class UdsFrame:
    arbitration_id: int
    data: bytes


@dataclass
class LiveValues:
    values: dict[str, float] = field(default_factory=dict)

    def update(self, key: str, value: float) -> None:
        self.values[key] = value

    def get(self, key: str, default: float = 0.0) -> float:
        return self.values.get(key, default)
