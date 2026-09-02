from __future__ import annotations

import argparse

from .server import run_toolkit_server, ToolkitSignalSnapshot
from .sim_car import SimCarConfig, sim_car_snapshots


def main() -> int:
    parser = argparse.ArgumentParser(description="Toolkit server for UI connection (simulated by default).")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--sim", action="store_true", help="Use simulated car data source (default).")
    parser.add_argument("--oil-start", type=float, default=88.0)
    parser.add_argument("--oil-target", type=float, default=140.0)
    parser.add_argument("--oil-rise-seconds", type=float, default=45.0)
    args = parser.parse_args()

    cfg = SimCarConfig(
        start_oil_temp_c=args.oil_start,
        target_oil_temp_c=args.oil_target,
        oil_rise_seconds=args.oil_rise_seconds,
    )

    # For now: only simulated source.
    snapshots = sim_car_snapshots(cfg=cfg)
    run_toolkit_server(snapshot_source=snapshots, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

