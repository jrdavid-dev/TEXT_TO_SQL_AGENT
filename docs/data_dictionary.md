# Data Dictionary — DPWH / PhilGEPS Database

This document exists to capture everything about this database that isn't
obvious from `schema.sql` alone — data quirks, join behavior, and business
logic discovered during cleaning and query validation. It's written to be
used as context for a text-to-SQL agent, so anything that could cause a
correctly-written query to return a *misleading* answer belongs here.

## Tables and Columns

### PhilGEPS dimension tables
Four independent lookup tables, each with its own UUID `id`, joined to
`philgeps` **by name** (not by id) via `UNIQUE TEXT` columns.

**`awardees`** — one row per distinct awardee (contractor/supplier, PhilGEPS side)
- `id` — UUID, internal primary key (not used for joins)
- `awardee_name` — UNIQUE, TEXT, lowercased. This is the join key to `philgeps.awardee_name`
- `count` — number of awards aggregated into this row
- `total` — total award value aggregated into this row
- `start_date` / `end_date` — date range spanned by the aggregated awards

**`organizations`** — one row per distinct procuring organization
- Same shape as `awardees`, joined via `organization_name`
- **Note:** rows with duplicate names across two separate source batches were merged during cleaning (counts/totals summed, dates spanned, `id` regenerated) — see Known Data Quirks

**`area_of_deliveries`** — one row per distinct delivery location, joined via `area_of_delivery`

**`business_categories`** — one row per distinct procurement category, joined via `business_category`

### PhilGEPS fact table

**`philgeps`** — one row per procurement award
- `id` — UUID primary key
- `reference_id` — PhilGEPS reference number
- `contract_no` — contract identifier as recorded by PhilGEPS (bridge key to DPWH — see Join Notes)
- `award_title` — title of the awarded contract; often contains the DPWH `contract_id` as its first word
- `notice_title` — title of the original bid notice
- `awardee_name`, `organization_name`, `area_of_delivery`, `business_category` — FKs to the four dimension tables above, by name
- `contract_amount` — the **winning bid amount** (see Business Logic Notes — this is not the same thing as `budget`)
- `award_date` — date the contract was awarded
- `award_status` — status of the award

### DPWH Transparency

**`dpwh_transparency_data`** — one row per DPWH infrastructure contract (root table of the DPWH side)
- `contract_id` — TEXT primary key. This is the bridge key to PhilGEPS (see Join Notes)
- `description` — free-text project description
- `category` — project category (single-value; not to be confused with `component_category_table`, which is multi-value)
- `status` — contract status (e.g. completed, terminated, ongoing — confirm exact spelling via `SELECT DISTINCT status`)
- `budget` — the **Approved Budget for the Contract (ABC)** — the government's pre-bidding ceiling (see Business Logic Notes)
- `amount_paid` — intended to track cash disbursed to date. **Currently all zero across the entire dataset — see Known Data Quirks**
- `progress` — percentage physical completion
- `contractor` — contractor name; **may contain multiple names separated by `/` for joint ventures** (see Known Data Quirks)
- `start_date` — when work began
- `completion_date` — **only populated when `status` is `completed` or `terminated`** (see Known Data Quirks) — this is an actual/realized date, not a planned/target date
- `infra_year` — year the infrastructure work is attributed to
- `program_name` — high-level program grouping (low cardinality — only 2 distinct values observed: inside/outside infra)
- `source_of_funds` — funding source
- `is_live`, `livestream_url`, `livestream_video_id`, `livestream_detected_at` — livestream monitoring fields; **sparse, true for only a small subset of contracts** (see Known Data Quirks)
- `latitude`, `longitude` — project coordinates
- `report_count` — count of public reports/feedback submitted on this contract; **low across the board, not just zero-vs-nonzero but genuinely low even at its max** (see Known Data Quirks)
- `has_satellite_image` — boolean; **sparse, same caveat as `is_live`**
- `province`, `region` — location, flattened from a nested `location` field during cleaning

**`component_category_table`** — junction table, one row per `(contract_id, component_category)` pair
- Explodes the original multi-value `component_categories` column (e.g. `"Bridges, Roads"`) into one row per category
- Composite PK `(contract_id, component_category)`, FK to `dpwh_transparency_data`
- **Note:** a single contract's `budget` is associated with *every* category it belongs to — summing `budget` grouped by category will overcount relative to the true grand total (see Known Data Quirks)

