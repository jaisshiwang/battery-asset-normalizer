from datetime import date, datetime
from typing import List, Optional

from battery_asset_normalizer.models import PowerSnapshot


WATTS_TO_KILOWATTS = 1000.0


def parse_growatt(
    raw_data: dict,
    query_date: date,
    device_id: Optional[str] = None,
) -> List[PowerSnapshot]:
    """
    Convert a Growatt SPH historical power response into normalised PowerSnapshot rows.

    Growatt returns row-based snapshots where most power values are reported in W.
    This parser converts all power values to kW.
    """

    rows = raw_data.get("data", {}).get("datas", [])

    snapshots: List[PowerSnapshot] = []

    for row in rows:
        timestamp = row.get("time")

        if timestamp is None:
            continue

        resolved_device_id = device_id or row.get("serialNum")

        load_kw = _w_to_kw(row.get("plocalLoadTotal", 0.0))
        solar_pv_kw = _w_to_kw(row.get("ppv", 0.0))

        battery_charge_kw = _w_to_kw(row.get("pcharge1", 0.0))
        battery_discharge_kw = _w_to_kw(row.get("pdischarge1", 0.0))

        grid_import_kw = _w_to_kw(row.get("pacToUserTotal", 0.0))
        grid_export_kw = _w_to_kw(row.get("pacToGridTotal", 0.0))

        snapshots.append(
            PowerSnapshot(
                vendor="growatt",
                query_date=query_date,
                device_id=resolved_device_id,
                timestamp=_parse_growatt_timestamp(timestamp),
                load_kw=load_kw,
                solar_pv_kw=solar_pv_kw,
                battery_kw=battery_charge_kw - battery_discharge_kw,
                grid_kw=grid_import_kw - grid_export_kw,
            )
        )

    return sorted(snapshots, key=lambda snapshot: snapshot.timestamp)


def _w_to_kw(value: float) -> float:
    return float(value) / WATTS_TO_KILOWATTS


def _parse_growatt_timestamp(timestamp: str) -> datetime:
    """
    Parse Growatt timestamp strings.

    Example:
        2025-09-23 23:59:36
    """

    return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")