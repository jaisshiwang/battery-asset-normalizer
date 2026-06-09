import json
from datetime import date
from pathlib import Path

from battery_asset_normalizer.parsers.foxess import parse_foxess
from battery_asset_normalizer.models import PowerSnapshot


def test_parse_foxess_returns_power_snapshots():
    fixture_path = Path("tests/fixtures/fox-history-query-v2.json")

    with fixture_path.open() as file:
        raw_data = json.load(file)

    snapshots = parse_foxess(
        raw_data=raw_data,
        query_date=date(2025, 10, 2),
        device_id="fox-device-1",
    )

    assert len(snapshots) > 0
    assert isinstance(snapshots[0], PowerSnapshot)

    first = snapshots[0]

    assert first.vendor == "foxess"
    assert first.query_date == date(2025, 10, 2)
    assert first.device_id == "fox-device-1"

    assert isinstance(first.load_kw, float)
    assert isinstance(first.solar_pv_kw, float)
    assert isinstance(first.battery_kw, float)
    assert isinstance(first.grid_kw, float)


def test_foxess_snapshots_are_sorted_by_timestamp():
    fixture_path = Path("tests/fixtures/fox-history-query-v2.json")

    with fixture_path.open() as file:
        raw_data = json.load(file)

    snapshots = parse_foxess(
        raw_data=raw_data,
        query_date=date(2025, 10, 2),
        device_id="fox-device-1",
    )

    timestamps = [snapshot.timestamp for snapshot in snapshots]

    assert timestamps == sorted(timestamps)