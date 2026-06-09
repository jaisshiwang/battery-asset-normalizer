# Battery Asset Normalizer

A lightweight Python package for normalising battery telemetry from different manufacturers into a common power and energy model.

This package exposes a vendor-independent public interface through `run_pipeline()`, allowing callers to retrieve normalised energy intervals without needing to understand vendor-specific payload structures.

The package currently supports:

- Fox ESS
- Growatt SPH devices

It converts vendor-specific power snapshot data into:

1. A unified Silver `PowerSnapshot` dataset.
2. A Gold `EnergyInterval` dataset containing estimated kWh values for clock-aligned periods.

---

## Problem

Battery manufacturers expose different APIs and data schemas.

Fox ESS and Growatt both provide power-flow snapshots, but:

- Their JSON structures are different.
- Their field names are different.
- Their units are different.
- Their snapshots arrive at irregular intervals.

This package hides those vendor differences behind a common interface.

---

## Architecture

The project follows a lightweight medallion-inspired flow:

```text
Bronze
Raw vendor JSON payloads
        ↓
Parsers
Vendor-specific mapping logic
        ↓
Silver
Normalised PowerSnapshot records in kW
        ↓
Resampling
Irregular power snapshots converted into fixed intervals
        ↓
Gold
EnergyInterval records in kWh
```

---

## Data Layers

### Bronze

Raw vendor API responses.

For this exercise, the HTTP/API layer is mocked using the supplied JSON files in `tests/fixtures`.

### Silver

A unified power snapshot dataset.

Output file:

```text
data/silver/power_snapshots.csv
```

Schema:

| Column | Description |
|---|---|
| vendor | Vendor name |
| query_date | Date requested |
| timestamp | Snapshot timestamp |
| load_kw | Load power in kW |
| solar_pv_kw | Solar generation in kW |
| battery_kw | Positive = charging, negative = discharging |
| grid_kw | Positive = importing, negative = exporting |
| device_id | Optional device or asset identifier |

### Gold

A unified energy interval dataset.

Output file:

```text
data/gold/energy_intervals.csv
```

Schema:

| Column | Description |
|---|---|
| vendor | Vendor name |
| query_date | Date requested |
| period_start | Interval start |
| period_end | Interval end |
| load_kwh | Load energy in kWh |
| solar_pv_kwh | Solar energy in kWh |
| battery_kwh | Positive = charged energy, negative = discharged energy |
| grid_kwh | Positive = imported energy, negative = exported energy |
| device_id | Optional device or asset identifier |

---

## Vendor Mappings

### Fox ESS

Fox ESS returns channel-based time series.

Mappings:

```text
load_kw      = loadsPower
solar_pv_kw  = pvPower
battery_kw   = batChargePower - batDischargePower
grid_kw      = gridConsumptionPower - feedinPower
```

Fox ESS values are already reported in kW.

### Growatt SPH

Growatt returns row-based snapshots.

Mappings:

```text
load_kw      = plocalLoadTotal / 1000
solar_pv_kw  = ppv / 1000
battery_kw   = (pcharge1 - pdischarge1) / 1000
grid_kw      = (pacToUserTotal - pacToGridTotal) / 1000
```

Growatt values are converted from W to kW.

---

## Power to Energy Conversion

Power is converted to energy using:

```text
Energy (kWh) = Power (kW) × Duration (hours)
```

The resampling engine assumes each power snapshot is valid until the next timestamp.

The final snapshot is not extrapolated because there is no following reading to define its duration.

---

## Installation

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the package:

```bash
pip install -e ".[dev]"
```

## Verify Installation

```bash
python -c "from battery_asset_normalizer import run_pipeline; print('ok')"
```

---

## Running Tests

```bash
pytest
```

---

## Public API

```python
from datetime import date

from battery_asset_normalizer import run_pipeline

intervals = run_pipeline(
    vendor="growatt",
    query_date=date(2025, 9, 23),
    device_info={},
    api_token="mock-token",
)

print(len(intervals))
```

---

## Generate Silver Dataset

```bash
python scripts/run_silver.py
```

This writes:

```text
data/silver/power_snapshots.csv
```

---

## Generate Silver and Gold Datasets

```bash
python scripts/run_gold.py
```

This writes:

```text
data/silver/power_snapshots.csv
data/gold/energy_intervals.csv
```

---

## Bonus: 5-Minute Resampling

```python
from datetime import date

from battery_asset_normalizer import run_pipeline

intervals = run_pipeline(
    vendor="foxess",
    query_date=date(2025, 10, 2),
    device_info={"device_id": "foxess-sample-device"},
    api_token="mock-token",
    interval_minutes=5,
)
```

---

## Example Usage

```python
from datetime import date

from battery_asset_normalizer import run_pipeline

intervals = run_pipeline(
    vendor="foxess",
    query_date=date(2025, 10, 2),
    device_info={"device_id": "foxess-sample-device"},
    api_token="mock-token",
)

print(intervals[0])
```

---

## Assumptions

- Fox ESS values are already in kW.
- Growatt SPH values are in W and are converted to kW.
- Battery values are positive when charging and negative when discharging.
- Grid values are positive when importing and negative when exporting.
- Snapshot values are treated as step functions.
- No energy is inferred before the first snapshot.
- The final snapshot is not extrapolated.
- CSV is used to keep the package lightweight and dependency-free.

---

## Assessment Coverage

- **Abstraction and extensibility:** Vendor-specific logic is isolated in `parsers/`. New vendors can be added by implementing a new parser that returns `PowerSnapshot` records.
- **Power-to-energy correctness:** Irregular snapshots are treated as step functions and converted using `kWh = kW × hours`. Partial overlaps across 30-minute buckets are prorated.
- **Testing:** Tests cover vendor parsing, unit conversion, sign conventions, 30-minute and 5-minute resampling, final snapshot handling, storage, and end-to-end flow.
- **Developer experience:** The package can be installed with `pip install -e ".[dev]"`, tested with `pytest`, and run through `run_pipeline()` or the scripts.

---
## Future Enhancements

- Add live API-backed clients.
- Add validation for missing or inconsistent vendor fields.
- Add Parquet or Delta persistence for production-scale use.
- Add additional vendors.
- Add richer data quality reporting.