### Flood Control

**`flood_control`** — one row per flood-control project **component** (PK: `global_id`)
- `global_id` — UUID primary key
- `object_id` — source system object id
- `infra_year` — year attribution
- `region`, `province`, `municipality` — location
- `implementing_office` — DPWH office responsible
- `project_id`, `project_description` — parent project identifiers
- `project_component_id`, `project_component_description` — this specific component
- `program` — funding/program grouping
- `type_of_work`, `infra_type` — classification of the work
- `longitude`, `latitude` — coordinates
- `contract_id` — **FK to `dpwh_transparency_data.contract_id`, many-to-one** (see Known Data Quirks — one contract can have multiple `flood_control` rows)
- `abc` — Approved Budget for the Contract, **at the component level** — relationship to `dpwh_transparency_data.budget` (contract level) is unconfirmed (see Known Data Quirks)
- `contract_cost` — actual contract cost for this component
- `completion_date_original` — **planned/target completion date**
- `completion_date_actual` — **actual completion date**. Unlike `dpwh_transparency_data`, this table has both a planned and actual date, so real delay (`completion_date_actual - completion_date_original`, or `CURRENT_DATE - completion_date_original` for still-open components) can be computed here
- `completion_year` — year of completion
- `contractor` — contractor name; same JV `/`-separator caveat as `dpwh_transparency_data.contractor`
- `creation_date`, `creator`, `edit_date`, `editor` — record metadata (source system audit fields)
- `funding_year` — year funding was allocated
- `legislative_district`, `district_engineering_office` — administrative location detail not present in `dpwh_transparency_data`
- `start_date` — when work began

## Known Data Quirks

