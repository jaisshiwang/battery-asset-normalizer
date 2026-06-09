from datetime import date, datetime

from battery_asset_normalizer.models import PowerSnapshot


def test_power_snapshot_creation():
    snapshot = PowerSnapshot(
        vendor="foxess",
        query_date=date(2025, 10, 2),
        timestamp=datetime(2025, 10, 2, 12, 0),

        load_kw=1.2,
        solar_pv_kw=2.3,
        battery_kw=-0.5,
        grid_kw=0.1,
    )

    assert snapshot.vendor == "foxess"
    assert snapshot.load_kw == 1.2