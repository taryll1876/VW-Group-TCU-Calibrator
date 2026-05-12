from __future__ import annotations

import json
from pathlib import Path

from .core import ProjectContext
from .drivers.base import TcuDriver
from .server import ToolkitSignalSnapshot


class HardwareTranslator:
    """Normalize adapter-specific responses into the UI signal schema."""

    def __init__(self, driver: TcuDriver, map_path: Path, *, context: ProjectContext | None = None):
        self.driver = driver
        self.context = context or driver.context
        with open(map_path, "r", encoding="utf-8") as f:
            self.map_data = json.load(f)

    def __iter__(self):
        while True:
            signals = {}
            for entry in self.map_data.get("mappings", []):
                did_int = int(entry["did"], 16)
                raw_resp = self.driver.read_did(did_int)

                if raw_resp and len(raw_resp) >= 6 and raw_resp[1] == 0x62:
                    raw_val = (raw_resp[4] << 8) | raw_resp[5]
                    signals[entry["signal"]] = (raw_val * entry.get("scale", 1.0)) + entry.get("offset", 0.0)
                else:
                    signals[entry["signal"]] = None

            yield ToolkitSignalSnapshot(
                k1_clutch_pressure_candidate_bar=signals.get("k1_clutch_pressure_candidate_bar"),
                k2_clutch_pressure_candidate_bar=signals.get("k2_clutch_pressure_candidate_bar"),
                oil_temp_c=signals.get("oil_temp_c"),
                oil_pressure_bar=signals.get("oil_pressure_bar"),
                abuse_index=signals.get("abuse_index"),
            )
