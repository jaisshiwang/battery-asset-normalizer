from datetime import date
from typing import Any, Dict, List, Optional

from battery_asset_normalizer.models import PowerSnapshot
from battery_asset_normalizer.parsers.foxess import parse_foxess
from battery_asset_normalizer.parsers.growatt import parse_growatt
from battery_asset_normalizer.storage import LocalDatasetStore


SUPPORTED_VENDORS = {"foxess", "growatt"}


def create_silver_snapshots(
    vendor: str,
    raw_data: Dict[str, Any],
    query_date: date,
    device_info: Optional[Dict[str, Any]] = None,
    api_token: Optional[str] = None,
    persist: bool = False,
    store: Optional[LocalDatasetStore] = None,
) -> List[PowerSnapshot]:
    """
    Create the Silver layer PowerSnapshot dataset from raw vendor data.

    Args:
        vendor: Battery manufacturer name. Supported values: foxess, growatt.
        raw_data: Raw vendor API response payload.
        query_date: Date being queried.
        device_info: Device metadata required for the vendor API.
        api_token: User API token. Included to match the required interface.
        persist: If True, writes the Silver dataset to local storage.
        store: Optional dataset store, useful for testing.

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
        snapshots = parse_foxess(
            raw_data=raw_data,
            query_date=query_date,
            device_id=device_id,
        )

    elif normalised_vendor == "growatt":
        snapshots = parse_growatt(
            raw_data=raw_data,
            query_date=query_date,
            device_id=device_id,
        )

    else:
        raise ValueError(f"Unsupported vendor '{vendor}'")

    if persist:
        dataset_store = store or LocalDatasetStore()
        dataset_store.write_silver(snapshots)

    return snapshots