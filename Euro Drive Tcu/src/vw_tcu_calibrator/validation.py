from __future__ import annotations

from enum import Enum


class ValidationState(str, Enum):
    INIT = "INIT"
    INTERFACE_VALIDATED = "INTERFACE_VALIDATED"
    SESSION_ACTIVE = "SESSION_ACTIVE"
    DEGRADED = "DEGRADED"
    PASSIVE_READONLY = "PASSIVE_READONLY"


class ValidationController:
    """Deterministic validation gating and fallback behaviour."""

    def __init__(self) -> None:
        self.state = ValidationState.INIT
        self._voltage_ok: bool | None = None
        self._handshake_valid: bool | None = None
        self._interface_connected: bool | None = None
        self._frame_health: bool | None = None

    def record_voltage(self, voltage: float) -> None:
        self._voltage_ok = voltage >= 11.0
        self._recompute_state()

    def record_handshake_valid(self, valid: bool) -> None:
        self._handshake_valid = valid
        self._recompute_state()

    def record_interface_connected(self, connected: bool) -> None:
        self._interface_connected = connected
        self._recompute_state()

    def record_frame_health(self, healthy: bool) -> None:
        self._frame_health = healthy
        self._recompute_state()

    def _recompute_state(self) -> None:
        if (
            self._voltage_ok is False
            or self._handshake_valid is False
            or self._interface_connected is False
            or self._frame_health is False
        ):
            self.state = ValidationState.PASSIVE_READONLY
            return

        if (
            self._voltage_ok is not None
            and self._handshake_valid is not None
            and self._interface_connected is not None
            and self._frame_health is not None
        ):
            self.state = ValidationState.INTERFACE_VALIDATED
            return

        self.state = ValidationState.INIT

    def allow_simulation(self) -> bool:
        return self.state not in {ValidationState.PASSIVE_READONLY, ValidationState.DEGRADED}
