import pandas as pd
import uuid
import json
import datetime
import os

#AREA OF DELIVERIES PRE-PROCESSING
df_area_of_deliveries = pd.read_parquet("docs/area_of_deliveries.parquet")

df_area_of_deliveries["id"] = df_area_of_deliveries["id"].apply(lambda x: str(uuid.UUID(bytes=x)))
df_area_of_deliveries["area_of_delivery"] = df_area_of_deliveries["area_of_delivery"].astype("string").str.lower()
df_area_of_deliveries["total"] = df_area_of_deliveries["total"].round(2)
df_area_of_deliveries["start_date"] = df_area_of_deliveries["start_date"].dt.date
df_area_of_deliveries["end_date"] = df_area_of_deliveries["end_date"].dt.date

print("AREA OF DELIVERIES")
print(df_area_of_deliveries.info())
# print(df_area_of_deliveries.iloc[0])



#AWARDEES PRE-PROCESSING
df_awardees = pd.read_parquet("docs/awardees.parquet")

df_awardees["id"] = df_awardees["id"].apply(lambda x: str(uuid.UUID(bytes=x)))
df_awardees["awardee_name"] = df_awardees["awardee_name"].astype("string").str.lower()
df_awardees["total"] = df_awardees["total"].round(2)
df_awardees["start_date"] = df_awardees["start_date"].dt.date
df_awardees["end_date"] = df_awardees["end_date"].dt.date

print("AWARDEES")
print(df_awardees.info())
# print(df_awardees.iloc[0])



#BUSINESS CATEGORIES PRE-PROCESSING
df_business_categories = pd.read_parquet("docs/business_categories.parquet")

df_business_categories["id"] = df_business_categories["id"].apply(lambda x: str(uuid.UUID(bytes=x)))
df_business_categories["business_category"] = df_business_categories["business_category"].astype("string").str.lower()
df_business_categories["total"] = df_business_categories["total"].round(2)
df_business_categories["start_date"] = df_business_categories["start_date"].dt.date
df_business_categories["end_date"] = df_business_categories["end_date"].dt.date

print("BUSINESS CATEGORIES")
print(df_business_categories.info())
# print(df_business_categories.iloc[0])

# Organizations Pre Processing
df_organizations = pd.read_parquet("docs/organizations.parquet")

df_organizations["id"] = df_organizations["id"].apply(lambda x: str(uuid.UUID(bytes=x)))
df_organizations["organization_name"] = df_organizations["organization_name"].astype("string").str.strip().str.lower()
df_organizations["total"] = df_organizations["total"].round(2)
df_organizations["start_date"] = df_organizations["start_date"].dt.date
df_organizations["end_date"] = df_organizations["end_date"].dt.date

print("ORGANIZATIONS")
print(df_organizations.info())
# print(df_organizations.iloc[0])


# PHILGEPS 
df_philgeps = pd.read_parquet("docs/philgeps.parquet")

# id already converted above — confirmed working, since your sample row already shows a dashed UUID string
df_philgeps["id"] = df_philgeps["id"].apply(lambda x: str(uuid.UUID(bytes=x)))

# --- plain identifiers: string, no case change ---
df_philgeps["reference_id"] = df_philgeps["reference_id"].astype("string")
df_philgeps["contract_no"] = df_philgeps["contract_no"].astype("string")
df_philgeps["award_title"] = df_philgeps["award_title"].astype("string")
df_philgeps["notice_title"] = df_philgeps["notice_title"].astype("string")

# --- matching/categorical columns: string + strip + lowercase, these are your join keys to the dimension tables ---
df_philgeps["awardee_name"] = df_philgeps["awardee_name"].astype("string").str.strip().str.lower()
df_philgeps["organization_name"] = df_philgeps["organization_name"].astype("string").str.strip().str.lower()
df_philgeps["area_of_delivery"] = df_philgeps["area_of_delivery"].astype("string").str.strip().str.lower()
df_philgeps["business_category"] = df_philgeps["business_category"].astype("string").str.strip().str.lower()
df_philgeps["award_status"] = df_philgeps["award_status"].astype("string").str.strip().str.lower()

# --- money ---
df_philgeps["contract_amount"] = df_philgeps["contract_amount"].round(2)
df_philgeps.loc[df_philgeps["award_date"] > pd.Timestamp.today(), "award_date"] = pd.NaT
df_philgeps["award_date"] = df_philgeps["award_date"].dt.date

