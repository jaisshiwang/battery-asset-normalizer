# Battery Asset Normalizer

A vendor-agnostic Python package for normalising battery telemetry from multiple manufacturers into a common energy model.

The package currently supports:

- Fox ESS
- Growatt SPH devices

The goal is to provide a single, consistent interface for converting vendor-specific power telemetry into standardised energy datasets suitable for optimisation, analytics and reporting.

---

## Problem Statement

Battery manufacturers expose different APIs and data schemas.

Fox ESS and Growatt both provide power flow snapshots, but:

- The payload structures are different.
- The naming conventions are different.
- The units are different.
- Snapshot timestamps occur at irregular intervals.

This package normalises vendor-specific payloads into a common schema and converts irregular power snapshots into clock-aligned energy intervals.

---

## Architecture

The solution follows a lightweight medallion-inspired architecture.

```text
FOX ESS JSON
      │
      ▼
GROWATT JSON
      │
      ▼
BRONZE
Raw Vendor Payloads
      │
      ▼
PARSERS
      │
      ▼
SILVER
PowerSnapshot Dataset
      │
      ▼
RESAMPLING ENGINE
      │
      ▼
GOLD
EnergyInterval Dataset
```

### Bronze Layer

Raw vendor API payloads.

For this exercise, API responses are mocked using the supplied JSON files.

Examples:

- Fox ESS historical power response
- Growatt SPH historical power response

### Silver Layer

Normalised power telemetry.

All vendor-specific fields are converted into a common schema:

| Column | Description |
|----------|----------|
| vendor | Manufacturer |
| query_date | Requested date |
| device_id | Device identifier |
| timestamp | Snapshot timestamp |
| load_kw | Site load power |
| solar_pv_kw | Solar generation power |
| battery_kw | Positive = charging, Negative = discharging |
| grid_kw | Positive = import, Negative = export |

### Gold Layer

Clock-aligned energy intervals.

Power snapshots are converted into estimated energy usage for fixed periods.

Default interval:

- 30 minutes

Output schema:

| Column | Description |
|----------|----------|
| vendor | Manufacturer |
| query_date | Requested date |
| device_id | Device identifier |
| period_start | Start of interval |
| period_end | End of interval |
| load_kwh | Load energy |
| solar_pv_kwh | Solar energy |
| battery_kwh | Battery energy |
| grid_kwh | Grid energy |

---

## Project Structure

```text
battery-asset-normalizer/
│
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── src/
│   └── battery_asset_normalizer/
│       ├── models.py
│       ├── pipeline.py
│       ├── storage.py
│       ├── resampling.py
│       │
│       └── parsers/
│           ├── foxess.py
│           └── growatt.py
│
├── tests/
│
├── README.md
└── pyproject.toml
```

---

## Vendor Mappings

### Fox ESS

The following fields are normalised:

```text
load_kw      = loadsPower
solar_pv_kw  = pvPower
battery_kw   = batChargePower - batDischargePower
grid_kw      = gridConsumptionPower - feedinPower
```

Fox ESS values are already provided in kW.

### Growatt SPH

The following fields are normalised:

```text
load_kw      = plocalLoadTotal
solar_pv_kw  = ppv
battery_kw   = pcharge1 - pdischarge1
grid_kw      = pacToUserTotal - pacToGridTotal
```

Growatt values are converted from W to kW during normalisation.

---

## Power to Energy Conversion

Power snapshots are recorded at irregular intervals.

Energy is calculated using:

```text
Energy (kWh) = Power (kW) × Time (hours)
```

The implementation assumes a step-function model where each power value applies until the next available snapshot.

Energy contributions are then prorated into fixed 30-minute intervals.

---

## Running the Project

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

---

## Assumptions

- Fox ESS values are reported in kW.
- Growatt SPH values are reported in W and converted to kW.
- Battery power is positive when charging and negative when discharging.
- Grid power is positive when importing and negative when exporting.
- Snapshot values are treated as step functions until the next reading.
- No energy is inferred before the first available snapshot.
- No energy is extrapolated beyond the final available snapshot.

---

## Future Enhancements

- Support additional battery vendors.
- Optional persistence to Parquet or Delta Lake.
- 5-minute interval resampling.
- API-backed ingestion clients.
- Data quality validation and anomaly detection.
- Forecast and optimisation integration.