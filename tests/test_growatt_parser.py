import json
from datetime import date
from pathlib import Path

import pytest

from battery_asset_normalizer.models import PowerSnapshot
from battery_asset_normalizer.parsers.growatt import parse_growatt


def test_parse_growatt_returns_power_snapshots():
    fixture_path = Path("tests/fixtures/growat-queryhistoricaldata.json")

    with fixture_path.open() as file:
        raw_data = json.load(file)

    snapshots = parse_growatt(
        raw_data=raw_data,
        query_date=date(2025, 9, 23),
    )

    assert len(snapshots) > 0
    assert isinstance(snapshots[0], PowerSnapshot)

    first = snapshots[0]

    assert first.vendor == "growatt"
    assert first.query_date == date(2025, 9, 23)

    assert isinstance(first.load_kw, float)
    assert isinstance(first.solar_pv_kw, float)
    assert isinstance(first.battery_kw, float)
    assert isinstance(first.grid_kw, float)


def test_growatt_converts_watts_to_kilowatts():
    raw_data = {
        "data": {
            "datas": [
                {
                    "time": "2025-09-23 12:00:00",
                    "serialNum": "EGM7F5T043",
                    "plocalLoadTotal": 1000.0,
                    "ppv": 500.0,
                    "pcharge1": 200.0,
                    "pdischarge1": 50.0,
                    "pacToUserTotal": 300.0,
                    "pacToGridTotal": 100.0,
                }
            ]
        }
    }

    snapshots = parse_growatt(
        raw_data=raw_data,
        query_date=date(2025, 9, 23),
    )

    snapshot = snapshots[0]

    assert snapshot.load_kw == 1.0
    assert snapshot.solar_pv_kw == 0.5
    assert snapshot.battery_kw == pytest.approx(0.15)
    assert snapshot.grid_kw == pytest.approx(0.2)


def test_growatt_snapshots_are_sorted_by_timestamp():
    raw_data = {
        "data": {
            "datas": [
                {
                    "time": "2025-09-23 12:05:00",
                    "serialNum": "EGM7F5T043",
                    "plocalLoadTotal": 1000.0,
                },
                {
                    "time": "2025-09-23 12:00:00",
                    "serialNum": "EGM7F5T043",
                    "plocalLoadTotal": 2000.0,
                },
            ]
        }
    }

    snapshots = parse_growatt(
        raw_data=raw_data,
        query_date=date(2025, 9, 23),
    )

    timestamps = [snapshot.timestamp for snapshot in snapshots]

    assert timestamps == sorted(timestamps)