import json
from datetime import date
from pathlib import Path

from battery_asset_normalizer.pipeline import create_silver_snapshots
from battery_asset_normalizer.resampling import resample_to_energy_intervals
from battery_asset_normalizer.storage import LocalDatasetStore


def load_fixture(path: str) -> dict:
    with Path(path).open() as file:
        return json.load(file)


def test_end_to_end_foxess_silver_to_gold(tmp_path):
    raw_data = load_fixture("tests/fixtures/fox-history-query-v2.json")

    snapshots = create_silver_snapshots(
        vendor="foxess",
        raw_data=raw_data,
        query_date=date(2025, 10, 2),
        device_info={"device_id": "foxess-sample-device"},
        api_token="mock-token",
    )

    intervals = resample_to_energy_intervals(
        snapshots=snapshots,
        query_date=date(2025, 10, 2),
    )

    store = LocalDatasetStore(base_path=tmp_path)

    silver_path = store.write_silver(snapshots)
    gold_path = store.write_gold(intervals)

    assert len(snapshots) > 0
    assert len(intervals) == 48

    assert silver_path.exists()
    assert gold_path.exists()

    assert "foxess" in silver_path.read_text()
    assert "foxess" in gold_path.read_text()


def test_end_to_end_growatt_silver_to_gold(tmp_path):
    raw_data = load_fixture("tests/fixtures/growat-queryhistoricaldata.json")

    snapshots = create_silver_snapshots(
        vendor="growatt",
        raw_data=raw_data,
        query_date=date(2025, 9, 23),
        device_info={},
        api_token="mock-token",
    )

    intervals = resample_to_energy_intervals(
        snapshots=snapshots,
        query_date=date(2025, 9, 23),
    )

    store = LocalDatasetStore(base_path=tmp_path)

    silver_path = store.write_silver(snapshots)
    gold_path = store.write_gold(intervals)

    assert len(snapshots) > 0
    assert len(intervals) == 48

    assert silver_path.exists()
    assert gold_path.exists()

    assert "growatt" in silver_path.read_text()
    assert "growatt" in gold_path.read_text()