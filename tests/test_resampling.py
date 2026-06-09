from datetime import date, datetime

import pytest

from battery_asset_normalizer.models import PowerSnapshot
from battery_asset_normalizer.resampling import resample_to_energy_intervals


def _find_interval(intervals, period_start):
    return next(
        interval
        for interval in intervals
        if interval.period_start == period_start
    )


def test_one_kw_for_thirty_minutes_equals_half_kwh():
    snapshots = [
        PowerSnapshot(
            vendor="foxess",
            query_date=date(2025, 10, 2),
            device_id="device-1",
            timestamp=datetime(2025, 10, 2, 10, 0),
            load_kw=1.0,
            solar_pv_kw=0.0,
            battery_kw=0.0,
            grid_kw=0.0,
        ),
        PowerSnapshot(
            vendor="foxess",
            query_date=date(2025, 10, 2),
            device_id="device-1",
            timestamp=datetime(2025, 10, 2, 10, 30),
            load_kw=0.0,
            solar_pv_kw=0.0,
            battery_kw=0.0,
            grid_kw=0.0,
        ),
    ]

    intervals = resample_to_energy_intervals(
        snapshots=snapshots,
        query_date=date(2025, 10, 2),
    )

    target = _find_interval(
        intervals,
        datetime(2025, 10, 2, 10, 0),
    )

    assert target.load_kwh == pytest.approx(0.5)


def test_interval_crossing_bucket_boundary_is_prorated():
    snapshots = [
        PowerSnapshot(
            vendor="foxess",
            query_date=date(2025, 10, 2),
            device_id="device-1",
            timestamp=datetime(2025, 10, 2, 10, 20),
            load_kw=3.0,
            solar_pv_kw=0.0,
            battery_kw=0.0,
            grid_kw=0.0,
        ),
        PowerSnapshot(
            vendor="foxess",
            query_date=date(2025, 10, 2),
            device_id="device-1",
            timestamp=datetime(2025, 10, 2, 10, 40),
            load_kw=0.0,
            solar_pv_kw=0.0,
            battery_kw=0.0,
            grid_kw=0.0,
        ),
    ]

    intervals = resample_to_energy_intervals(
        snapshots=snapshots,
        query_date=date(2025, 10, 2),
    )

    bucket_10_00 = _find_interval(
        intervals,
        datetime(2025, 10, 2, 10, 0),
    )
    bucket_10_30 = _find_interval(
        intervals,
        datetime(2025, 10, 2, 10, 30),
    )

    assert bucket_10_00.load_kwh == pytest.approx(0.5)
    assert bucket_10_30.load_kwh == pytest.approx(0.5)


def test_final_snapshot_is_not_extrapolated():
    snapshots = [
        PowerSnapshot(
            vendor="growatt",
            query_date=date(2025, 9, 23),
            device_id="device-1",
            timestamp=datetime(2025, 9, 23, 23, 40),
            load_kw=2.0,
            solar_pv_kw=0.0,
            battery_kw=0.0,
            grid_kw=0.0,
        )
    ]

    intervals = resample_to_energy_intervals(
        snapshots=snapshots,
        query_date=date(2025, 9, 23),
    )

    bucket_23_30 = _find_interval(
        intervals,
        datetime(2025, 9, 23, 23, 30),
    )

    assert bucket_23_30.load_kwh == 0.0


def test_battery_and_grid_signs_are_preserved():
    snapshots = [
        PowerSnapshot(
            vendor="growatt",
            query_date=date(2025, 9, 23),
            device_id="device-1",
            timestamp=datetime(2025, 9, 23, 12, 0),
            load_kw=0.0,
            solar_pv_kw=0.0,
            battery_kw=-2.0,
            grid_kw=1.0,
        ),
        PowerSnapshot(
            vendor="growatt",
            query_date=date(2025, 9, 23),
            device_id="device-1",
            timestamp=datetime(2025, 9, 23, 12, 30),
            load_kw=0.0,
            solar_pv_kw=0.0,
            battery_kw=0.0,
            grid_kw=0.0,
        ),
    ]

    intervals = resample_to_energy_intervals(
        snapshots=snapshots,
        query_date=date(2025, 9, 23),
    )

    target = _find_interval(
        intervals,
        datetime(2025, 9, 23, 12, 0),
    )

    assert target.battery_kwh == pytest.approx(-1.0)
    assert target.grid_kwh == pytest.approx(0.5)


def test_can_resample_to_five_minute_intervals():
    snapshots = [
        PowerSnapshot(
            vendor="foxess",
            query_date=date(2025, 10, 2),
            device_id="device-1",
            timestamp=datetime(2025, 10, 2, 10, 0),
            load_kw=1.0,
            solar_pv_kw=0.0,
            battery_kw=0.0,
            grid_kw=0.0,
        ),
        PowerSnapshot(
            vendor="foxess",
            query_date=date(2025, 10, 2),
            device_id="device-1",
            timestamp=datetime(2025, 10, 2, 10, 5),
            load_kw=0.0,
            solar_pv_kw=0.0,
            battery_kw=0.0,
            grid_kw=0.0,
        ),
    ]

    intervals = resample_to_energy_intervals(
        snapshots=snapshots,
        query_date=date(2025, 10, 2),
        interval_minutes=5,
    )

    target = _find_interval(
        intervals,
        datetime(2025, 10, 2, 10, 0),
    )

    assert target.load_kwh == pytest.approx(1.0 * (5 / 60), abs=1e-6)