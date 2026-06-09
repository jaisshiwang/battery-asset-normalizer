import csv
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path
from typing import Any, List

from battery_asset_normalizer.models import EnergyInterval, PowerSnapshot


class LocalDatasetStore:
    """
    Local file-backed dataset writer.

    Silver:
        data/silver/power_snapshots.csv

    Gold:
        data/gold/energy_intervals.csv
    """

    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)

    def write_silver(
        self,
        snapshots: List[PowerSnapshot],
        overwrite: bool = True,
    ) -> Path:
        path = self.base_path / "silver" / "power_snapshots.csv"
        return self._write_rows(path=path, rows=snapshots, overwrite=overwrite)

    def write_gold(
        self,
        intervals: List[EnergyInterval],
        overwrite: bool = True,
    ) -> Path:
        path = self.base_path / "gold" / "energy_intervals.csv"
        return self._write_rows(path=path, rows=intervals, overwrite=overwrite)

    def _write_rows(
        self,
        path: Path,
        rows: List[Any],
        overwrite: bool,
    ) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)

        serialised_rows = [self._to_dict(row) for row in rows]

        if overwrite:
            mode = "w"
            write_header = True
        else:
            mode = "a"
            write_header = not path.exists() or path.stat().st_size == 0

        if not serialised_rows:
            path.write_text("")
            return path

        with path.open(mode, newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=serialised_rows[0].keys(),
            )

            if write_header:
                writer.writeheader()

            writer.writerows(serialised_rows)

        return path

    def _to_dict(self, item: Any) -> dict:
        row = asdict(item)

        for key, value in row.items():
            if isinstance(value, (datetime, date)):
                row[key] = value.isoformat()

        return row