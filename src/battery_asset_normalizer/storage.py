import csv
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path
from typing import Any, List

from battery_asset_normalizer.models import PowerSnapshot


class LocalDatasetStore:
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)

    def write_silver(self, snapshots: List[PowerSnapshot]) -> Path:
        path = self.base_path / "silver" / "power_snapshots.csv"
        path.parent.mkdir(parents=True, exist_ok=True)

        rows = [self._to_dict(snapshot) for snapshot in snapshots]

        if not rows:
            path.write_text("")
            return path

        with path.open("w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        return path

    def _to_dict(self, item: Any) -> dict:
        row = asdict(item)

        for key, value in row.items():
            if isinstance(value, (datetime, date)):
                row[key] = value.isoformat()

        return row