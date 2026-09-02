from __future__ import annotations

from vw_tcu_calibrator.replay import Event, EventStream, ReplaySession
from vw_tcu_calibrator.telemetry import NormalizedSignal, SignalNormalizer
from vw_tcu_calibrator.validation import ValidationController, ValidationState


def test_signal_normalizer_builds_engineering_signal():
    signal = SignalNormalizer().normalize(
        name="clutch_k1_pressure_raw",
        value=42.0,
        source="dq500",
        unit="raw",
        scaling={"scale": 0.5, "offset": 0.0},
        timestamp=1_000,
        confidence=0.9,
    )

    assert isinstance(signal, NormalizedSignal)
    assert signal.engineering_name == "clutch_k1_pressure_bar"
    assert signal.value == 42.0 * 0.5
    assert signal.metadata["source"] == "dq500"
    assert signal.metadata["confidence"] == 0.9


def test_validation_state_machine_escapes_to_safe_state():
    controller = ValidationController()

    controller.record_voltage(11.5)
    controller.record_handshake_valid(True)
    controller.record_interface_connected(True)
    controller.record_frame_health(True)
    assert controller.state == ValidationState.INTERFACE_VALIDATED

    controller.record_voltage(10.2)
    controller.record_handshake_valid(True)
    controller.record_interface_connected(True)
    controller.record_frame_health(True)
    assert controller.state == ValidationState.PASSIVE_READONLY


def test_replay_session_orders_timeout_and_updates():
    events = [
        Event("signal_update", 100.0, {"name": "clutch_k1_pressure_bar", "value": 20.0}),
        Event("timeout", 110.0, {"name": "session", "reason": "heartbeat"}),
        Event("signal_update", 90.0, {"name": "clutch_k2_pressure_bar", "value": 18.0}),
    ]

    stream = EventStream(events)
    session = ReplaySession(stream)
    ordered = session.ordered_events()

    assert [event.timestamp for event in ordered] == [90.0, 100.0, 110.0]
    assert ordered[0].kind == "signal_update"
    assert ordered[1].payload["value"] == 20.0
