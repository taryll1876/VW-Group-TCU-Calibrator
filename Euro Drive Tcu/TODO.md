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
