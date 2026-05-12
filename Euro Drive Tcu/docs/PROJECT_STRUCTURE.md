# Project Structure

```text
.
├── index.html                         UI prototype
├── README.md                          Product and hardware brief
├── pyproject.toml                     Python package metadata
├── requirements.txt                   Runtime dependencies
├── configs/dq500_readonly.yaml        Read-only DQ500 profile
├── data/sample_dq500_stream.csv       Sample live-stream values
├── docs/                              Supporting documentation
├── src/vw_tcu_calibrator/             Main Python package
└── tools/uds_dq500_probe.py           Legacy standalone probe
```

Primary entrypoint:

```powershell
python -m vw_tcu_calibrator.cli --config configs/dq500_readonly.yaml --dry-run
```
