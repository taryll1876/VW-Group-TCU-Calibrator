# TODO - Euro Drive Tcu toolkit + simulator + UI wiring

## Step 1: Backend “toolkit” server + translator abstraction [DONE]
- Create a Python web server module under `src/vw_tcu_calibrator/server.py`.
- Define internal signal schema.
- Implement translator layer in `src/vw_tcu_calibrator/translator.py`.

## Step 2: Simulator `sim_car.py` [DONE]
- Implement simulation logic and feed into server.

## Step 3: Driver scaffolding [IN PROGRESS]
- Add `drivers/openport.py` wrapper skeleton.
- Add base driver class for J2534/CAN abstraction.

## Step 4: dq5 mapping [DONE]
- Created `data/dq500_map.json` with high-res oil pressure PID (0x2213).

## Step 5: UI wiring [DONE]
- Wired "Start Connection" to toolkit stream.
- Implement real-time updates for oil temp and abuse index.
- Implement: abuse index glows red when oil temp >= 130°C.

## Step 6: README updates [DONE]
- Document how to add drivers and mapping entries.
- Document how to run simulation.

## Step 7: Calibration Features [NEW]
- Implement modeling for Shift Time reduction and AMAX mode.
- Map part-throttle and WOT target curves for modeling.

## Step 7: Tests / smoke checks
- Run `python -m vw_tcu_calibrator.cli --dry-run` as a baseline.
- Smoke-test the server and simulator stream.

Engineering Master Task List
1. Hardware & Firmware (The Interface Layer)
PCB Design Validation: Perform a full review of the Custom PCB Roadmap against ISO 7637-2 transient standards.

Galvanic Isolation: Finalize the ISO7741 integration to ensure 100% isolation between the vehicle CAN bus and the host PC.

Native USB Implementation: Evaluate replacing the FT232H with a native STM32G474 USB stack to reduce latency for UDS 'Tester Present' handshakes.

Bare-Metal CAN FD: Optimize the TJA1443 transceiver logic for stable 5 Mbit/s data rates on MQB Evo platforms.

2. Systems & Protocol (The Transport Layer)
Unified Session Orchestration: Refactor uds_session.py to automatically handle timing variations across DQ250, DQ381, and DL501 families.

J2534 Driver Hardening: Build a robust SAE J2534 wrapper that handles Windows DLL threading without blocking the Python event loop.

Async Telemetry Pipeline: Optimize the Live Stream Dashboard to handle high-frequency UDS 0x22 polling without frame drops.

SecurityAccess Guardrails: Implement a "Hardware Lock" in the UDS Protocol Wrapper that physically prevents write commands when in read_only mode.

3. Data & Simulation (The Physics Layer)
Clutch Modeling: Refine the K1/K2 handover physics in sim_car.py using real-world pressure datasets.

Telemetry Normalization: Convert dq500_map.json DIDs into a standardized physical unit schema (Bar, Celsius, Nm) shared across all vehicle profiles.

Abuse Index Algorithm: Develop a predictive "Heat-Soak" model that calculates clutch wear based on oil temperature and high-frequency pressure oscillations.

Log Replay Engine: Enable the CSV logging tool to act as a data source for the simulator, allowing offline "playback" of recorded drives.

4. UI/UX & HMI (The Operator Layer)
Validation Gate Feedback: Enhance the index.html dashboard to show exactly why a validation gate is failing (e.g., specific voltage drop or handshake timeout).

Real-time Charting: Replace static elements with high-performance Webkit/Canvas charts to visualize the 7x3 shift-pressure heatmap during live sessions.

Export Review Pack: Automate the generation of a "Tuner Review" PDF that diffs the baseline software against the target calibration targets.

Safety Interlocks: Implement a mandatory "Session Audit" log that records every diagnostic handshake for liability and safety tracking.

5. Quality Assurance (The Integrity Layer)
Sanity Gate Expansion: Add hardware-in-the-loop (HIL) tests to sanity_check.py to verify Zero-Footprint compliance.

DID Discovery Tools: Develop a signal sniffing workflow for RS3 8Y Torque Splitter research using SavvyCAN log interpretation.

BOM Sourcing: Verify all components in HARDWARE_BOM.md for AEC-Q100 (Automotive Grade) availability and lead times.

Mission Objective: Ensure every line of code maintains the Non-Negotiable Safety Boundary while delivering the world's most precise DSG/S tronic calibration workflow


Core System & Infrastructure
Unified Session Orchestration: Refactor uds_session.py to automatically handle timing variations and session management across DQ250, DQ381, and DL501 families.

Driver Hardening: Complete the driver scaffolding by finalizing the base driver class and the openport.py wrapper for robust J2534/CAN abstraction.

Async Telemetry Pipeline: Optimize the server.py and translator.py to handle high-frequency UDS 0x22 polling without UI lag or frame drops.

SecurityAccess Guardrails: Implement a "Hardware Lock" in the transport layer to physically prevent write commands when the system is in its mandated read_only posture.

Hardware & Firmware Integration
PCB Design Validation: Review the hardware against ISO 7637-2 standards, ensuring the ISO7741 digital isolator provides 100% galvanic isolation between the vehicle and the PC.

Native USB Migration: Evaluate moving from FT232H to native STM32G474 USB control to minimize latency during critical diagnostic handshakes.

Thermal & Power Management: Validate the LM25011-Q1 buck regulator for high-current bench sessions and ensure the TJA1443 transceiver maintains signal integrity at 5 Mbit/s. 

Data Physics & Advanced Simulation
Clutch & Thermal Modeling: Refine the simulation logic in sim_car.py to include K1/K2 pressure curves and an "Abuse Index" that responds to oil temp thresholds.

Telemetry Normalization: Standardize dq500_map.json into physical units (Bar, °C, Nm) to enable cross-platform comparisons.

Log Replay Engine: Enable the save_live_csv.py tool to act as a data provider, allowing the dashboard to "replay" recorded diagnostic sessions for offline review.


: UI/UX & Operator Integrity
Validation Gate Feedback: Expand the UI wiring to show detailed error codes if a validation gate fails (e.g., low battery voltage or loss of CAN sync).

Shift-Pressure Heatmaps: Implement high-performance canvas-based visualization for the 7x3 heatmap during live data streams.

Calibration Review Workflow: Finalize the "Export Review Pack" which diffs the mechatronic state before and after a workstation session for the technician's audit trail.