- **All text columns are normalized to lowercase** during cleaning (`awardee_name`, `organization_name`, `area_of_delivery`, `business_category`, `status`, `category`, `contractor`, `program_name`, `source_of_funds`, `province`, `region`, etc.). String filters must use lowercase values, or `ILIKE` if unsure — a filter like `WHERE status = 'Completed'` will silently return zero rows, not an error.
- **`amount_paid` is zero for every row** in `dpwh_transparency_data`. No query should attempt to use this column for disbursement, overpayment, or payment-gap analysis — it carries no signal in the current dataset.
- **`completion_date` is only populated for `status IN ('completed', 'terminated')`.** For any other status, it's `NULL`. This means `completion_date < CURRENT_DATE` cannot be used to detect delay in ongoing contracts — the comparison silently evaluates to `NULL` (excluding the row) rather than `TRUE`, since there is no target/expected completion date recorded for open contracts.
- **Contractor names may represent joint ventures**, formatted as multiple contractor names separated by `/` (e.g. `"Contractor 1 / Contractor 2"`). A plain `GROUP BY contractor` treats each JV combination as its own distinct entity, separate from the same contractors appearing solo elsewhere — this understates each individual contractor's true totals. Splitting requires `unnest(string_to_array(contractor, '/'))`, with `TRIM()` applied to each resulting value (there are leading/trailing spaces around the `/`).
- **`is_live`, `livestream_url`, `livestream_video_id`, `livestream_detected_at`, and `has_satellite_image` are sparse** — only roughly 100 rows (out of ~248,000) have `is_live = true` or `has_satellite_image = true`. These columns cannot support "top N contractors by X" ranking questions, since nearly every contractor would tie at zero. They may still support "profile of the small verified/live subset" questions.
- **`report_count` is low across the board**, not just mostly-zero — even its observed maximum is small relative to the dataset size. It cannot meaningfully support ranking questions either, though a flat statistic ("% of contracts with `report_count = 0`") is still valid.
- **The DPWH ↔ PhilGEPS contract-id bridge is not 1:1 or fully exact.** Not every `dpwh_transparency_data.contract_id` has a matching `philgeps.contract_no`. The real match is tiered: (1) exact match on `contract_no`, (2) dash-stripped `contract_no` (PhilGEPS sometimes formats ids with dashes, e.g. `"25IJ-0021"` vs DPWH's `"25IJ0021"`), (3) leading token of `philgeps.award_title`, dash-stripped (the DPWH `contract_id` often appears as the first word of the award title). Combined, these three tiers cover roughly 90% of DPWH contracts — see README for exact figures. A plain `=` join on `contract_no` alone will therefore miss a meaningful share of otherwise-matchable rows.
- **`organizations` had duplicate-name rows merged during cleaning.** Some raw rows shared the same `organization_name` across two separate aggregate batches (a legacy import and an ongoing one) with different original ids. These were collapsed into one row per name (counts/totals summed, `start_date`/`end_date` spanned to the min/max, `id` regenerated) to satisfy the `UNIQUE` constraint needed for `philgeps`'s FK. `awardees`, `area_of_deliveries`, and `business_categories` were **not** merged this way — only `organizations` went through this step.
- **A `dpwh_transparency_data` contract can have multiple `flood_control` rows** (one contract, many components — many-to-one from `flood_control` to `dpwh_transparency_data`). Joining the two tables and summing a `dpwh_transparency_data` column (like `budget`) without aggregating first will duplicate that value once per matching `flood_control` row.
- **The relationship between `flood_control.abc` (component-level) and `dpwh_transparency_data.budget` (contract-level) has not been verified.** It's hypothesized that summing a contract's `flood_control.abc` values should reconcile to that contract's `dpwh_transparency_data.budget`, but this has not been confirmed with a query. Treat any comparison between these two columns as unverified until checked.
- **`program_name` has only 2 distinct values** (inside/outside infra) — too low-cardinality to support a "top 10 program_names" style ranking question.

## Join Notes

- **PhilGEPS's four dimension tables join to `philgeps` by name, not by id** — `awardee_name`, `organization_name`, `area_of_delivery`, `business_category` are `UNIQUE TEXT` columns referenced by `philgeps`'s foreign keys. This is atypical; don't assume an `id`-based join here.
- **`dpwh_transparency_data.contract_id` ↔ `philgeps.contract_no`** is the primary DPWH-world ↔ PhilGEPS-world bridge, and it is tiered/imperfect — see Known Data Quirks above for the three-tier match logic and its ~90% combined coverage.
- **`dpwh_transparency_data.contract_id` ↔ `flood_control.contract_id`** is one-to-many (one DPWH contract → many flood control component rows). Use `INNER JOIN` when you only want DPWH contracts that have flood-control detail; use `LEFT JOIN` with a `WHERE ... IS NULL` check specifically when you want to find DPWH contracts that have *no* flood-control component.
- **`dpwh_transparency_data.contract_id` ↔ `component_category_table.contract_id`** is also one-to-many (one contract can belong to multiple categories). Same INNER/LEFT JOIN guidance applies. A contract's `budget` will be counted once per associated category if you group by category and sum budget — this is expected but should be described as "budget associated with category," not "budget attributable only to that category."

## Business Logic Notes

- **Procurement sequence, in order:**
  1. The government sets the **Approved Budget for the Contract (ABC)** before bidding opens — this is `budget` in `dpwh_transparency_data` and `abc` in `flood_control`. It is a ceiling, not a target.
  2. Contractors submit bids. Any bid above the ABC is automatically disqualified.
  3. The lowest bid that also meets technical/eligibility requirements ("Lowest Calculated Responsive Bid") wins. This winning bid becomes `philgeps.contract_amount`.
  4. Therefore **`contract_amount` should be ≤ `budget`** (the ABC) as a rule — this can be checked as a data-quality/anomaly test across the bridged tables; violations are worth flagging, not silently accepting.
  5. Execution and payment happen after award, tracked in `dpwh_transparency_data` via `progress`, `status`, and (intended to be) `amount_paid`. Payments are normally disbursed incrementally against progress milestones, not paid in full upfront — so even a fully-paid completed contract would not necessarily show `amount_paid = contract_amount` exactly (deductions like withholding tax and retention money are typical). This project's `amount_paid` column does not currently carry this signal at all (see Known Data Quirks).
- **A `status = 'completed'` contract with `progress < 100` is a data-integrity/reporting red flag** — status and progress should agree once a project is genuinely finished. This pattern has been confirmed to occur in the real data.
- **"Delay" cannot currently be measured for ongoing `dpwh_transparency_data` contracts**, because there is no expected/target completion date recorded for open work (`completion_date` is only set once a contract reaches `completed`/`terminated`). Any "is this contract behind schedule" question for ongoing DPWH contracts should be treated as unanswerable with the current schema — reframe as a progress-level snapshot instead of a date-based delay claim. `flood_control.completion_date_original` vs `completion_date_actual` is the one place in this schema where genuine delay *can* be computed, since it has both a planned and an actual date.
