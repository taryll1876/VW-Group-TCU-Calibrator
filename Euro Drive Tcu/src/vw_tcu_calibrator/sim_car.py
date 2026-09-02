from __future__ import annotations

import time
from dataclasses import dataclass

from .server import ToolkitSignalSnapshot
from .simulation import SimulationEngine, SimulationConfig


@dataclass
class SimCarConfig(SimulationConfig):
    pass


def sim_car_snapshots(*, cfg: SimCarConfig | None = None):
    """Generator of normalized snapshots.

    This is bench-safe mock data intended for UI/abuse-index prototyping.
    """
    if cfg is None:
        cfg = SimCarConfig()

    engine = SimulationEngine(cfg)
    t0 = time.time()
    while True:
        t = time.time() - t0
        payload = engine.snapshot(t, now=time.time())
        yield ToolkitSignalSnapshot(
            k1_clutch_pressure_candidate_bar=float(payload["clutch_k1_pressure_bar"] or 0.0),
            k2_clutch_pressure_candidate_bar=float(payload["clutch_k2_pressure_bar"] or 0.0),
            oil_temp_c=float(payload["oil_temp_c"] or 0.0),
            oil_pump_hydraulic_pressure_bar=float(payload["oil_pressure_bar"] or 0.0),
            transmission_oil_monitor_level_percent=float(payload["oil_level_percent"] or 0.0),
            drive_shaft_speed_rpm=float(payload["drive_shaft_speed_rpm"] or 0.0),
            output_shaft_speed_rpm=float(payload["output_shaft_speed_rpm"] or 0.0),
            abuse_index=float(payload["thermal_load_index"] or 0.0),
        )

