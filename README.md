# Text-to-SQL Agent — Philippine Government Procurement & Infrastructure Data

## Data Sources

This project uses publicly available Philippine government data on infrastructure contracts and procurement. Raw data files are **not included in this repository** — see below for how to obtain them.

### DPWH Infrastructure Transparency Data
- **Source:** [BetterGov.ph Open Data Portal](https://data.bettergov.ph)
- **File:** `dpwh_transparency_data.parquet`
- **Description:** Contract-level infrastructure project data from the Department of Public Works and Highways — budgets, contractors, status, location, and progress across ~248,000 contracts.

### Flood Control Projects (Esri GeoJSON export)
- **Source:** [BetterGov.ph — Flood Control Projects Dashboard](https://data.bettergov.ph)
- **File:** `flood_control.json`
- **Description:** Geospatial subset of DPWH flood control infrastructure projects, including coordinates and legislative district data not present in the main transparency dataset.

### PhilGEPS Procurement Data
- **Source:** [Open PhilGEPS Data, BetterGov.ph](https://data.bettergov.ph) / [PhilGEPS](https://www.philgeps.gov.ph)
- **Files:** `philgeps.parquet` (fact table), `awardees.parquet`, `organizations.parquet`, `business_categories.parquet`, `area_of_deliveries.parquet` (dimension tables)
- **Description:** Government procurement award records — contracts, awardees, procuring organizations, business categories, and delivery locations.

## Getting the Data

1. Download the source files from the links above.
2. Place them in a `docs/` folder in the project root.
3. This folder is excluded from version control via `.gitignore` — raw data files are not tracked in this repository due to their size.

## Running the Preprocessing Script

```bash
python data_preprocessing.py
```

This cleans and normalizes the raw files (type conversions, date parsing, UUID decoding, and schema normalization) in preparation for loading into a SQL database.