print("PHILGEPS")
print(df_philgeps.info())
# print(df_philgeps.iloc[0])

#DPWH TRANSPARENCY DATA PRE-PROCESSING
df_dpwh_transparency_data = pd.read_parquet("docs/dpwh_transparency_data.parquet")

# --- rename to snake_case right away, before any other processing ---
df_dpwh_transparency_data = df_dpwh_transparency_data.rename(columns={
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
})

# Turn location into two separate columns
df_dpwh_transparency_data[["province", "region"]] = pd.json_normalize(df_dpwh_transparency_data["location"])

# drop the location
df_dpwh_transparency_data = df_dpwh_transparency_data.drop(columns=["location"])

# Plain text — convert to string dtype, no case change needed (not used for matching/filtering)
df_dpwh_transparency_data["contract_id"] = df_dpwh_transparency_data["contract_id"].astype("string")
df_dpwh_transparency_data["description"] = df_dpwh_transparency_data["description"].astype("string")
# df_dpwh_transparency_data["livestream_url"] = df_dpwh_transparency_data["livestream_url"].astype("string")
# df_dpwh_transparency_data["livestream_video_id"] = df_dpwh_transparency_data["livestream_video_id"].astype("string")

# Categorical / matching columns — convert to string AND lowercase for consistent joins/filtering
df_dpwh_transparency_data["category"] = df_dpwh_transparency_data["category"].astype("string").str.lower()
df_dpwh_transparency_data["component_categories"] = df_dpwh_transparency_data["component_categories"].astype("string").str.lower()
df_dpwh_transparency_data["status"] = df_dpwh_transparency_data["status"].astype("string").str.lower()
df_dpwh_transparency_data["contractor"] = df_dpwh_transparency_data["contractor"].astype("string").str.lower()
df_dpwh_transparency_data["program_name"] = df_dpwh_transparency_data["program_name"].astype("string").str.lower()
df_dpwh_transparency_data["source_of_funds"] = df_dpwh_transparency_data["source_of_funds"].astype("string").str.lower()

# province/region — created via json_normalize earlier, now lowercase them too for consistency
df_dpwh_transparency_data["province"] = df_dpwh_transparency_data["province"].astype("string").str.lower()
df_dpwh_transparency_data["region"] = df_dpwh_transparency_data["region"].astype("string").str.lower()

df_dpwh_transparency_data["start_date"] = pd.to_datetime(df_dpwh_transparency_data["start_date"], errors="coerce").dt.date
df_dpwh_transparency_data["completion_date"] = pd.to_datetime(df_dpwh_transparency_data["completion_date"], errors="coerce").dt.date
df_dpwh_transparency_data["infra_year"] = pd.to_numeric(df_dpwh_transparency_data["infra_year"], errors="coerce").astype("Int64")

df_dpwh_transparency_data["budget"] = df_dpwh_transparency_data["budget"].round(2)

component_category_table = df_dpwh_transparency_data[["contract_id", "component_categories"]].copy()
component_category_table["component_categories"] = component_category_table["component_categories"].str.split(", ")
component_category_table = component_category_table.explode("component_categories")
component_category_table["component_categories"] = component_category_table["component_categories"].str.strip().str.lower()
component_category_table = component_category_table.rename(columns={"component_categories": "component_category"})


df_dpwh_transparency_data = df_dpwh_transparency_data.drop(columns=["component_categories"])
print("DPWH TRANSPARENCY DATA")
print(df_dpwh_transparency_data.info())
print(component_category_table.info())
# print(df_dpwh_transparency_data.iloc[0])


# FLOOD CONTROL PRE-PROCESSING
with open("docs/flood_control.json") as f:
    data = json.load(f)

flood_records = [f["attributes"] for f in data["features"]]
df_flood_control = pd.DataFrame(flood_records)

# --- rename to camelCase ---
df_flood_control = df_flood_control.rename(columns={
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
})
# --- strip whitespace on every object column first ---
for col in df_flood_control.select_dtypes(include="object").columns:
    df_flood_control[col] = df_flood_control[col].str.strip()

