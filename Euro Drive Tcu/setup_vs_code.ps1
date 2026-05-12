Write-Host "Creating virtual environment..."
py -3 -m venv .venv

Write-Host "Installing dependencies..."
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -e .[dev]

Write-Host "Running dry probe..."
.\.venv\Scripts\python.exe -m vw_tcu_calibrator.cli --config configs/dq500_readonly.yaml --dry-run
