from __future__ import annotations

import argparse
from pathlib import Path

from .core import ProjectContext, ProjectMode
from .drivers.registry import create_driver
from .server import run_toolkit_server
from .sim_car import SimCarConfig, sim_car_snapshots
from .translator import HardwareTranslator


def main() -> int:
    parser = argparse.ArgumentParser(description="Toolkit server for UI connection and normalized TCU signals.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--driver", default="sim", choices=["sim", "raw-can", "j2534", "openport2", "obdlink"])
    parser.add_argument("--mode", default="read_only", choices=["read_only"])
    parser.add_argument("--map", default="data/dq500_map.json")
    parser.add_argument("--sim", action="store_true", help="Use simulated car data source.")
    parser.add_argument("--oil-start", type=float, default=88.0)
    parser.add_argument("--oil-max", type=float, default=145.0)
    parser.add_argument("--oil-rise-c-per-second", type=float, default=0.5)
    args = parser.parse_args()

    context = ProjectContext(mode=ProjectMode.READ_ONLY)
    cfg = SimCarConfig(
        start_oil_temp_c=args.oil_start,
        max_oil_temp_c=args.oil_max,
        oil_rise_c_per_second=args.oil_rise_c_per_second,
    )

    if args.driver == "sim" or args.sim:
        snapshots = sim_car_snapshots(cfg=cfg)
    else:
        driver = create_driver(args.driver, context=context)
        driver.connect()
        snapshots = HardwareTranslator(driver, Path(args.map), context=context)

    run_toolkit_server(snapshot_source=snapshots, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

