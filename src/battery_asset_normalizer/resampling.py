from datetime import date, datetime, time, timedelta
from typing import Dict, List, Tuple

from battery_asset_normalizer.models import EnergyInterval, PowerSnapshot


EnergyBucket = Dict[str, float]
BucketKey = Tuple[datetime, datetime]


def resample_to_energy_intervals(
    snapshots: List[PowerSnapshot],
    query_date: date,
    interval_minutes: int = 30,
) -> List[EnergyInterval]:
    """
    Convert irregular PowerSnapshot records into clock-aligned EnergyInterval rows.

    Assumption:
        Each snapshot value is valid until the next timestamp.
        The final snapshot is not extrapolated.
    """

    if not snapshots:
        return []

    if interval_minutes <= 0:
        raise ValueError("interval_minutes must be greater than zero")

    ordered_snapshots = sorted(snapshots, key=lambda snapshot: snapshot.timestamp)

    vendor = ordered_snapshots[0].vendor
    device_id = ordered_snapshots[0].device_id

    day_start = datetime.combine(query_date, time.min)
    day_end = day_start + timedelta(days=1)

    buckets = _create_empty_buckets(
        start=day_start,
        end=day_end,
        interval_minutes=interval_minutes,
    )

    for current_snapshot, next_snapshot in zip(
        ordered_snapshots,
        ordered_snapshots[1:],
    ):
        segment_start = max(
            _remove_timezone(current_snapshot.timestamp),
            day_start,
        )
        segment_end = min(
            _remove_timezone(next_snapshot.timestamp),
            day_end,
        )

        if segment_end <= segment_start:
            continue

        _add_snapshot_energy_to_buckets(
            buckets=buckets,
            snapshot=current_snapshot,
            segment_start=segment_start,
            segment_end=segment_end,
            interval_minutes=interval_minutes,
        )

    return [
        EnergyInterval(
            vendor=vendor,
            query_date=query_date,
            device_id=device_id,
            period_start=period_start,
            period_end=period_end,
            load_kwh=round(values["load_kwh"], 6),
            solar_pv_kwh=round(values["solar_pv_kwh"], 6),
            battery_kwh=round(values["battery_kwh"], 6),
            grid_kwh=round(values["grid_kwh"], 6),
        )
        for (period_start, period_end), values in buckets.items()
    ]


def _create_empty_buckets(
    start: datetime,
    end: datetime,
    interval_minutes: int,
) -> Dict[BucketKey, EnergyBucket]:
    buckets: Dict[BucketKey, EnergyBucket] = {}

    current = start

    while current < end:
        period_end = current + timedelta(minutes=interval_minutes)

        buckets[(current, period_end)] = {
            "load_kwh": 0.0,
            "solar_pv_kwh": 0.0,
            "battery_kwh": 0.0,
            "grid_kwh": 0.0,
        }

        current = period_end

    return buckets


def _add_snapshot_energy_to_buckets(
    buckets: Dict[BucketKey, EnergyBucket],
    snapshot: PowerSnapshot,
    segment_start: datetime,
    segment_end: datetime,
    interval_minutes: int,
) -> None:
    current = segment_start

    while current < segment_end:
        bucket_start = _floor_to_interval(current, interval_minutes)
        bucket_end = bucket_start + timedelta(minutes=interval_minutes)

        overlap_end = min(bucket_end, segment_end)
        duration_hours = (overlap_end - current).total_seconds() / 3600

        bucket = buckets.get((bucket_start, bucket_end))

        if bucket is not None:
            bucket["load_kwh"] += snapshot.load_kw * duration_hours
            bucket["solar_pv_kwh"] += snapshot.solar_pv_kw * duration_hours
            bucket["battery_kwh"] += snapshot.battery_kw * duration_hours
            bucket["grid_kwh"] += snapshot.grid_kw * duration_hours

        current = overlap_end


def _floor_to_interval(timestamp: datetime, interval_minutes: int) -> datetime:
    floored_minute = (timestamp.minute // interval_minutes) * interval_minutes

    return timestamp.replace(
        minute=floored_minute,
        second=0,
        microsecond=0,
    )


def _remove_timezone(timestamp: datetime) -> datetime:
    return timestamp.replace(tzinfo=None)