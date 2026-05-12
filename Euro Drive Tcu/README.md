# VW Group TCU Calibrator

Offline prototype for a VW/Audi specialist DSG and S tronic calibration workstation. The current app is a single-page HTML control view for modeling drivability changes before any real bench or vehicle process.

## Current App

- File: `index.html`
- Target family: VW Group DSG/S tronic workflows, including DQ250, DQ381, DQ500, and DL501 style calibrations
- Example vehicles: Audi RS3 8Y, Golf R, S3, TTRS, S4/S5 reference workflows
- Collaborator tuner area: Stav Built
- Live flashing: intentionally disabled in this prototype

## Toolkit / UI Stream (prototype)

To allow the UI to run consistently while adapters/translators are being added, this repo includes a small toolkit backend + a simulated car data source.

- Backend: `src/vw_tcu_calibrator/toolkit_cli.py`
- Stream endpoint: `http://127.0.0.1:8765/stream`
- Simulator source: `src/vw_tcu_calibrator/sim_car.py`

### Run the toolkit server (simulated car)

```powershell
py -3 -m vw_tcu_calibrator.toolkit_cli --sim --port 8765
```

### Use from the UI

1. Open `index.html` in a browser.
2. Click **Start Connection**.
3. When the simulated oil temperature reaches **130°C**, the **Abuse index** card will glow red.

### Contributing & Driver Development

To add a new hardware driver:
1. Inherit from `TcuDriver` in `src/vw_tcu_calibrator/drivers/base.py`.
2. Implement the `read_did` method using your hardware's SDK (e.g., J2534, SocketCAN).
3. Register the driver in the toolkit CLI.

Example for OpenPort 2.0 (J2534):
```python
from .base import TcuDriver

class OpenPortDriver(TcuDriver):
    def connect(self):
        # Initialize J2534 DLL
        pass

    def read_did(self, did: int) -> bytes:
        # Send UDS 0x22 request via J2534
        return b''
```

### Mapping Secret PIDs

DQ500 specific offsets and "secret" PIDs are managed in `data/dq500_map.json`.
Example for Oil Pressure:
- Logical Name: `gearbox_oil_pressure_high_res`
- DID: `0x2213`

This toolkit slice is intentionally read-only and exists for UI/abuse-metric prototyping until real driver adapters are implemented.


## Open In VS Code

Recommended first run:

```powershell
.\setup_vs_code.ps1
```

Manual setup:

```powershell
py -3 -m venv .venv

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -e .[dev]
.\.venv\Scripts\python.exe -m vw_tcu_calibrator.cli --config configs/dq500_readonly.yaml --dry-run
```

Hardware-mode example:

```powershell
.\.venv\Scripts\python.exe -m vw_tcu_calibrator.cli --config configs/dq500_readonly.yaml --stream
```

If your CAN interface is not PCAN, override it:

```powershell
.\.venv\Scripts\python.exe -m vw_tcu_calibrator.cli --config configs/dq500_readonly.yaml --bustype kvaser --channel 0 --stream
```

Run tests:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Project Files

- `index.html`: dark VW specialist UI prototype
- `src/vw_tcu_calibrator/`: reusable Python package
- `configs/dq500_readonly.yaml`: DQ500 read-only profile
- `configs/hardware_manifest.example.yaml`: shop/device manifest template
- `data/sample_dq500_stream.csv`: sample pressure/oil stream
- `docs/HARDWARE_BOM.md`: hardware and PCB build list
- `docs/UDS_READONLY.md`: diagnostic handshake and DID polling guide
- `cpp/uds_readonly_probe.cpp`: C++ read-only starter skeleton
- `tools/uds_dq500_probe.py`: standalone legacy probe
- `.vscode/`: launch/tasks/settings for VS Code

## Product Goal

Build a plug-and-play calibrator for legitimate VW Group TCU work:

1. Connect approved hardware to the car or bench harness.
2. Identify vehicle, TCU family, voltage state, and communication health.
3. Import baseline logs and calibration project files.
4. Tune high-level map targets for drivability, protection, and shift quality.
5. Run safety checks before export.
6. Generate a review pack for the tuner, customer, and bench technician.
7. Only perform programming through lawful, authorized tooling and validated procedures.

This project should not include immobilizer bypass, seed-key cracking, unauthorized firmware extraction, or raw memory unlock workflows.

## Software Modules To Build

- Device manager: detects approved pass-thru, CAN, and CAN FD interfaces
- UDS probe: confirms the interface can reach the target TCU with read-only diagnostic requests
- Vehicle profile manager: stores TCU family, gearbox, engine, model year, and supported protocol profile
- Project manager: encrypted customer/tune projects with version history
- Calibration editor: high-level map controls, tables, comparison, guardrails, and notes
- Log viewer: CSV/MDF-style import, clutch slip, torque request, shift time, temperature, and adaptation graphs
- Simulation engine: abuse index, heat model, shift comfort, protection score, and repeated-shift stress model
- Validation gates: voltage, ignition state, VIN/profile match, interface health, backup present, tuner approval
- Export pack: JSON/PDF-style report with before/after values, notes, risks, and test plan
- Plugin layer: adapters for J2534, CAN FD, bench controller, and future approved hardware

