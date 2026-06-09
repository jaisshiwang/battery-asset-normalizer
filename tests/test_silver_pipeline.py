from datetime import date

import pytest

from battery_asset_normalizer.pipeline import create_silver_snapshots
from battery_asset_normalizer.storage import LocalDatasetStore


def test_create_silver_snapshots_for_growatt():
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

    snapshots = create_silver_snapshots(
        vendor="growatt",
        raw_data=raw_data,
        query_date=date(2025, 9, 23),
        device_info={},
        api_token="mock-token",
    )

    assert len(snapshots) == 1
    assert snapshots[0].vendor == "growatt"


def test_create_silver_snapshots_for_foxess():
    raw_data = {
        "result": [
            {
                "datas": [
                    {
                        "variable": "loadsPower",
                        "data": [
                            {
                                "time": "2025-10-02 01:00:00 BST+0100",
                                "value": 0.5,
                            }
                        ],
                    },
                    {
                        "variable": "pvPower",
                        "data": [
                            {
                                "time": "2025-10-02 01:00:00 BST+0100",
                                "value": 0.2,
                            }
                        ],
                    },
                ]
            }
        ]
    }

    snapshots = create_silver_snapshots(
        vendor="foxess",
        raw_data=raw_data,
        query_date=date(2025, 10, 2),
        device_info={"device_id": "fox-device-1"},
        api_token="mock-token",
    )

    assert len(snapshots) == 1
    assert snapshots[0].vendor == "foxess"
    assert snapshots[0].device_id == "fox-device-1"


def test_create_silver_snapshots_rejects_unknown_vendor():
    with pytest.raises(ValueError):
        create_silver_snapshots(
            vendor="tesla",
            raw_data={},
            query_date=date(2025, 10, 2),
            device_info={},
            api_token="mock-token",
        )

