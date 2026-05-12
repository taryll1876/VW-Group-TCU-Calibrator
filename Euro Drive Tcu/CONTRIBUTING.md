# Contributing

Thanks for helping build the Euro Drive TCU Toolkit. The goal is a clean, adapter-neutral, read-only diagnostic and calibration review stack for VW Group DSG/S tronic work.

## Ground Rules

- Keep default project mode as `read_only`.
- Do not add seed-key calculators, SecurityAccess unlocks, immobilizer bypasses, flash write routines, or proprietary ODIS material.
- Every car-facing function must use `ProjectContext` and safety checks before sending frames.
- Prefer simulator-first development before touching hardware.
- Mark unknown DIDs as candidate placeholders until validated against the exact gearbox code and software version.

## Add A Driver

1. Create `src/vw_tcu_calibrator/drivers/<driver_name>.py`.
2. Subclass `BaseReadOnlyDriver`.
3. Implement `connect()`, `close()`, and `send(arbitration_id, payload)`.
4. Register it in `src/vw_tcu_calibrator/drivers/registry.py`.
5. Add dependency notes to `README_TOOLKIT.md`.
6. Add tests for read-DID behavior and blocked write/protected services.
7. Add public/candidate signal mappings to `data/dq500_map.json`.

## Local Workflow

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -e .[dev]
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m vw_tcu_calibrator.toolkit_cli --driver sim --port 8765
```

Open `index.html` and press **Start Connection** to consume the simulator stream.

## Pull Request Checklist

- Simulator still runs.
- Tests pass.
- README or README_TOOLKIT updated.
- No write/unlock/flash/security bypass code added.
- Units, scale, offsets, and validation status documented for any new signal.
