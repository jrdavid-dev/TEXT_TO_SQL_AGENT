import pandas as pd
import uuid
import json
import datetime
import os

CLEAN_DIR = "clean"
DOCS_DIR = "docs"
DPWH_COLUMN_RENAMES = {
    "contractId": "contract_id",
    "amountPaid": "amount_paid",
    "startDate": "start_date",
    "completionDate": "completion_date",
    "infraYear": "infra_year",
    "programName": "program_name",
    "sourceOfFunds": "source_of_funds",
    "isLive": "is_live",
    "livestreamUrl": "livestream_url",
    "livestreamVideoId": "livestream_video_id",
    "livestreamDetectedAt": "livestream_detected_at",
    "reportCount": "report_count",
    "hasSatelliteImage": "has_satellite_image",
    "componentCategories": "component_categories",
}

FLOOD_CONTROL_COLUMN_RENAMES = {
    "InfraYear": "infra_year",
    "Region": "region",
    "Province": "province",
    "Municipality": "municipality",
    "ImplementingOffice": "implementing_office",
    "ProjectID": "project_id",
    "ProjectDescription": "project_description",
    "ProjectComponentID": "project_component_id",
    "ProjectComponentDescription": "project_component_description",
    "Program": "program",
    "TypeofWork": "type_of_work",
    "infra_type": "infra_type",
    "Longitude": "longitude",
    "Latitude": "latitude",
    "ContractID": "contract_id",
    "ABC": "abc",
    "ContractCost": "contract_cost",
    "CompletionDateOriginal": "completion_date_original",
    "CompletionYear": "completion_year",
    "Contractor": "contractor",
    "ObjectId": "object_id",
    "CreationDate": "creation_date",
    "Creator": "creator",
    "EditDate": "edit_date",
    "Editor": "editor",
    "FundingYear": "funding_year",
    "LegislativeDistrict": "legislative_district",
    "DistrictEngineeringOffice": "district_engineering_office",
    "GlobalID": "global_id",
    "ABC_String": "abc_string",
    "ContractCost_String": "contract_cost_string",
    "CompletionDateActual": "completion_date_actual",
    "StartDate": "start_date",
}

# HELPER FUNCTIONS
def uuid_bytes_to_str(series:  pd.Series) -> pd.Series:
    return series.apply(lambda x: str(uuid.UUID(bytes = x)))

