# Toolkit / UI Server

This repository’s UI (`index.html`) is a static dashboard. The “Start Connection” button will connect to a local toolkit backend which streams normalized vehicle signals for prototyping.

## Run the toolkit server (simulated car)

```powershell
py -3 -m vw_tcu_calibrator.toolkit_cli --sim --port 8765
```

Default endpoint:
- `http://127.0.0.1:8765/stream` (newline-delimited JSON frames)

## Notes

- Current implementation streams simulated data for UI prototyping.
- The translator/driver layer is planned next to normalize real adapter outputs into the same signal schema.

