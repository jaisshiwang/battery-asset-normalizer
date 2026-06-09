import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional
from battery_asset_normalizer.models import EnergyInterval, PowerSnapshot
from battery_asset_normalizer.parsers.foxess import parse_foxess
from battery_asset_normalizer.parsers.growatt import parse_growatt
from battery_asset_normalizer.resampling import resample_to_energy_intervals

SUPPORTED_VENDORS = {"foxess", "growatt"}

FIXTURE_PATHS = {
    "foxess": Path("tests/fixtures/fox-history-query-v2.json"),
    "growatt": Path("tests/fixtures/growat-queryhistoricaldata.json"),
}


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

def run_pipeline(
    vendor: str,
    query_date: date,
    device_info: Optional[Dict[str, Any]] = None,
    api_token: Optional[str] = None,
    interval_minutes: int = 30,
    raw_data: Optional[Dict[str, Any]] = None,

) -> List[EnergyInterval]:

    """
    Public package interface.
    Accepts the same vendor-independent inputs for Fox ESS and Growatt:
    - query date
    - device information
    - API token
    For this exercise, raw_data can be supplied directly or loaded from
    fixture files that mock the vendor HTTP responses.
    """

    normalised_vendor = vendor.lower()

    if raw_data is None:
        raw_data = load_mock_api_response(normalised_vendor)

    snapshots = create_silver_snapshots(
        vendor=normalised_vendor,
        raw_data=raw_data,
        query_date=query_date,
        device_info=device_info,
        api_token=api_token,
    )
    return resample_to_energy_intervals(
        snapshots=snapshots,
        query_date=query_date,
        interval_minutes=interval_minutes,
    )

def load_mock_api_response(vendor: str) -> Dict[str, Any]:
    normalised_vendor = vendor.lower()
    if normalised_vendor not in FIXTURE_PATHS:
        raise ValueError(
            f"Unsupported vendor '{vendor}'. "
            f"Supported vendors are: {sorted(FIXTURE_PATHS)}"
        )

    fixture_path = FIXTURE_PATHS[normalised_vendor]
    with fixture_path.open() as file:
        return json.load(file)