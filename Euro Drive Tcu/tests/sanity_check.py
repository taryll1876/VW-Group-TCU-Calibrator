from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from vw_tcu_calibrator.core import DEFAULT_CONTEXT  # noqa: E402
from vw_tcu_calibrator.drivers.registry import create_driver  # noqa: E402
from vw_tcu_calibrator.safety import assert_project_mode_allows_frame  # noqa: E402
from vw_tcu_calibrator.sim_car import SimCarConfig, sim_car_snapshots  # noqa: E402


def validate_json(path: Path) -> None:
    with path.open("r", encoding="utf-8") as fh:
        json.load(fh)


def validate_simulator() -> None:
    gen = sim_car_snapshots(cfg=SimCarConfig(oil_rise_c_per_second=0.5))
    snap = next(gen)
    assert snap.rpm is not None and 800 <= snap.rpm <= 8100
    assert snap.k1_clutch_pressure_candidate_bar is not None
    assert 0 <= snap.k1_clutch_pressure_candidate_bar <= 12.0
    assert snap.oil_temp_c is not None


def validate_read_only_guard() -> None:
    assert_project_mode_allows_frame(DEFAULT_CONTEXT, bytes.fromhex("03 22 19 01 00 00 00 00"))
    try:
        assert_project_mode_allows_frame(DEFAULT_CONTEXT, bytes.fromhex("03 2E 19 01 00 00 00 00"))
    except PermissionError:
        pass
    else:
        raise AssertionError("write service was not blocked")

    driver = create_driver("sim")
    response = driver.read_did(0x1901)
    assert response is not None and response[1] == 0x62


def main() -> int:
    validate_json(ROOT / "data" / "dq500_map.json")
    validate_json(ROOT / "data" / "vehicle_profiles.json")
    validate_json(ROOT / "data" / "torque_splitter_map.json")
    validate_simulator()
    validate_read_only_guard()
    print("sanity_check: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
