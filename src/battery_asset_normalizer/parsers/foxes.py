from collections import defaultdict
from datetime import date, datetime
from typing import Dict, List, Optional

from battery_asset_normalizer.models import PowerSnapshot


FOX_CHANNEL_MAPPING = {
    "loadsPower": "load_kw",
    "pvPower": "solar_pv_kw",
    "gridConsumptionPower": "grid_import_kw",
    "feedinPower": "grid_export_kw",
    "batChargePower": "battery_charge_kw",
    "batDischargePower": "battery_discharge_kw",
}


def parse_foxess(
    raw_data: dict,
    query_date: date,
    device_id: Optional[str] = None,
) -> List[PowerSnapshot]:
    """
    Convert a Fox ESS historical power response into normalised PowerSnapshot rows.

    Fox ESS returns channel-based time series. This parser pivots those channels
    into timestamp-level snapshots.

    Fox values are already reported in kW.
    """

    rows: Dict[str, dict] = defaultdict(dict)

    

    for result_item in raw_data.get("result", []):
        for channel in result_item.get("datas", []):
            
            variable = channel.get("variable")
            if variable not in FOX_CHANNEL_MAPPING:
                continue
            
            target_field = FOX_CHANNEL_MAPPING[variable]
            
            for datapoint in channel.get("data", []):
                timestamp = datapoint.get("time")
                if timestamp is None:
                    continue
                rows[timestamp][target_field] = float(datapoint.get("value", 0.0))

    snapshots: List[PowerSnapshot] = []

    for timestamp_str, values in rows.items():
        battery_charge_kw = values.get("battery_charge_kw", 0.0)
        battery_discharge_kw = values.get("battery_discharge_kw", 0.0)

        grid_import_kw = values.get("grid_import_kw", 0.0)
        grid_export_kw = values.get("grid_export_kw", 0.0)

        snapshots.append(
            PowerSnapshot(
                vendor="foxess",
                query_date=query_date,
                device_id=device_id,
                timestamp=_parse_foxess_timestamp(timestamp_str),
                load_kw=values.get("load_kw", 0.0),
                solar_pv_kw=values.get("solar_pv_kw", 0.0),
                battery_kw=battery_charge_kw - battery_discharge_kw,
                grid_kw=grid_import_kw - grid_export_kw,
            )
        )

    return sorted(snapshots, key=lambda snapshot: snapshot.timestamp)


def _parse_foxess_timestamp(timestamp: str) -> datetime:
    """
    Parse Fox ESS timestamp strings.

    Example:
        2025-10-02 01:04:37 BST+0100
    """

    cleaned = timestamp.replace(" BST", "")

    try:
        return datetime.strptime(cleaned, "%Y-%m-%d %H:%M:%S%z")
    except ValueError:
        return datetime.fromisoformat(timestamp.replace(" ", "T"))