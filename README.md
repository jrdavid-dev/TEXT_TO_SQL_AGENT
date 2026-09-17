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

This cleans and normalizes the raw files (type conversions, date parsing, UUID decoding, duplicate-name merging, and schema normalization) in preparation for loading into a SQL database. Cleaned output is written to `clean/*.parquet`.

## Data Architecture

The data forms two independently clean "islands," connected by two different kinds of bridges.

### DPWH-world
- **`dpwh_transparency_data`** (PK: `contract_id`) — the root table of infrastructure contracts.
- **`flood_control`** (PK: `global_id`) — a geospatial subset of DPWH's flood control projects. `contract_id` here is a foreign key back to `dpwh_transparency_data` — **many-to-one**, since one contract can have multiple flood control component rows, each with its own `object_id`/`global_id`.
- **`component_category_table`** — a junction table exploding DPWH's multi-value `component_categories` column (e.g. `"Bridges, Roads"`) into one row per `(contract_id, component_category)` pair. Composite primary key, FK back to `dpwh_transparency_data`.

### PhilGEPS-world
- **`philgeps`** (PK: `id`) — the procurement award fact table.
- **Four dimension tables** — `awardees`, `organizations`, `area_of_deliveries`, `business_categories` — each with its own independent UUID `id`, joined to `philgeps` **by name**, not by id (`awardee_name`, `organization_name`, etc. are `UNIQUE TEXT` columns referenced by `philgeps`'s FKs).
- Some raw dimension-table rows shared the same name across two separate aggregate batches (a legacy import and an ongoing one) with different `id`s — these were merged (summed counts/totals, spanned start/end dates, regenerated `id`) during cleaning to satisfy the `UNIQUE` constraint needed for the FK.

### Bridging the two islands

**Primary bridge — contract identifiers (mostly exact, ~90% coverage).** Checked via a tiered match:
1. Exact match: `philgeps.contract_no` = `dpwh_transparency_data.contract_id` — 82.75% of DPWH's 248,220 contracts.
2. Dash-stripped `contract_no` (e.g. PhilGEPS's `"25IJ-0021"` vs DPWH's `"25IJ0021"`) — +1.07%, cumulative 83.82%.
3. Leading token of `philgeps.award_title`, dash-stripped (the DPWH contract_id often appears as the first word of the award title) — +6.42%, **cumulative 90.24%**.

24,234 DPWH contracts (9.76%) remain unmatched by any of these methods — not yet confirmed why (leading hypothesis: no corresponding PhilGEPS award exists yet for these contracts).

**Fallback bridge — fuzzy contractor/awardee name matching.** For the entity-resolution challenge this project is built around: `dpwh_transparency_data.contractor` / `flood_control.contractor` ≈ `philgeps.awardee_name` is *not* a clean join — DPWH names carry messy suffixes (e.g. `"C'ZARLES CONSTRUCTION & SUPPLY (23426)"`) that PhilGEPS's cleaner `"ALLEN TRADING"`-style names don't have. This requires actual fuzzy matching (rapidfuzz or Postgres's `pg_trgm`), not exact `=`, and — per the ID-bridge findings above — is now scoped to just the ~24,234 contracts the ID-based bridge doesn't resolve, rather than the whole dataset. **Not yet built.**

## Database Setup

Schema DDL lives in `schema.sql` (PostgreSQL). Table creation order matters — parent tables (PhilGEPS's four dimension tables, `dpwh_transparency_data`) are created before the tables that reference them (`philgeps`, `flood_control`, `component_category_table`).

To create the schema and load cleaned data:

```bash
python setup_database.py
```

This requires the following environment variables to be set (e.g. via a `.env` file, not committed to version control):

```
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=...
DB_NAME=...
```

`setup_database.py` runs `schema.sql` against the target database, then loads each `clean/*.parquet` file into its matching table via `pandas.DataFrame.to_sql()`.

## What's Left

- Build the fuzzy contractor ↔ awardee_name crosswalk for the ~24,234 contracts the ID-based bridge doesn't resolve.
- Investigate why those contracts don't match (check `status`).
- Write 15–20 hand-written SQL queries as a validation/test set.
- Build the text-to-SQL agent, add guardrails (read-only enforcement, SQL validation, retry loop), and evaluate against the test set.
- Accuracy numbers and setup instructions to be added here once the agent is evaluated.
- Small demo interface (Streamlit/CLI).