#!/usr/bin/env python3
"""
Read-only DQ500 UDS probe.

This script confirms that a CAN/CAN FD interface can talk to a VW Group TCU
by sending DiagnosticSessionControl and polling configured ReadDataByIdentifier
requests. It intentionally does not implement SecurityAccess, seed-key unlock,
or write/flash services.
"""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from typing import Iterable


SESSION_EXTENDED = bytes.fromhex("02 10 03 00 00 00 00 00")


@dataclass(frozen=True)
class DidSignal:
    name: str
    did: int
    unit: str
    scale: float
    offset: float = 0.0


DIDS = [
    DidSignal("k1_clutch_pressure_candidate", 0x1901, "bar", 0.1),
    DidSignal("k2_clutch_pressure_candidate", 0x1902, "bar", 0.1),
    DidSignal("gearbox_oil_pressure_or_temp_candidate", 0x1905, "raw", 1.0),
    DidSignal("oil_pump_hydraulic_pressure", 0x1906, "bar", 0.1),
    DidSignal("transmission_oil_monitor_level", 0x1907, "%", 1.0),
    DidSignal("drive_shaft_speed", 0x1908, "rpm", 1.0),
    DidSignal("output_shaft_speed", 0x1909, "rpm", 1.0),
]


def parse_can_id(value: str) -> int:
    return int(value, 16 if value.lower().startswith("0x") else 10)


def fmt(data: Iterable[int]) -> str:
    return " ".join(f"{byte:02X}" for byte in data)


def did_request(did: int) -> bytes:
    high = (did >> 8) & 0xFF
    low = did & 0xFF
    return bytes([0x03, 0x22, high, low, 0x00, 0x00, 0x00, 0x00])


def decode_first_u16(payload: bytes, signal: DidSignal) -> str:
    # Positive DID response on classic CAN usually looks like:
    # length, 0x62, DID high, DID low, data...
    if len(payload) < 6 or payload[1] != 0x62:
        return "no decoded value"
    raw = (payload[4] << 8) | payload[5]
    value = raw * signal.scale + signal.offset
    return f"{value:.1f} {signal.unit} raw=0x{raw:04X}"


def health_from_values(values: dict[str, float]) -> int:
    k1 = values.get("k1_clutch_pressure_candidate", 0.0)
    k2 = values.get("k2_clutch_pressure_candidate", 0.0)
    oil = values.get("gearbox_oil_pressure_or_temp_candidate", 0.0)
    imbalance = abs(k1 - k2)
    score = 100 - min(35, imbalance * 0.8) - min(25, max(0, oil - 120) * 0.12)
    return max(0, min(100, round(score)))


class DryBus:
    def __init__(self, rx_id: int) -> None:
        self.rx_id = rx_id
        self.counter = 0

    def send(self, message) -> None:
        print(f"TX 0x{message.arbitration_id:X}  {fmt(message.data)}")

    def recv(self, timeout: float = 1.0):
        time.sleep(min(timeout, 0.08))
        self.counter += 1
        if self.counter == 1:
            return DryMessage(self.rx_id, bytes.fromhex("02 50 03 00 00 00 00 00"))
        sample = [
            bytes.fromhex("05 62 19 01 01 6D 00 00"),  # 36.5 bar
            bytes.fromhex("05 62 19 02 01 59 00 00"),  # 34.5 bar
            bytes.fromhex("05 62 19 05 00 58 00 00"),  # 88 raw
            bytes.fromhex("05 62 19 06 01 9B 00 00"),  # 41.1 bar
            bytes.fromhex("05 62 19 07 00 55 00 00"),  # 85 %
            bytes.fromhex("05 62 19 08 04 B0 00 00"),  # 1200 rpm
            bytes.fromhex("05 62 19 09 04 B0 00 00"),  # 1200 rpm
        ][(self.counter - 2) % 7]
        return DryMessage(self.rx_id, sample)

    def shutdown(self) -> None:
        return None


class DryMessage:
    def __init__(self, arbitration_id: int, data: bytes) -> None:
        self.arbitration_id = arbitration_id
        self.data = data


def load_can():
    try:
        import can  # type: ignore
    except ImportError:
        return None
    return can


