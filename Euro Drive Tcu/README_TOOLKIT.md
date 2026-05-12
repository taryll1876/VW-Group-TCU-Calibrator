# Toolkit / UI Server

The UI in `index.html` talks to one stable local endpoint regardless of cable type. The backend translates simulator, J2534, OpenPort 2.0, OBDLink, and raw CAN sources into the same normalized signal payload.

Default stream endpoint:

```text
http://127.0.0.1:8765/stream
```

The stream emits newline-delimited JSON snapshots:

```json
{"type":"snapshot","k1_clutch_pressure_candidate_bar":36.5,"k2_clutch_pressure_candidate_bar":34.5,"oil_temp_c":88.0,"oil_pressure_bar":2.6,"abuse_index":21.6}
```

## Start The Simulator

```powershell
py -3 -m vw_tcu_calibrator.toolkit_cli --driver sim --port 8765
```

Use this while polishing the dashboard. It feeds DQ500-style K1/K2 clutch pressure, oil pressure, oil temperature, and abuse-index data. The simulator deliberately drives oil temperature toward the hot zone so the UI can prove the 130 C red-glow warning.

## Driver Translator

All cable types must implement the same driver shape:

```python
connect() -> None
close() -> None
send(arbitration_id: int, payload: bytes) -> bytes | None
read_did(did: int) -> bytes | None
write_payload(arbitration_id: int, payload: bytes) -> bytes | None
```

The translator reads `data/dq500_map.json`, calls `driver.read_did(...)`, decodes the response, and emits UI-ready fields. The UI does not care whether the data came from OpenPort, J2534, OBDLink, raw CAN, or `sim_car.py`.

## Available Driver Shells

- `src/vw_tcu_calibrator/drivers/sim.py`: software simulator
- `src/vw_tcu_calibrator/drivers/raw_can.py`: `python-can` adapter path
- `src/vw_tcu_calibrator/drivers/j2534.py`: generic SAE J2534 placeholder
- `src/vw_tcu_calibrator/drivers/openport.py`: OpenPort 2.0 wrapper over J2534 concepts
- `src/vw_tcu_calibrator/drivers/obdlink.py`: OBDLink/STN serial skeleton
- `src/vw_tcu_calibrator/oenport.py`: compatibility alias for the common `oenport.py` typo

## Read-Only Rule

Every function that communicates with the vehicle must pass through `ProjectContext` and the safety guards in `src/vw_tcu_calibrator/safety.py`.

In `read_only` mode, allowed UDS services are:

- `0x10` DiagnosticSessionControl
- `0x22` ReadDataByIdentifier
- `0x3E` TesterPresent

Blocked services include SecurityAccess, writes, downloads, transfer data, and flashing routines. Driver authors must not bypass this rule.

## Add A Driver

1. Create a file in `src/vw_tcu_calibrator/drivers/`, for example `my_adapter.py`.
2. Subclass `BaseReadOnlyDriver`.
3. Implement `connect`, `close`, and `send`.
4. Register it in `drivers/registry.py`.
5. Add a dry/mock test proving blocked writes raise `PermissionError`.
6. Document required vendor SDKs, DLLs, COM ports, or device permissions.

Driver contribution checklist:

- Reads work in simulator or bench-safe mode first.
- No seed-key, unlock, or protected programming code.
- No hidden/proprietary maps committed to the repo.
- Clear units and scale/offset added to `data/dq500_map.json`.
- Hardware setup documented in `docs/HARDWARE_BOM.md`.

## OpenPort 2.0 Notes

OpenPort 2.0 is treated as a J2534-style adapter path. The wrapper currently defines the project-facing interface and read-only safety boundary. A real implementation should bind to the vendor J2534 DLL locally and keep all protected write/programming paths disabled unless an authorized workflow is added later.

## Safety Sandbox 1: Virtual Gearbox

The simulator now drives a more realistic engineering signal set:

- RPM follows a sine sweep from idle toward 8000 rpm.
- K1/K2 clutch pressure climbs toward 12 bar as RPM/load increases.
- Simulated clutch exchange spikes occur during the sweep.
- Oil temperature rises at 0.5 C per second.
- Abuse index rises with heat/load and triggers the dashboard red state at 130 C.

## Cable Neutral Entry Point

New drivers should target `GearboxInterface` in `src/vw_tcu_calibrator/interface.py`:

```python
connect()
send_hex(arbitration_id, hex_payload)
read_hex(timeout=1.0)
```

Use `UdsProtocolWrapper` in `src/vw_tcu_calibrator/uds_session.py` for session start, tester-present, read-DID, and timeout handling.

## Data-Only Vehicle Support

Add new cars in `data/vehicle_profiles.json`. Add signal scaling in a map file like `data/dq500_map.json`. Do not hard-code a vehicle into the UI or driver layer unless there is no other option.

## CI / PR Sanity Gate

```powershell
py -3 tests/sanity_check.py
```

This is the minimum check for pull requests: JSON maps parse, simulator outputs sane pressure/RPM values, and write/protected services remain blocked.
