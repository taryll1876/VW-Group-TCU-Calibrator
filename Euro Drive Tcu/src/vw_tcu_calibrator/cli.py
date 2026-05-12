from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

from .bus import BusLike, make_bus
from .decoding import describe_response, hex_bytes
from .health import compute_health_score, pressure_jump_detected
from .models import DidSignal, LiveValues, UdsFrame
from .profile import load_profile
from .safety import assert_read_only_frame
from .uds import EXTENDED_SESSION_REQUEST, is_positive_session_response, read_did_request


def recv_matching(bus: BusLike, rx_id: int, timeout: float) -> UdsFrame | None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        frame = bus.recv(timeout=max(0.01, min(0.2, deadline - time.time())))
        if frame is None:
            continue
        if frame.arbitration_id == rx_id:
            return frame
        print(f"RX other 0x{frame.arbitration_id:X}  {hex_bytes(frame.data)}")
    return None


def send_and_log(bus: BusLike, tx_id: int, payload: bytes, label: str) -> None:
    assert_read_only_frame(payload)
    print(f"TX 0x{tx_id:X}  {hex_bytes(payload)}  {label}")
    bus.send(UdsFrame(tx_id, payload))


def request_session(bus: BusLike, tx_id: int, rx_id: int, timeout: float) -> bool:
    send_and_log(bus, tx_id, EXTENDED_SESSION_REQUEST, "DiagnosticSessionControl extended")
    frame = recv_matching(bus, rx_id, timeout)
    if frame is None:
        print("No response to DiagnosticSessionControl.")
        return False
    print(f"RX 0x{frame.arbitration_id:X}  {hex_bytes(frame.data)}")
    if is_positive_session_response(frame.data):
        print("UDS handshake success: positive response 50 03.")
        return True
    print("UDS handshake failed: expected positive response 50 03.")
    return False


def poll_signal(bus: BusLike, tx_id: int, rx_id: int, timeout: float, signal: DidSignal) -> float | None:
    request = read_did_request(signal.did)
    send_and_log(bus, tx_id, request, f"ReadDID 0x{signal.did:04X} {signal.name}")
    frame = recv_matching(bus, rx_id, timeout)
    if frame is None:
        print(f"RX timeout DID 0x{signal.did:04X}")
        return None
    desc = describe_response(frame.data, signal)
    print(f"RX 0x{frame.arbitration_id:X}  {hex_bytes(frame.data)}  {desc}")
    if "=" not in desc:
        return None
    value_text = desc.split("=", 1)[1].split(" ", 1)[0]
    return float(value_text)


def write_csv_header(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["timestamp", "signal", "value", "unit"])


def append_csv(path: Path, signal: DidSignal, value: float) -> None:
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([time.time(), signal.name, value, signal.unit])


def run(args: argparse.Namespace) -> int:
    profile = load_profile(args.config)
    bus_cfg = profile.bus
    output = Path(args.output)
    write_csv_header(output)

    print(f"profile={profile.name}")
    print(f"mechatronic={profile.mechatronic} gearbox={profile.gearbox_family}")
    print(f"K1={profile.clutch_architecture.get('K1')} K2={profile.clutch_architecture.get('K2')}")
    print(f"solenoids={', '.join(profile.solenoids)}")

    bus = make_bus(
        dry_run=args.dry_run,
        bustype=args.bustype or bus_cfg.bustype,
        channel=args.channel or bus_cfg.channel,
        bitrate=args.bitrate or bus_cfg.bitrate,
        rx_id=bus_cfg.rx_id,
    )

    current = LiveValues()
    previous = LiveValues()
    try:
        if not request_session(bus, bus_cfg.tx_id, bus_cfg.rx_id, bus_cfg.timeout_seconds):
            return 1

        while True:
            previous.values = dict(current.values)
            for signal in profile.dids:
                value = poll_signal(bus, bus_cfg.tx_id, bus_cfg.rx_id, bus_cfg.timeout_seconds, signal)
                if value is None:
                    continue
                current.update(signal.name, value)
                append_csv(output, signal, value)

            score = compute_health_score(current)
            jump = " pressure_jump=true" if pressure_jump_detected(previous, current) else ""
            print(f"health_score={score} live_values={current.values}{jump}")

            if not args.stream:
                break
            time.sleep(bus_cfg.interval_seconds)
    finally:
        bus.shutdown()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="VW Group TCU read-only UDS probe.")
    parser.add_argument("--config", default="configs/dq500_readonly.yaml")
    parser.add_argument("--bustype", default=None)
    parser.add_argument("--channel", default=None)
    parser.add_argument("--bitrate", type=int, default=None)
    parser.add_argument("--stream", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", default="logs/live_did_stream.csv")
    args = parser.parse_args()
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
