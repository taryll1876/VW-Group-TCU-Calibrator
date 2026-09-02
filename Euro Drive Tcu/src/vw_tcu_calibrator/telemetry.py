from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class NormalizedSignal:
    """Normalized, gearbox-agnostic engineering value with source metadata."""

    engineering_name: str
    value: float
    raw_value: float
    unit: str
    source: str
    timestamp: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class SignalNormalizer:
    """Maps raw values into a stable engineering signal layer."""

    _aliases = {
        "clutch_k1_pressure_raw": "clutch_k1_pressure_bar",
        "clutch_k2_pressure_raw": "clutch_k2_pressure_bar",
        "clutch_fill_time_raw": "clutch_fill_time_ms",
        "thermal_load_raw": "thermal_load_index",
        "k1_clutch_pressure_candidate": "clutch_k1_pressure_bar",
        "k2_clutch_pressure_candidate": "clutch_k2_pressure_bar",
    }

    def normalize(
        self,
        *,
        name: str,
        value: float,
        source: str = "unknown",
        unit: str = "raw",
        scaling: dict[str, float] | None = None,
        timestamp: float | None = None,
        confidence: float = 1.0,
        valid: bool = True,
    ) -> NormalizedSignal:
        scale = float((scaling or {}).get("scale", 1.0))
        offset = float((scaling or {}).get("offset", 0.0))
        scaled = value * scale + offset
        engineering_name = self._aliases.get(name.lower(), self._canonical_name(name))
        metadata = {
            "raw_name": name,
            "source": source,
            "unit": unit,
            "scale": scale,
            "offset": offset,
            "confidence": float(confidence),
            "valid": bool(valid),
            "timestamp": timestamp,
        }
        return NormalizedSignal(
            engineering_name=engineering_name,
            value=scaled,
            raw_value=float(value),
            unit=unit,
            source=source,
            timestamp=timestamp,
            metadata=metadata,
        )

    def _canonical_name(self, name: str) -> str:
        cleaned = name.strip().lower().replace(" ", "_")
        if "k1" in cleaned and "pressure" in cleaned:
            return "clutch_k1_pressure_bar"
        if "k2" in cleaned and "pressure" in cleaned:
            return "clutch_k2_pressure_bar"
        if "fill_time" in cleaned:
            return "clutch_fill_time_ms"
        if "thermal" in cleaned and "load" in cleaned:
            return "thermal_load_index"
        if cleaned.endswith("_pressure"):
            return cleaned.replace("_pressure", "_pressure_bar")
        return cleaned


def normalize_signal(*, name: str, value: float, source: str = "unknown", unit: str = "raw", scaling: dict[str, float] | None = None, timestamp: float | None = None, confidence: float = 1.0, valid: bool = True) -> NormalizedSignal:
    return SignalNormalizer().normalize(
        name=name,
        value=value,
        source=source,
        unit=unit,
        scaling=scaling,
        timestamp=timestamp,
        confidence=confidence,
        valid=valid,
    )
