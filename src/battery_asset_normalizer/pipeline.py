from datetime import date
from typing import Any, Dict, List, Optional

from battery_asset_normalizer.models import PowerSnapshot
from battery_asset_normalizer.parsers.foxess import parse_foxess
from battery_asset_normalizer.parsers.growatt import parse_growatt


SUPPORTED_VENDORS = {"foxess", "growatt"}


def create_silver_snapshots(
    vendor: str,
    raw_data: Dict[str, Any],
    query_date: date,
    device_info: Optional[Dict[str, Any]] = None,
    api_token: Optional[str] = None,
) -> List[PowerSnapshot]:
    """
    Create the Silver layer PowerSnapshot dataset from raw vendor data.

    Args:
        vendor: Battery manufacturer name. Supported values: foxess, growatt.
        raw_data: Raw vendor API response payload.
        query_date: Date being queried.
        device_info: Device metadata required for the vendor API.
        api_token: User API token. Included to match the required interface.

    Returns:
        A list of normalised PowerSnapshot records.
    """
    
    normalised_vendor = vendor.lower()

    if normalised_vendor not in SUPPORTED_VENDORS:
        raise ValueError(
            f"Unsupported vendor '{vendor}'. "
            f"Supported vendors are: {sorted(SUPPORTED_VENDORS)}"
        )

    device_info = device_info or {}
    device_id = device_info.get("device_id")

    if normalised_vendor == "foxess":
        return parse_foxess(raw_data, query_date, device_id)

    if normalised_vendor == "growatt":
        return parse_growatt(raw_data, query_date, device_id)

    raise ValueError(f"Unsupported vendor '{vendor}'")