## DQ500 Architecture Notes

Reference target in the prototype:

- Mechatronic controller family: `0BH 927 711 X`
- Gearbox family: DQ500 / 7-speed DSG style workflow
- K1 clutch pack: odd gears, typically 1 / 3 / 5 / 7
- K2 clutch pack: even gears and reverse, typically 2 / 4 / 6 / R
- Critical solenoid watch list: `N472`, `N436`, `N440`, `N471`

Treat these as diagnostic labels until verified against licensed service data for the exact gearbox code and mechatronic revision.

## Read-Only UDS Probe

The project includes a read-only probe script:

```powershell
python .\tools\uds_dq500_probe.py --channel PCAN_USBBUS1 --bustype pcan --tx-id 0x7e1 --rx-id 0x7e9 --stream
```

What it does:

- Sends UDS `DiagnosticSessionControl` extended-session request: `02 10 03 00 00 00 00 00`
- Accepts a positive response beginning with `50 03`
- Polls read-only DIDs with service `0x22`
- Prints timestamped CAN/UDS frames to the console
- Computes a simple live health sketch from available pressure and temperature bytes

The user-provided target response CAN ID is `0x7e9`. In most UDS layouts the transmit/request ID and receive/response ID are different, so the script makes both IDs configurable. Do not assume `0x7e9` is the request ID unless your interface documentation confirms that routing.

Configured read-only DID requests:

- `22 19 01`: candidate clutch pressure / K1 channel
- `22 19 02`: candidate clutch pressure / K2 channel
- `22 19 05`: candidate gearbox oil pressure or oil temperature channel

These identifiers must be validated for the exact DQ500 software version. If a DID is unsupported, the TCU may return a negative response such as `7F 22 31`.

## Security Access Boundary

This repository does not implement seed-key unlock, proprietary SecurityAccess algorithms, ODIS reverse engineering, torque-limit unlocking, immobilizer bypass, or unauthorized flashing.

Allowed direction:

- Log that the TCU is reachable
- Log positive and negative UDS responses
- Read supported public/authorized DIDs
- Build health scoring from live read-only data
- Integrate an authorized vendor SDK or licensed calibration workflow later

Not included:

- Seed-key calculator for `27 xx` SecurityAccess
- Reverse-engineered ODIS algorithms
- Stage 3 torque-limit unlock logic
- Raw flash write routines

## Plug-And-Play Hardware Stack

Minimum shop setup:

- Windows laptop or rugged tablet
- Approved J2534 pass-thru interface for OEM-style programming workflows
- Professional CAN/CAN FD interface for logging and development
- OBD-II J1962 cable with strain relief
- Bench harness for supported VW Group TCU families
- Current-limited 12-14.5 V bench power supply, 30-60 A preferred
- Battery support unit for in-car sessions
- Fused power distribution block
- Emergency stop switch for bench rig
- Isolated USB hub
- Logic analyzer or oscilloscope for bus and power validation
- Digital multimeter
- Thermal probe or IR thermometer for bench testing
- Label printer and cable ID system

Professional interface examples to evaluate:

- SAE J2534-compatible pass-thru devices for standardized PC-to-vehicle programming workflows
- Kvaser CAN/CAN FD interfaces for development and logging
- PEAK PCAN-USB FD for CAN FD development and diagnostics
- Vector VN-series or CANoe/CANalyzer setups for higher-end calibration and validation labs

## Custom PCB Roadmap

The first PCB should be an interface and protection board, not a black-box unlock tool.

Core PCB blocks:

- USB-C or USB-B device input
- Automotive-grade microcontroller with CAN FD support
- Dual CAN/CAN FD transceivers
- Optional LIN transceiver for auxiliary diagnostics
- Galvanic isolation for USB-to-vehicle communication
- Reverse-polarity protection
- Load-dump and transient suppression
- ESD protection on connector lines
- Resettable fuses or blade fuses on supply paths
- Ignition sense input
- Vehicle battery voltage measurement
- Current measurement for bench safety
- Switchable 120 ohm CAN termination
- Status LEDs for power, USB, CAN activity, fault, and programming state
- Hardware write-enable switch or keyed enable input
- Emergency stop input
- J1962 OBD-II connector or rugged automotive connector
- Bench harness connector with keyed pinout per supported TCU adapter

Useful PCB parts/classes to research:

