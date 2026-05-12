from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass

from .server import ToolkitSignalSnapshot


@dataclass
class SimCarConfig:
    start_oil_temp_c: float = 88.0
    max_oil_temp_c: float = 145.0
    oil_rise_c_per_second: float = 0.5
    rpm_idle: float = 900.0
    rpm_limit: float = 8000.0
    rpm_period_seconds: float = 16.0
    noise: float = 0.12


def _sine01(x: float) -> float:
    return (math.sin(x) + 1.0) / 2.0


def sim_car_snapshots(*, cfg: SimCarConfig | None = None):
    """Virtual VW/Audi gearbox.

    Logic model:
    - RPM follows a sine sweep from idle toward 8000 rpm.
    - Clutch pressure rises non-linearly toward 12 bar as RPM/load climbs.
    - K1/K2 alternate emphasis by virtual gear and add short pressure spikes.
    - Oil temperature rises at 0.5 C per second until capped.
    """
    if cfg is None:
        cfg = SimCarConfig()

    t0 = time.time()
    while True:
        t = time.time() - t0
        rpm_phase = _sine01((t / cfg.rpm_period_seconds) * math.tau)
        rpm = cfg.rpm_idle + (cfg.rpm_limit - cfg.rpm_idle) * rpm_phase
        throttle_pct = 18.0 + 82.0 * rpm_phase
        oil_temp = min(cfg.max_oil_temp_c, cfg.start_oil_temp_c + (t * cfg.oil_rise_c_per_second))

        virtual_gear = max(1, min(7, int(rpm / 1100) + 1))
        load = max(0.0, min(1.0, (rpm - cfg.rpm_idle) / (cfg.rpm_limit - cfg.rpm_idle)))
        base_pressure = 2.0 + 10.0 * (load ** 1.35)
        spike = 1.3 if (t % 2.8) < 0.22 else 0.0
        sine_trim = math.sin(t * 5.0) * 0.18

        if virtual_gear in {1, 3, 5, 7}:
            k1 = base_pressure + spike + sine_trim
            k2 = base_pressure * 0.72 + sine_trim * 0.4
        else:
            k1 = base_pressure * 0.72 + sine_trim * 0.4
            k2 = base_pressure + spike + sine_trim

        k1 += random.uniform(-cfg.noise, cfg.noise)
        k2 += random.uniform(-cfg.noise, cfg.noise)
        oil_pressure = 1.5 + base_pressure * 0.18 + spike * 0.05
        abuse_index = max(0.0, min(100.0, (oil_temp - 70.0) * 1.2 + load * 18.0))

        yield ToolkitSignalSnapshot(
            k1_clutch_pressure_candidate_bar=max(0.0, min(12.0, k1)),
            k2_clutch_pressure_candidate_bar=max(0.0, min(12.0, k2)),
            oil_temp_c=max(0.0, oil_temp),
            oil_pressure_bar=max(0.0, oil_pressure),
            abuse_index=abuse_index,
            rpm=rpm,
            throttle_pct=throttle_pct,
            virtual_gear=virtual_gear,
        )
