from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .drivers.base import TcuDriver
from .server import ToolkitSignalSnapshot

class HardwareTranslator:
    """
    Translates raw hardware responses into normalized ToolkitSignalSnapshots
    using a JSON mapping file.
    """

    def __init__(self, driver: TcuDriver, map_path: Path):
        self.driver = driver
        with open(map_path, 'r') as f:
            self.map_data = json.load(f)

    def __iter__(self):
        while True:
            signals = {}
            for entry in self.map_data.get("mappings", []):
                did_int = int(entry["did"], 16)
                raw_resp = self.driver.read_did(did_int)

                if raw_resp and len(raw_resp) >= 5:
                    # Simple decoding: Assume bytes 4-5 are the u16 value
                    # This would be expanded for specific PID formats
                    raw_val = (raw_resp[-2] << 8) | raw_resp[-1]
                    signals[entry["signal"]] = (raw_val * entry["scale"]) + entry["offset"]
                else:
                    signals[entry["signal"]] = None

            yield ToolkitSignalSnapshot(
                k1_clutch_pressure_candidate_bar=signals.get("k1_clutch_pressure_candidate_bar"),
                k2_clutch_pressure_candidate_bar=signals.get("k2_clutch_pressure_candidate_bar"),
                oil_temp_c=signals.get("oil_temp_c"),
                oil_pressure_bar=signals.get("oil_pressure_bar")
            )