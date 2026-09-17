import pandas as pd
import os
from data_preprocessing import (
    load_philgeps,
    load_awardees,
    load_organizations,
    load_area_of_deliveries,
    load_business_categories,
    load_dpwh_transparency_data,
    load_clean_flood_control,
)


# =========================================
# HELPERS
# =========================================
def print_section(title: str) -> None:
    """Print a labeled divider so check output is easy to scan."""
    print()
    print("=" * 50)
    print(title)
    print("=" * 50)


def strip_dashes(value) -> str | None:
    """Remove dashes from an id-like string for cross-system comparison."""
    if pd.isna(value):
        return None
    return str(value).replace("-", "")


def extract_first_word(title) -> str | None:
    """Grab the first whitespace-separated token of a title, dashes removed."""
    words = str(title).split()
    if not words:
        return None
    return words[0].replace("-", "")


# =========================================
# CHECKS
# =========================================
def check_match_rate(
    source_df: pd.DataFrame,
    source_col: str,
    target_df: pd.DataFrame,
    target_col: str,
    label: str,
) -> None:
    """Check what fraction of source_df's distinct values exist in target_df."""
    source_values = set(source_df[source_col].dropna())
    target_values = set(target_df[target_col].dropna())

    unmatched = source_values - target_values
    match_rate = 1 - (len(unmatched) / len(source_values))

    print_section(f"{label} match rate")
    print(f"Distinct source values: {len(source_values)}")
    print(f"Match rate:             {match_rate:.2%}")
    print(f"Unmatched count:        {len(unmatched)}")


def check_dpwh_philgeps_contract_bridge(
    df_philgeps: pd.DataFrame,
    df_dpwh: pd.DataFrame,
) -> set[str]:
    """
    Check the dpwh_transparency_data <-> philgeps contract-id bridge,
    tiered from strictest to loosest match method. Returns the combined
    set of matched DPWH contract_ids.
    """
    philgeps_contract_nos = set(df_philgeps["contract_no"].dropna())
    dpwh_contract_ids = set(df_dpwh["contract_id"].dropna())

    # Tier 1: exact match on contract_no
    matched_exact = dpwh_contract_ids & philgeps_contract_nos
    unmatched_after_exact = dpwh_contract_ids - philgeps_contract_nos

    print_section("STEP 1 — Match via contract_no (exact)")
    print(f"Total DPWH contracts:    {len(dpwh_contract_ids)}")
    print(f"Matched via contract_no: {len(matched_exact)}")
    print(f"Still unmatched:         {len(unmatched_after_exact)}")
    print(f"Match rate (of DPWH):    {len(matched_exact) / len(dpwh_contract_ids):.2%}")

    # Tier 2: dash-stripped contract_no
    philgeps_contract_nos_no_dash = set(
        df_philgeps["contract_no"].apply(strip_dashes)
    )
    matched_dash_removal = unmatched_after_exact & philgeps_contract_nos_no_dash
    unmatched_after_dash_removal = unmatched_after_exact - philgeps_contract_nos_no_dash

    print_section("STEP 2 — Match remaining gap via dash-stripped contract_no")
    print(f"Entering step 2:        {len(unmatched_after_exact)}")
    print(f"Additionally matched:   {len(matched_dash_removal)}")
    print(f"Still unmatched:        {len(unmatched_after_dash_removal)}")

    # Tier 3: leading token of award_title, dash-stripped
    df_philgeps["extracted_id"] = df_philgeps["award_title"].apply(extract_first_word)
    philgeps_ids_from_title = set(df_philgeps["extracted_id"].dropna())

    matched_title = unmatched_after_dash_removal & philgeps_ids_from_title
    still_unmatched = unmatched_after_dash_removal - philgeps_ids_from_title

    print_section("STEP 3 — Match remaining gap via award_title extraction")
    print(f"Entering step 3:        {len(unmatched_after_dash_removal)}")
    print(f"Additionally matched:   {len(matched_title)}")
    print(f"Still unmatched:        {len(still_unmatched)}")

    # Combined
    total_matched = matched_exact | matched_dash_removal | matched_title
    combined_match_rate = len(total_matched) / len(dpwh_contract_ids)

    print_section("COMBINED RESULTS — dpwh_transparency_data <-> philgeps")
    print(f"Total DPWH contracts:           {len(dpwh_contract_ids)}")
    print(f"  Matched via contract_no:      {len(matched_exact)}")
    print(f"  Matched via dash removal:     {len(matched_dash_removal)}")
    print(f"  Matched via title extraction: {len(matched_title)}")
    print(f"Total matched (combined):       {len(total_matched)}")
    print(f"Still unmatched:                {len(still_unmatched)}")
    print(f"Combined match rate (of DPWH):  {combined_match_rate:.2%}")

    print_section("SAMPLE — still unmatched after all three methods")
    for cid in list(still_unmatched)[:10]:
        print(f"  {cid!r}")

    print_section("SAMPLE — matched via dash-stripped contract_no")
    sample_dash = df_philgeps[
        df_philgeps["contract_no"].apply(strip_dashes).isin(matched_dash_removal)
    ][["contract_no", "award_title"]].head(10)
    print(sample_dash)

    print_section("SAMPLE — matched via award_title extraction")
    sample_title = df_philgeps[
        df_philgeps["extracted_id"].isin(matched_title)
    ][["award_title", "extracted_id"]].head(10)
    print(sample_title)

    return total_matched


def check_flood_control_bridge(df_dpwh: pd.DataFrame, df_flood_control: pd.DataFrame) -> None:
    """Check flood_control.contract_id against dpwh_transparency_data.contract_id."""
    check_match_rate(
        source_df=df_flood_control,
        source_col="contract_id",
        target_df=df_dpwh,
        target_col="contract_id",
        label="flood_control -> dpwh_transparency_data (contract_id)",
    )


# =========================================
# MAIN
# =========================================
def main():
    df_philgeps = load_philgeps("clean")
    df_awardees = load_awardees("clean")
    df_organizations = load_organizations("clean")
    df_area_of_deliveries = load_area_of_deliveries("clean")
    df_business_categories = load_business_categories("clean")
    df_dpwh_transparency_data = load_dpwh_transparency_data("clean")
    df_flood_control = load_clean_flood_control("clean")

    # PhilGEPS fact table <-> its 4 dimension tables (should be ~exact)
    check_match_rate(df_philgeps, "awardee_name", df_awardees, "awardee_name", "awardee_name")
    check_match_rate(df_philgeps, "organization_name", df_organizations, "organization_name", "organization_name")
    check_match_rate(df_philgeps, "area_of_delivery", df_area_of_deliveries, "area_of_delivery", "area_of_delivery")
    check_match_rate(df_philgeps, "business_category", df_business_categories, "business_category", "business_category")

    # DPWH-world internal bridge
    check_flood_control_bridge(df_dpwh_transparency_data, df_flood_control)

    # DPWH-world <-> PhilGEPS-world bridge (tiered contract-id match)
    check_dpwh_philgeps_contract_bridge(df_philgeps, df_dpwh_transparency_data)


if __name__ == "__main__":
    main()