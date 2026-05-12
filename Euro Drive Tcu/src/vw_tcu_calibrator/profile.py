from __future__ import annotations

from pathlib import Path

import yaml

from .decoding import parse_can_id
from .models import BusConfig, DidSignal, TcuProfile


def load_profile(path: str | Path) -> TcuProfile:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    bus_data = data["bus"]
    bus = BusConfig(
        bustype=bus_data.get("bustype", "pcan"),
        channel=bus_data.get("channel", "PCAN_USBBUS1"),
        bitrate=int(bus_data.get("bitrate", 500000)),
        tx_id=parse_can_id(bus_data.get("tx_id", "0x7e1")),
        rx_id=parse_can_id(bus_data.get("rx_id", "0x7e9")),
        timeout_seconds=float(bus_data.get("timeout_seconds", 1.0)),
        interval_seconds=float(bus_data.get("interval_seconds", 0.35)),
    )
    dids = [
        DidSignal(
            name=item["name"],
            did=parse_can_id(item["did"]),
            unit=item.get("unit", "raw"),
            scale=float(item.get("scale", 1.0)),
            offset=float(item.get("offset", 0.0)),
            description=item.get("description", ""),
        )
        for item in data.get("dids", [])
    ]
    return TcuProfile(
        name=data["name"],
        mechatronic=data["mechatronic"],
        gearbox_family=data["gearbox_family"],
        clutch_architecture=data.get("clutch_architecture", {}),
        solenoids=data.get("solenoids", []),
        bus=bus,
        dids=dids,
    )