# --- plain identifiers / free text: string dtype, no case change ---
df_flood_control["project_id"] = df_flood_control["project_id"].astype("string")
df_flood_control["project_description"] = df_flood_control["project_description"].astype("string")
df_flood_control["project_component_id"] = df_flood_control["project_component_id"].astype("string")
df_flood_control["project_component_description"] = df_flood_control["project_component_description"].astype("string")
df_flood_control["contract_id"] = df_flood_control["contract_id"].astype("string")
df_flood_control["global_id"] = df_flood_control["global_id"].astype("string")  # already dashed format here, not bytes
df_flood_control["creator"] = df_flood_control["creator"].astype("string")
df_flood_control["editor"] = df_flood_control["editor"].astype("string")

# --- categorical / matching columns: string + lowercase, for consistent joins/filtering ---
df_flood_control["region"] = df_flood_control["region"].astype("string").str.lower()
df_flood_control["province"] = df_flood_control["province"].astype("string").str.lower()
df_flood_control["municipality"] = df_flood_control["municipality"].astype("string").str.lower()
df_flood_control["implementing_office"] = df_flood_control["implementing_office"].astype("string").str.lower()
df_flood_control["type_of_work"] = df_flood_control["type_of_work"].astype("string").str.lower()
df_flood_control["infra_type"] = df_flood_control["infra_type"].astype("string").str.lower()
df_flood_control["contractor"] = df_flood_control["contractor"].astype("string").str.lower()
df_flood_control["legislative_district"] = df_flood_control["legislative_district"].astype("string").str.lower()
df_flood_control["district_engineering_office"] = df_flood_control["district_engineering_office"].astype("string").str.lower()

# --- program: all-null, still type it properly rather than leave vague object ---
df_flood_control["program"] = df_flood_control["program"].astype("string")

# --- numeric-looking column stored as text ---
df_flood_control["funding_year"] = pd.to_numeric(df_flood_control["funding_year"], errors="coerce").astype("Int64")

# --- money columns: round to 2dp, drop the redundant *_string duplicates after verifying they match ---
df_flood_control["abc"] = df_flood_control["abc"].round(2)
df_flood_control["contract_cost"] = df_flood_control["contract_cost"].round(2)
# quick check before dropping: do abc/contract_cost already match their string counterparts?
df_flood_control = df_flood_control.drop(columns=["abc_string", "contract_cost_string"])

# --- dates: no meaningful time-of-day in source, so reduce to date-only ---
df_flood_control["completion_date_original"] = pd.to_datetime(
    df_flood_control["completion_date_original"], unit="ms", errors="coerce"
).dt.date
df_flood_control["completion_date_actual"] = pd.to_datetime(
    df_flood_control["completion_date_actual"], errors="coerce"
).dt.date
df_flood_control["start_date"] = pd.to_datetime(
    df_flood_control["start_date"], format="%m/%d/%Y", errors="coerce"
).dt.date

# --- creation_date/edit_date DO have real time-of-day info (system audit timestamps) — keep full datetime ---
df_flood_control["creation_date"] = pd.to_datetime(df_flood_control["creation_date"], unit="ms", errors="coerce")
df_flood_control["edit_date"] = pd.to_datetime(df_flood_control["edit_date"], unit="ms", errors="coerce")

print("FLOOD CONTROL")
print(df_flood_control.info())
# print(df_flood_control.iloc[0])


# CHECKING OF DUPLICATES FOR PRIMARY KEYS
print(df_dpwh_transparency_data["contract_id"].duplicated().sum())
print(df_flood_control["global_id"].duplicated().sum())
print(df_philgeps["id"].duplicated().sum())
print(df_organizations["id"].duplicated().sum())
print(df_awardees["id"].duplicated().sum())
print(df_business_categories["id"].duplicated().sum())
print(df_area_of_deliveries["id"].duplicated().sum())

os.makedirs("clean", exist_ok=True)

df_dpwh_transparency_data.to_parquet("clean/dpwh_transparency_data.parquet", index=False)
df_flood_control.to_parquet("clean/flood_control.parquet", index=False)
component_category_table.to_parquet("clean/component_category_table.parquet", index=False)
df_philgeps.to_parquet("clean/philgeps.parquet", index=False)
df_organizations.to_parquet("clean/organizations.parquet", index=False)
df_awardees.to_parquet("clean/awardees.parquet", index=False)
df_business_categories.to_parquet("clean/business_categories.parquet", index=False)
df_area_of_deliveries.to_parquet("clean/area_of_deliveries.parquet", index=False)

