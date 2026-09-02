from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass

from .telemetry import normalize_signal


@dataclass
class SimulationConfig:
    start_oil_temp_c: float = 88.0
    target_oil_temp_c: float = 140.0
    oil_rise_seconds: float = 45.0
    noise: float = 0.7
    base_pressure_bar: float = 28.0


class SimulationEngine:
    """Deterministic, normalized simulation layer for UI and replay testing."""

    def __init__(self, cfg: SimulationConfig | None = None) -> None:
        self.cfg = cfg or SimulationConfig()

    def snapshot(self, elapsed_seconds: float, *, now: float | None = None) -> dict[str, float | int | None]:
        cfg = self.cfg
        frac = min(1.0, elapsed_seconds / cfg.oil_rise_seconds)
        oil_temp = cfg.start_oil_temp_c + (cfg.target_oil_temp_c - cfg.start_oil_temp_c) * (1.0 - math.exp(-frac * 3.5))
        oil_temp += random.uniform(-cfg.noise, cfg.noise)

        k_base = cfg.base_pressure_bar + (oil_temp - cfg.start_oil_temp_c) * 0.45
        k1 = k_base + 2.5 * math.sin(elapsed_seconds * 0.9)
        k2 = k_base + 1.2 * math.cos(elapsed_seconds * 0.6)
        pump_pressure = 35.0 + (oil_temp - cfg.start_oil_temp_c) * 0.3 + 5.0 * math.sin(elapsed_seconds * 0.7)
        oil_level = max(10.0, 85.0 - elapsed_seconds * 0.2)
        base_speed = min(4000.0, elapsed_seconds * 150.0)
        drive_shaft = base_speed + 200.0 * math.sin(elapsed_seconds * 0.5)
        output_shaft = base_speed + 150.0 * math.cos(elapsed_seconds * 0.4)

        thermal_load = min(100.0, max(0.0, (oil_temp - 80.0) * 1.6 + (k1 + k2) * 0.35))

        values: dict[str, float | int | None] = {
            "timestamp": float(now if now is not None else time.time()),
            "clutch_k1_pressure_bar": normalize_signal(
                name="clutch_k1_pressure_raw",
                value=k1,
                source="simulation",
                scaling={"scale": 1.0, "offset": 0.0},
                timestamp=float(now if now is not None else time.time()),
            ).value,
            "clutch_k2_pressure_bar": normalize_signal(
                name="clutch_k2_pressure_raw",
                value=k2,
                source="simulation",
                scaling={"scale": 1.0, "offset": 0.0},
                timestamp=float(now if now is not None else time.time()),
            ).value,
            "oil_pressure_bar": max(0.0, pump_pressure),
            "oil_temp_c": max(0.0, oil_temp),
            "thermal_load_index": thermal_load,
            "oil_level_percent": max(0.0, oil_level),
            "drive_shaft_speed_rpm": max(0.0, drive_shaft),
            "output_shaft_speed_rpm": max(0.0, output_shaft),
        }
        return values

    def iter_snapshots(self, *, interval_seconds: float = 0.25, duration_seconds: float | None = None):
        start = time.time()
        elapsed = 0.0
        while duration_seconds is None or elapsed <= duration_seconds:
            now = time.time()
            yield self.snapshot(elapsed, now=now)
            elapsed = time.time() - start
            time.sleep(interval_seconds)