def make_bus(args):
    if args.dry_run:
        return None, DryBus(args.rx_id)

    can = load_can()
    if can is None:
        print("python-can is not installed. Re-run with --dry-run or install python-can.", file=sys.stderr)
        return None, None

    bus = can.Bus(interface=args.bustype, channel=args.channel, bitrate=args.bitrate)
    return can, bus


def send_frame(can_module, bus, arbitration_id: int, data: bytes) -> None:
    if can_module is None:
        message = DryMessage(arbitration_id, data)
    else:
        message = can_module.Message(arbitration_id=arbitration_id, data=data, is_extended_id=False)
    bus.send(message)


def recv_matching(bus, rx_id: int, timeout: float):
    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = bus.recv(timeout=max(0.01, min(0.2, deadline - time.time())))
        if msg is None:
            continue
        if msg.arbitration_id == rx_id:
            return msg
        print(f"RX other 0x{msg.arbitration_id:X}  {fmt(msg.data)}")
    return None


def request_session(can_module, bus, tx_id: int, rx_id: int, timeout: float) -> bool:
    print(f"Requesting extended diagnostic session: TX 0x{tx_id:X}, RX 0x{rx_id:X}")
    send_frame(can_module, bus, tx_id, SESSION_EXTENDED)
    msg = recv_matching(bus, rx_id, timeout)
    if msg is None:
        print("No response to DiagnosticSessionControl.")
        return False

    data = bytes(msg.data)
    print(f"RX 0x{msg.arbitration_id:X}  {fmt(data)}")
    if len(data) >= 3 and data[1] == 0x50 and data[2] == 0x03:
        print("UDS handshake success: positive response 50 03.")
        return True

    print("UDS handshake did not return positive response 50 03.")
    return False


def poll_did(can_module, bus, tx_id: int, rx_id: int, signal: DidSignal, timeout: float):
    request = did_request(signal.did)
    print(f"TX 0x{tx_id:X}  {fmt(request)}  ReadDID 0x{signal.did:04X} {signal.name}")
    send_frame(can_module, bus, tx_id, request)
    msg = recv_matching(bus, rx_id, timeout)
    if msg is None:
        print(f"RX timeout for DID 0x{signal.did:04X}")
        return None

    payload = bytes(msg.data)
    print(f"RX 0x{msg.arbitration_id:X}  {fmt(payload)}  {decode_first_u16(payload, signal)}")
    if len(payload) >= 6 and payload[1] == 0x62:
        raw = (payload[4] << 8) | payload[5]
        return raw * signal.scale + signal.offset
    if len(payload) >= 4 and payload[1] == 0x7F:
        print(f"Negative response: service=0x{payload[2]:02X} nrc=0x{payload[3]:02X}")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only VW Group DQ500 UDS probe.")
    parser.add_argument("--bustype", default="pcan", help="python-can interface, for example pcan, vector, kvaser, socketcan.")
    parser.add_argument("--channel", default="PCAN_USBBUS1", help="Interface channel name.")
    parser.add_argument("--bitrate", type=int, default=500000, help="CAN bitrate.")
    parser.add_argument("--tx-id", type=parse_can_id, default=0x7E1, help="UDS request CAN ID. Example: 0x7e1.")
    parser.add_argument("--rx-id", type=parse_can_id, default=0x7E9, help="UDS response CAN ID. Example: 0x7e9.")
    parser.add_argument("--timeout", type=float, default=1.0, help="Response timeout in seconds.")
    parser.add_argument("--stream", action="store_true", help="Continuously poll configured read-only DIDs.")
    parser.add_argument("--interval", type=float, default=0.35, help="Delay between DID cycles when streaming.")
    parser.add_argument("--dry-run", action="store_true", help="Use simulated frames without hardware.")
    args = parser.parse_args()

    can_module, bus = make_bus(args)
    if bus is None:
        return 2

    values: dict[str, float] = {}
    try:
        if not request_session(can_module, bus, args.tx_id, args.rx_id, args.timeout):
            return 1

        while True:
            for signal in DIDS:
                value = poll_did(can_module, bus, args.tx_id, args.rx_id, signal, args.timeout)
                if value is not None:
                    values[signal.name] = value
            if values:
                print(f"health_score={health_from_values(values)} values={values}")
            if not args.stream:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        shutdown = getattr(bus, "shutdown", None)
        if callable(shutdown):
            shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
