from __future__ import annotations

import argparse
import csv
import json
import time
from urllib.request import urlopen


def main() -> int:
    parser = argparse.ArgumentParser(description="Save toolkit live stream to CSV for Excel/pandas analysis.")
    parser.add_argument("--url", default="http://127.0.0.1:8765/stream")
    parser.add_argument("--output", default="logs/live_stream_export.csv")
    parser.add_argument("--limit", type=int, default=0, help="Stop after N snapshots; 0 means forever.")
    args = parser.parse_args()

    fields = ["ts", "rpm", "virtual_gear", "k1_clutch_pressure_candidate_bar", "k2_clutch_pressure_candidate_bar", "oil_pressure_bar", "oil_temp_c", "abuse_index"]
    count = 0
    with urlopen(args.url, timeout=10) as response, open(args.output, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for raw in response:
            payload = json.loads(raw.decode("utf-8"))
            if payload.get("type") != "snapshot":
                continue
            writer.writerow({key: payload.get(key) for key in fields})
            fh.flush()
            count += 1
            if args.limit and count >= args.limit:
                break
            time.sleep(0.0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
