from __future__ import annotations

from .models import LiveValues


def compute_health_score(values: LiveValues) -> int:
    k1 = values.get("k1_clutch_pressure_actual", values.get("k1_clutch_pressure_candidate"))
    k2 = values.get("k2_clutch_pressure_actual", values.get("k2_clutch_pressure_candidate"))
    oil = values.get("gearbox_oil_pressure_or_temp_candidate")

    imbalance = abs(k1 - k2)
    pressure_penalty = min(35.0, imbalance * 0.8)
    oil_penalty = min(25.0, max(0.0, oil - 120.0) * 0.12)
    low_pressure_penalty = 12.0 if (k1 > 0 and k2 > 0 and max(k1, k2) < 8) else 0.0
    score = 100.0 - pressure_penalty - oil_penalty - low_pressure_penalty
    return max(0, min(100, round(score)))


def pressure_jump_detected(previous: LiveValues, current: LiveValues, threshold: float = 3.0) -> bool:
    for key in ("k1_clutch_pressure_actual", "k2_clutch_pressure_actual", "k1_clutch_pressure_candidate", "k2_clutch_pressure_candidate"):
        if abs(current.get(key) - previous.get(key)) >= threshold:
            return True
    return False
