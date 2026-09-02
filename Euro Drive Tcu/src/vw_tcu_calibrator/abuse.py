from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence

try:
    import numpy as np
except ImportError:  # pragma: no cover - optional dependency fallback
    np = None


@dataclass
class AbuseIndexModel:
    """Rolling abuse scorer for pressure, thermal, and shaft-load spikes.

    This uses lightweight in-memory ring buffers and optional NumPy acceleration
    for high-frequency processing. The result remains bounded to 0..100.
    """

    window_size: int = 32
    pressure_weight: float = 0.45
    thermal_weight: float = 0.35
    shaft_weight: float = 0.20
    _history: deque[dict[str, float]] = field(default_factory=deque)

    def score(self, samples: Sequence[Mapping[str, float]] | Iterable[Mapping[str, float]]) -> float:
        sample_list = list(samples)
        if not sample_list:
            return 0.0

        values = [self._coerce_sample(sample) for sample in sample_list]
        if not values:
            return 0.0

        pressure = [item["pressure_bar"] for item in values]
        thermal = [item["thermal_index"] for item in values]
        shaft = [item["shaft_rpm"] for item in values]

        # Rolling, bounded-window behavior keeps memory predictable for live telemetry.
        self._history.extend(values)
        if len(self._history) > self.window_size:
            while len(self._history) > self.window_size:
                self._history.popleft()

        if np is not None:
            pressure_arr = np.asarray(pressure, dtype=float)
            thermal_arr = np.asarray(thermal, dtype=float)
            shaft_arr = np.asarray(shaft, dtype=float)
            pressure_mean = float(np.mean(pressure_arr))
            thermal_mean = float(np.mean(thermal_arr))
            shaft_peak = float(np.max(shaft_arr))
            pressure_ramp = float(np.max(pressure_arr) - np.min(pressure_arr))
            thermal_ramp = float(np.max(thermal_arr) - np.min(thermal_arr))
        else:
            pressure_mean = sum(pressure) / len(pressure)
            thermal_mean = sum(thermal) / len(thermal)
            shaft_peak = max(shaft)
            pressure_ramp = max(pressure) - min(pressure)
            thermal_ramp = max(thermal) - min(thermal)

        pressure_component = min(100.0, pressure_mean * 1.4 + pressure_ramp * 0.8)
        thermal_component = min(100.0, thermal_mean * 0.9 + thermal_ramp * 0.6)
        shaft_component = min(100.0, (shaft_peak / 4000.0) * 100.0)

        score = (
            pressure_component * self.pressure_weight
            + thermal_component * self.thermal_weight
            + shaft_component * self.shaft_weight
        )
        return max(0.0, min(100.0, float(score)))

    def _coerce_sample(self, sample: Mapping[str, float]) -> dict[str, float]:
        return {
            "pressure_bar": float(sample.get("pressure_bar", 0.0)),
            "thermal_index": float(sample.get("thermal_index", 0.0)),
            "shaft_rpm": float(sample.get("shaft_rpm", 0.0)),
        }
