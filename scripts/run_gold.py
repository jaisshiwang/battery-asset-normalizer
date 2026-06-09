import json
from datetime import date
from pathlib import Path

from battery_asset_normalizer.pipeline import create_silver_snapshots
from battery_asset_normalizer.resampling import resample_to_energy_intervals
from battery_asset_normalizer.storage import LocalDatasetStore


def load_json(path: str) -> dict:
    with Path(path).open() as file:
        return json.load(file)


store = LocalDatasetStore()

foxess_raw = load_json("tests/fixtures/fox-history-query-v2.json")
growatt_raw = load_json("tests/fixtures/growat-queryhistoricaldata.json")

foxess_snapshots = create_silver_snapshots(
    vendor="foxess",
    raw_data=foxess_raw,
    query_date=date(2025, 10, 2),
    device_info={"device_id": "foxess-sample-device"},
    api_token="mock-token",
)

growatt_snapshots = create_silver_snapshots(
    vendor="growatt",
    raw_data=growatt_raw,
    query_date=date(2025, 9, 23),
    device_info={},
    api_token="mock-token",
)

all_snapshots = foxess_snapshots + growatt_snapshots

foxess_intervals = resample_to_energy_intervals(
    snapshots=foxess_snapshots,
    query_date=date(2025, 10, 2),
)

growatt_intervals = resample_to_energy_intervals(
    snapshots=growatt_snapshots,
    query_date=date(2025, 9, 23),
)

all_intervals = foxess_intervals + growatt_intervals

silver_path = store.write_silver(all_snapshots)
gold_path = store.write_gold(all_intervals)

print(f"Silver dataset written to {silver_path}")
print(f"Gold dataset written to {gold_path}")
print(f"Silver rows: {len(all_snapshots)}")
print(f"Gold rows: {len(all_intervals)}")