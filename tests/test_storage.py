from datetime import date, datetime

from battery_asset_normalizer.models import PowerSnapshot
from battery_asset_normalizer.storage import LocalDatasetStore


def test_write_silver_dataset(tmp_path):
    store = LocalDatasetStore(base_path=tmp_path)

    snapshots = [
        PowerSnapshot(
            vendor="foxess",
            query_date=date(2025, 10, 2),
            device_id="fox-device-1",
            timestamp=datetime(2025, 10, 2, 1, 0),
            load_kw=0.2,
            solar_pv_kw=0.0,
            battery_kw=-0.3,
            grid_kw=0.1,
        )
    ]

    output_path = store.write_silver(snapshots)

    assert output_path.exists()

    content = output_path.read_text()

    assert "vendor,query_date,timestamp,load_kw,solar_pv_kw,battery_kw,grid_kw,device_id" in content
    assert "foxess" in content
    assert "2025-10-02" in content
    assert "fox-device-1" in content