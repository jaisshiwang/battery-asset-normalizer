from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass(frozen=True)
class PowerSnapshot:
    """
    Silver layer representation.

    A normalised power reading at a specific timestamp.
    All power values are stored in kW.
    """

    vendor: str
    query_date: date
    timestamp: datetime

    load_kw: float
    solar_pv_kw: float
    battery_kw: float
    grid_kw: float

    device_id: Optional[str] = None


@dataclass(frozen=True)
class EnergyInterval:
    """
    Gold layer representation.

    Energy aggregated over a fixed interval.
    All energy values are stored in kWh.
    """

    vendor: str
    query_date: date

    period_start: datetime
    period_end: datetime

    load_kwh: float
    solar_pv_kwh: float
    battery_kwh: float
    grid_kwh: float

    device_id: Optional[str] = None