- CAN FD controller or MCU with integrated CAN FD
- Automotive CAN FD transceiver, ISO 11898-2 compliant
- Digital isolator rated for USB/CAN use
- Automotive TVS diodes
- Common-mode choke for CAN lines
- Protected high-side switch
- Buck regulator for 5 V and 3.3 V rails
- Precision voltage divider or ADC front-end for battery monitoring
- Polyfuse or blade fuse holders
- Rugged enclosure with panel-mount connectors

## Bench Harness Kit

Build each harness as a labeled adapter, not a universal loose-wire lead.

- DQ250 adapter
- DQ381 adapter
- DQ500 adapter
- DL501 adapter
- OBD-II vehicle adapter
- Breakout/test adapter with banana plugs for power and ground
- Inline fuse carrier
- Ignition simulation switch
- Termination switch
- Harness label showing supported TCU family, revision, and inspection date

Do not ship or publish unverified pinouts. Validate pinouts from OEM service data, licensed repair information, or supplier documentation before building any harness.

## Safety And Validation Gates

The software should refuse risky actions when:

- Battery voltage is low or unstable
- Interface health check fails
- Vehicle profile does not match the project
- TCU family is unknown
- Baseline backup is missing
- Bench power current limit is not configured
- Thermal model is outside limits
- Tuner approval is missing
- Customer/project identity is incomplete
- The operation would require unauthorized access

## Data Model Ideas

Project fields:

- Customer name or internal job ID
- Vehicle VIN or anonymized vehicle ID
- Model, year, engine, gearbox, TCU family
- Hardware interface used
- Baseline software version
- Calibration pack name
- Tuner name
- Road-log files
- Bench-log files
- Approval status
- Export history

Calibration groups:

- Launch and take-off
- Clutch kiss-point adaptation
- K1/K2 handover
- Pressure ramp shaping
- Torque intervention timing
- D-mode schedule
- S-mode schedule
- Manual paddle behavior
- Downshift damping
- Thermal protection
- Abuse counter strategy
- Customer comfort target

## References

- SAE J2534 describes a standardized pass-thru interface between a PC and vehicle for reprogramming workflows: https://webstore.ansi.org/standards/sae/saej25341_05002022
- Kvaser CAN FD overview notes that CAN FD increases payload size up to 64 bytes and can improve bandwidth for flashing and diagnostics: https://kvaser.com/about-can/can-fd/
- PEAK PCAN-USB FD is an example of a CAN FD USB interface family used for diagnostics and development: https://www.peak-system.com/PCAN-USB-FD.365.0.html
- Vector CAN/CAN FD tooling is commonly used in professional automotive network development and validation: https://www.vector.com/int/en/products/products-a-z/hardware/network-interfaces/

## Legal Position

This project is for lawful diagnostics, calibration planning, logging, and review. Real vehicle programming must use authorized access, licensed data, correct service information, proper power support, and validated hardware. Emissions, warranty, road-use, and motorsport rules vary by location and vehicle use.

## Toolkit Driver Contributions

The toolkit layer keeps the UI stable while adapters change underneath it. New connector work should live under `src/vw_tcu_calibrator/drivers/` and should emit the normalized signal schema consumed by `ToolkitSignalSnapshot`.

Supported driver targets in the current structure:

- Simulator: `--driver sim`
- Raw CAN through `python-can`: `--driver raw-can`
- Generic J2534 shell: `--driver j2534`
- OpenPort 2.0 wrapper: `--driver openport2`
- OBDLink/STN serial shell: `--driver obdlink`

Start the simulated backend for the dashboard:

```powershell
py -3 -m vw_tcu_calibrator.toolkit_cli --driver sim --port 8765
```

Then open `index.html` and press **Start Connection**. The UI will consume `http://127.0.0.1:8765/stream` and keep the same dashboard no matter which driver is behind the translator.

### Add A Driver

1. Add a driver file under `src/vw_tcu_calibrator/drivers/`.
2. Subclass `BaseReadOnlyDriver`.
3. Implement `connect()`, `close()`, and `send(arbitration_id, payload)`.
4. Register the driver name in `drivers/registry.py`.
5. Add a sample command to `README_TOOLKIT.md`.
6. Add or update tests proving write/protected services are blocked in `read_only` mode.
7. Add any new public DID scale/offset data to `data/dq500_map.json` with a validation status.

### Safety Rule

Every function that talks to the vehicle must check project mode. Current project mode is `read_only`; it allows diagnostic session, tester-present, and read-DID requests only. SecurityAccess, seed-key, write, download, transfer, and flash commands are blocked.

### DQ500 Map Data

`data/dq500_map.json` contains open/candidate mapping data for the simulator and translator. Do not commit proprietary secret addresses or reverse-engineered security material. Unknown DIDs should be marked as placeholders until validated for a specific gearbox code and software version.

## Elite Contributor Program

