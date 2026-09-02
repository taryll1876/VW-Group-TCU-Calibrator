from __future__ import annotations

from vw_tcu_calibrator.simulation import SimulationEngine


def test_simulation_engine_produces_normalized_signals():
    engine = SimulationEngine()
    payload = engine.snapshot(5.0, now=100.0)

    assert payload["clutch_k1_pressure_bar"] > 0
    assert payload["clutch_k2_pressure_bar"] > 0
    assert payload["thermal_load_index"] >= 0
    assert payload["timestamp"] == 100.0