def normalize_text(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().str.lower()

def find_duplicate_names(df: pd.DataFrame, name_col: str) -> pd.DataFrame:
        """Return name values that appear on more than one row."""
        counts = df[name_col].value_counts()
        dupes = counts[counts > 1]
        return df[df[name_col].isin(dupes.index)].sort_values(name_col)

def merge_duplicate_names(dataframe: pd.DataFrame, name_column: str) -> pd.DataFrame:
    """Collapse duplicate name rows into one, summing counts/totals and spanning dates."""
    merged = (
        dataframe
        .groupby(name_column, as_index=False)
        .agg(
            count=("count", "sum"),
            total=("total", "sum"),
            start_date=("start_date", "min"),
            end_date=("end_date", "max"),
        )
    )
    merged["id"] = [str(uuid.uuid4()) for _ in range(len(merged))]
    return merged


# LOAD FUNCTIONS
def load_area_of_deliveries(docs_dir: str = DOCS_DIR) -> pd.DataFrame:
    """Read the raw area_of_deliveries parquet file into a DataFrame."""
    path = os.path.join(docs_dir, "area_of_deliveries.parquet")
    return pd.read_parquet(path)


def load_awardees(docs_dir: str = DOCS_DIR) -> pd.DataFrame:
    """Read the raw awardees parquet file into a DataFrame."""
    path = os.path.join(docs_dir, "awardees.parquet")
    return pd.read_parquet(path)


def load_business_categories(docs_dir: str = DOCS_DIR) -> pd.DataFrame:
    """Read the raw business_categories parquet file into a DataFrame."""
    path = os.path.join(docs_dir, "business_categories.parquet")
    return pd.read_parquet(path)


def load_organizations(docs_dir: str = DOCS_DIR) -> pd.DataFrame:
    """Read the raw organizations parquet file into a DataFrame."""
    path = os.path.join(docs_dir, "organizations.parquet")
    return pd.read_parquet(path)


def load_philgeps(docs_dir: str = DOCS_DIR) -> pd.DataFrame:
    """Read the raw philgeps fact table parquet file into a DataFrame."""
    path = os.path.join(docs_dir, "philgeps.parquet")
    return pd.read_parquet(path)


def load_dpwh_transparency_data(docs_dir: str = DOCS_DIR) -> pd.DataFrame:
    """Read the raw DPWH transparency data parquet file into a DataFrame."""
    path = os.path.join(docs_dir, "dpwh_transparency_data.parquet")
    return pd.read_parquet(path)


def load_flood_control(docs_dir: str = DOCS_DIR) -> pd.DataFrame:
    """Read the flood control GeoJSON export and flatten it into a DataFrame."""
    path = os.path.join(docs_dir, "flood_control.json")
    with open(path) as f:
        data = json.load(f)
    records = [f["attributes"] for f in data["features"]]
    return pd.DataFrame(records)

def load_clean_flood_control(clean_dir: str = CLEAN_DIR) -> pd.DataFrame:
    """Read the cleaned flood control parquet file into a DataFrame."""
    path = os.path.join(clean_dir, "flood_control.parquet")
    return pd.read_parquet(path)

def load_component_category_table(clean_dir: str = CLEAN_DIR) -> pd.DataFrame:
    """Read the cleaned component category junction table parquet file into a DataFrame."""
    path = os.path.join(clean_dir, "component_category_table.parquet")
    return pd.read_parquet(path)


#CLEANER FUNCTIONS
def clean_dimension_table(dataframe: pd.DataFrame, name_column: str) -> pd.DataFrame:
    """Clean a PhilGEPS dimension table (id, name column, total, start/end dates)."""
    dataframe = dataframe.copy()

    dataframe["id"] = uuid_bytes_to_str(dataframe["id"])
    dataframe[name_column] = normalize_text(dataframe[name_column])
    dataframe["total"] = dataframe["total"].round(2)
    dataframe["start_date"] = dataframe["start_date"].dt.date 
    dataframe["end_date"] = dataframe["end_date"].dt.date

    return dataframe


def clean_area_of_deliveries(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean the area_of_deliveries dimension table."""
    return clean_dimension_table(dataframe, name_column="area_of_delivery")


def clean_awardees(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean the awardees dimension table."""
    return clean_dimension_table(dataframe, name_column="awardee_name")

def clean_organizations(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean the organizations dimension table."""
    dataframe = clean_dimension_table(dataframe, name_column="organization_name")
    dataframe = merge_duplicate_names(dataframe, name_column="organization_name")
    return dataframe

def clean_business_categories(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean the business_categories dimension table."""
    return clean_dimension_table(dataframe, name_column="business_category")

def clean_philgeps(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean and type the PhilGEPS fact table."""
    dataframe = dataframe.copy()

    dataframe["id"] = uuid_bytes_to_str(dataframe["id"])

    dataframe["reference_id"] = dataframe["reference_id"].astype("string")
    dataframe["contract_no"] = dataframe["contract_no"].astype("string")
    dataframe["award_title"] = dataframe["award_title"].astype("string")
    dataframe["notice_title"] = dataframe["notice_title"].astype("string")

    dataframe["awardee_name"] = normalize_text(dataframe["awardee_name"])
    dataframe["organization_name"] = normalize_text(dataframe["organization_name"])
    dataframe["area_of_delivery"] = normalize_text(dataframe["area_of_delivery"])
    dataframe["business_category"] = normalize_text(dataframe["business_category"])
    dataframe["award_status"] = normalize_text(dataframe["award_status"])

    dataframe["contract_amount"] = dataframe["contract_amount"].round(2)

    dataframe.loc[
        dataframe["award_date"] > pd.Timestamp.today(),
        "award_date"
    ] = pd.NaT

    dataframe["award_date"] = dataframe["award_date"].dt.date

    return dataframe


def clean_dpwh_transparency_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean and type the DPWH transparency contracts table."""
    dataframe = dataframe.copy()
    dataframe = dataframe.rename(columns=DPWH_COLUMN_RENAMES)

    dataframe[["province", "region"]] = pd.json_normalize(dataframe["location"])
    dataframe = dataframe.drop(columns=["location"])

    dataframe["contract_id"] = dataframe["contract_id"].astype("string")
    dataframe["description"] = dataframe["description"].astype("string")
    # df_dpwh_transparency_data["livestream_url"] = df_dpwh_transparency_data["livestream_url"].astype("string")
    # df_dpwh_transparency_data["livestream_video_id"] = df_dpwh_transparency_data["livestream_video_id"].astype("string")
    
    dataframe["category"] = normalize_text(dataframe["category"])
    dataframe["component_categories"] = normalize_text(
        dataframe["component_categories"]
    )
    dataframe["status"] = normalize_text(dataframe["status"])
    dataframe["contractor"] = normalize_text(dataframe["contractor"])
    dataframe["program_name"] = normalize_text(dataframe["program_name"])
    dataframe["source_of_funds"] = normalize_text(dataframe["source_of_funds"])
    dataframe["province"] = normalize_text(dataframe["province"])
    dataframe["region"] = normalize_text(dataframe["region"])

    dataframe["start_date"] = pd.to_datetime(
        dataframe["start_date"],
        errors="coerce"
    ).dt.date

    dataframe["completion_date"] = pd.to_datetime(
        dataframe["completion_date"],
        errors="coerce"
    ).dt.date

    dataframe["infra_year"] = pd.to_numeric(
        dataframe["infra_year"],
        errors="coerce"
    ).astype("Int64")

    dataframe["budget"] = dataframe["budget"].round(2)

    return dataframe


def build_component_category_table(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Explode the multi-value component_categories column into a junction table."""
    table = dataframe[["contract_id", "component_categories"]].copy()

    table["component_categories"] = table["component_categories"].str.split(", ")
    table = table.explode("component_categories")

    table["component_categories"] = (
        table["component_categories"]
        .str.strip()
        .str.lower()
    )
    table = table.dropna()
    return table.rename(
        columns={"component_categories": "component_category"}
    )


def drop_component_categories(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Drop the now-redundant multi-value column after the junction table is built."""
    return dataframe.drop(columns=["component_categories"])


def clean_flood_control(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean and type the flood control GeoJSON-derived table."""
    dataframe = dataframe.copy()
    dataframe = dataframe.rename(columns=FLOOD_CONTROL_COLUMN_RENAMES)

    for column in dataframe.select_dtypes(include="object").columns:
        dataframe[column] = dataframe[column].str.strip()

    dataframe["project_id"] = dataframe["project_id"].astype("string")
    dataframe["project_description"] = dataframe["project_description"].astype("string")
    dataframe["project_component_id"] = dataframe["project_component_id"].astype("string")
    dataframe["project_component_description"] = dataframe["project_component_description"].astype("string")
    dataframe["contract_id"] = dataframe["contract_id"].astype("string")
    dataframe["global_id"] = dataframe["global_id"].astype("string")
    dataframe["creator"] = dataframe["creator"].astype("string")
    dataframe["editor"] = dataframe["editor"].astype("string")
    dataframe["program"] = dataframe["program"].astype("string")

    dataframe["region"] = normalize_text(dataframe["region"])
    dataframe["province"] = normalize_text(dataframe["province"])
    dataframe["municipality"] = normalize_text(dataframe["municipality"])
    dataframe["implementing_office"] = normalize_text(dataframe["implementing_office"])
    dataframe["type_of_work"] = normalize_text(dataframe["type_of_work"])
    dataframe["infra_type"] = normalize_text(dataframe["infra_type"])
    dataframe["contractor"] = normalize_text(dataframe["contractor"])
    dataframe["legislative_district"] = normalize_text(dataframe["legislative_district"])
    dataframe["district_engineering_office"] = normalize_text(
        dataframe["district_engineering_office"]
    )

    dataframe["funding_year"] = pd.to_numeric(
        dataframe["funding_year"],
        errors="coerce"
    ).astype("Int64")

    dataframe["abc"] = dataframe["abc"].round(2)
    dataframe["contract_cost"] = dataframe["contract_cost"].round(2)

    dataframe = dataframe.drop(
        columns=["abc_string", "contract_cost_string"]
    )

    dataframe["completion_date_original"] = pd.to_datetime(
        dataframe["completion_date_original"],
        unit="ms",
        errors="coerce"
    ).dt.date

    dataframe["completion_date_actual"] = pd.to_datetime(
        dataframe["completion_date_actual"],
        errors="coerce"
    ).dt.date

    dataframe["start_date"] = pd.to_datetime(
        dataframe["start_date"],
        format="%m/%d/%Y",
        errors="coerce"
    ).dt.date

    dataframe["creation_date"] = pd.to_datetime(
        dataframe["creation_date"],
        unit="ms",
        errors="coerce"
    )

    dataframe["edit_date"] = pd.to_datetime(
        dataframe["edit_date"],
        unit="ms",
        errors="coerce"
    )

    return dataframe


def save_dataframe(dataframe: pd.DataFrame, filename: str, clean_dir: str = CLEAN_DIR) -> None:
    """Write a cleaned DataFrame to the clean/ output folder as parquet."""
    os.makedirs(clean_dir, exist_ok=True)
    path = os.path.join(clean_dir, filename)
    dataframe.to_parquet(path, index=False)


def main():
#    """
    df_area_of_deliveries = clean_area_of_deliveries(load_area_of_deliveries())
    print("AREA OF DELIVERIES")
    df_area_of_deliveries.info()
    print(df_area_of_deliveries.iloc[0])

    df_awardees = clean_awardees(load_awardees())
    print("AWARDEES")
    df_awardees.info()
    print(df_awardees.iloc[0])

    df_business_categories = clean_business_categories(load_business_categories())
    print("BUSINESS CATEGORIES")
    df_business_categories.info()
    print(df_business_categories.iloc[0])

    df_organizations = clean_organizations(load_organizations())
    print("ORGANIZATIONS")
    df_organizations.info()
    print(df_organizations.iloc[0])

    df_philgeps = clean_philgeps(load_philgeps())
    print("PHILGEPS")
    df_philgeps.info()
    print(df_philgeps.iloc[0])
    
    
    df_dpwh_transparency_data = clean_dpwh_transparency_data(load_dpwh_transparency_data())
    component_category_table = build_component_category_table(df_dpwh_transparency_data)
    df_dpwh_transparency_data = drop_component_categories(df_dpwh_transparency_data)
    print("DPWH TRANSPARENCY DATA")
    df_dpwh_transparency_data.info()
    print(df_dpwh_transparency_data.iloc[0])
    print("COMPONENT CATEGORY TABLE")
    component_category_table.info()
    print(component_category_table.iloc[0])
    
    df_flood_control = clean_flood_control(load_flood_control())
    print("FLOOD CONTROL")
    df_flood_control.info()
    print(df_flood_control.iloc[0])
    
    save_dataframe(df_area_of_deliveries, "area_of_deliveries.parquet")
    save_dataframe(df_awardees, "awardees.parquet")
    save_dataframe(df_business_categories, "business_categories.parquet")
    save_dataframe(df_organizations, "organizations.parquet")
    save_dataframe(df_philgeps, "philgeps.parquet")
    save_dataframe(df_dpwh_transparency_data, "dpwh_transparency_data.parquet")
    save_dataframe(component_category_table, "component_category_table.parquet")
    save_dataframe(df_flood_control, "flood_control.parquet")
    save_dataframe(component_category_table, "component_category_table.parquet")
#   """
    


if __name__ == "__main__":
    main()