This project is being shaped as a professional, cable-neutral VW/Audi gearbox engineering toolkit. The highest-value contributors are people who can make the platform safer, more measurable, and easier to extend without locking it to one cable or one car.

### Contributor Skill Tracks

- Embedded interface engineers: C/C++ for STM32, ESP32, or Infineon TriCore; automotive power protection; CAN transceivers; isolation; boot-safe firmware design.
- Diagnostics engineers: UDS / ISO 14229, CAN / ISO 11898, DoIP, J2534, tester-present timing, negative response handling, trace analysis.
- Data architecture engineers: JSON schemas, vehicle profile design, typed signal maps, log ingestion, reproducible calibration projects.
- Backend/math specialists: Python, pandas, NumPy, DSP, signal filtering, thermal modeling, clutch pressure models, abuse-index physics.
- Visualization engineers: React, Flutter, Qt, WebGL/canvas, real-time plotting, dark motorsport UI systems, ergonomic tuner workflows.
- Test bench builders: simulator design, HIL/SIL rigs, CI gatekeepers, reproducible bench logs, validation dashboards.

### Automotive Abstraction Layer

The core rule is simple: the UI must stay the same no matter what cable is used. A contributor who wants to support a new cable should implement `GearboxInterface`:

```python
connect() -> None
send_hex(arbitration_id: int, hex_payload: str) -> None
read_hex(timeout: float = 1.0) -> str | None
```

The toolkit already has driver shells for simulator, raw CAN, J2534, OpenPort 2.0, and OBDLink. The translator converts cable-specific reads into one normalized signal schema so the dashboard does not care whether data came from a VCI, OpenPort 2.0, OBDLink, python-can, or the virtual gearbox.

### UDS Protocol Wrapper

`src/vw_tcu_calibrator/uds_session.py` handles the boring but critical UDS session work:

- opens the selected `GearboxInterface`
- requests extended diagnostic session with `02 10 03 00 00 00 00 00`
- checks for positive response `50 03`
- maintains tester-present with `02 3E 00 00 00 00 00 00`
- centralizes timeout behavior
- routes all frames through read-only safety checks

### Standardized Vehicle JSON

`data/vehicle_profiles.json` lets contributors add a new car without rewriting code. Add a vehicle object with make, model, generation, gearbox family, request/response IDs, and a signal-map file. This is the path for Golf R, Audi S3, RS3, and future VW Group DSG/S tronic profiles.

`data/dq500_map.json` stores candidate read-only DIDs and scaling. `data/torque_splitter_map.json` documents the RS3 8Y torque-splitter research status and placeholder signals for contributor validation.

### Virtual Gearbox Simulator

`src/vw_tcu_calibrator/sim_car.py` is Safety Sandbox 1: the virtual gearbox. It now models:

- virtual RPM sine sweep from idle toward 8000 rpm
- K1/K2 pressure rising toward 12 bar as RPM/load climbs
- pressure spikes during simulated clutch exchange
- virtual gear selection from RPM bands
- oil temperature rising at 0.5 C per second
- abuse index increasing with heat and load

Run it:

```powershell
py -3 -m vw_tcu_calibrator.toolkit_cli --driver sim --port 8765
```

Open `index.html`, choose units, and press **Start Connection**.

### CSV Logging For Excel

Save the live stream for Excel or pandas:

```powershell
py -3 tools/save_live_csv.py --output logs/live_stream_export.csv --limit 500
```

### Pull Request Gatekeeper

Run the sanity gate before proposing changes:

```powershell
py -3 tests/sanity_check.py
```

The gate validates JSON maps, runs the simulator, checks pressure limits, and proves write/protected UDS services remain blocked.

### RS3 8Y Torque Splitter Research

Public Audi sources confirm the 8Y RS3 torque splitter uses two electronically controlled rear multi-disc clutches, one per rear drive shaft. Inputs include wheel speeds, longitudinal/lateral acceleration, steering angle, accelerator position, selected gear, yaw angle, and drive-select mode. Public Audi material does not publish validated CAN IDs or DIDs for the left/right torque-splitter clutch channels. Those fields remain `TBD_FROM_LOGS` in `data/torque_splitter_map.json` until contributors validate them from lawful logs or authorized diagnostics.

Sources:

- Audi Technology Portal: https://www.audi-technology-portal.de/en/drivetrain/quattro_en/audi-rs-3-torque-splitter-en
- Audi MediaCenter: https://www.audi-mediacenter.com/en/press-releases/a-matter-of-lateral-the-torque-splitter-in-the-new-audi-rs-3-14067

### Non-Negotiable Safety Boundary

This repository is read-only by default. Do not add seed-key calculators, SecurityAccess unlocks, protected write routines, RequestDownload/TransferData flashing, immobilizer bypass, or proprietary ODIS reverse-engineering material. The goal is a serious diagnostics, simulator, visualization, and calibration-review platform.
