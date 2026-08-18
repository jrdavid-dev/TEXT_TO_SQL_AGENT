import pandas as pd
import uuid
import json
import datetime

#AREA OF DELIVERIES PRE-PROCESSING
df_area_of_deliveries = pd.read_parquet("docs/area_of_deliveries.parquet")

df_area_of_deliveries["id"] = df_area_of_deliveries["id"].apply(lambda x: str(uuid.UUID(bytes=x)))
df_area_of_deliveries["area_of_delivery"] = df_area_of_deliveries["area_of_delivery"].astype("string").str.lower()
df_area_of_deliveries["total"] = df_area_of_deliveries["total"].round(2)
df_area_of_deliveries["start_date"] = df_area_of_deliveries["start_date"].dt.date
df_area_of_deliveries["end_date"] = df_area_of_deliveries["end_date"].dt.date

print(df_area_of_deliveries.info())
print(df_area_of_deliveries.iloc[0])



#AWARDEES PRE-PROCESSING
df_awardees = pd.read_parquet("docs/awardees.parquet")

df_awardees["id"] = df_awardees["id"].apply(lambda x: str(uuid.UUID(bytes=x)))
df_awardees["awardee_name"] = df_awardees["awardee_name"].astype("string").str.lower()
df_awardees["total"] = df_awardees["total"].round(2)
df_awardees["start_date"] = df_awardees["start_date"].dt.date
df_awardees["end_date"] = df_awardees["end_date"].dt.date

print(df_awardees.info())
print(df_awardees.iloc[0])



#BUSINESS CATEGORIES PRE-PROCESSING
df_business_categories = pd.read_parquet("docs/business_categories.parquet")

df_business_categories["id"] = df_business_categories["id"].apply(lambda x: str(uuid.UUID(bytes=x)))
df_business_categories["business_category"] = df_business_categories["business_category"].astype("string").str.lower()
df_business_categories["total"] = df_business_categories["total"].round(2)
df_business_categories["start_date"] = df_business_categories["start_date"].dt.date
df_business_categories["end_date"] = df_business_categories["end_date"].dt.date

print(df_business_categories.info())
print(df_business_categories.iloc[0])

#DPWH TRANSPARENCY DATA PRE-PROCESSING
df_dpwh_transparency_data = pd.read_parquet("docs/dpwh_transparency_data.parquet")

# Turn location into two seperate columns
df_dpwh_transparency_data[["province", "region"]] =  pd.json_normalize(df_dpwh_transparency_data["location"])

# drop the location
df_dpwh_transparency_data = df_dpwh_transparency_data.drop(columns=["location"])

# Plain text — convert to string dtype, no case change needed (not used for matching/filtering)
df_dpwh_transparency_data["contractId"] = df_dpwh_transparency_data["contractId"].astype("string")
df_dpwh_transparency_data["description"] = df_dpwh_transparency_data["description"].astype("string")
# df_dpwh_transparency_data["livestreamUrl"] = df_dpwh_transparency_data["livestreamUrl"].astype("string")
# df_dpwh_transparency_data["livestreamVideoId"] = df_dpwh_transparency_data["livestreamVideoId"].astype("string")

# Categorical / matching columns — convert to string AND lowercase for consistent joins/filtering
df_dpwh_transparency_data["category"] = df_dpwh_transparency_data["category"].astype("string").str.lower()
df_dpwh_transparency_data["componentCategories"] = df_dpwh_transparency_data["componentCategories"].astype("string").str.lower()
df_dpwh_transparency_data["status"] = df_dpwh_transparency_data["status"].astype("string").str.lower()
df_dpwh_transparency_data["contractor"] = df_dpwh_transparency_data["contractor"].astype("string").str.lower()
df_dpwh_transparency_data["programName"] = df_dpwh_transparency_data["programName"].astype("string").str.lower()
df_dpwh_transparency_data["sourceOfFunds"] = df_dpwh_transparency_data["sourceOfFunds"].astype("string").str.lower()

# province/region — created via json_normalize earlier, now lowercase them too for consistency
df_dpwh_transparency_data["province"] = df_dpwh_transparency_data["province"].astype("string").str.lower()
df_dpwh_transparency_data["region"] = df_dpwh_transparency_data["region"].astype("string").str.lower()

df_dpwh_transparency_data["startDate"] = pd.to_datetime(df_dpwh_transparency_data["startDate"], errors="coerce").dt.date
df_dpwh_transparency_data["completionDate"] = pd.to_datetime(df_dpwh_transparency_data["completionDate"], errors="coerce").dt.date
df_dpwh_transparency_data["infraYear"] = pd.to_numeric(df_dpwh_transparency_data["infraYear"], errors="coerce").astype("Int64")

df_dpwh_transparency_data["budget"] = df_dpwh_transparency_data["budget"].round(2)

componentCategoriesTable = df_dpwh_transparency_data[["contractId", "componentCategories"]].copy()
componentCategoriesTable["componentCategories"] = componentCategoriesTable["componentCategories"].str.split(", ")
componentCategoriesTable = componentCategoriesTable.explode("componentCategories")
componentCategoriesTable["componentCategories"] = componentCategoriesTable["componentCategories"].str.strip().str.lower()
# Drop component Categories
df_dpwh_transparency_data = df_dpwh_transparency_data.drop(columns=["componentCategories"])

print(df_dpwh_transparency_data.info())
print(df_dpwh_transparency_data.iloc[0])


# FLOOD CONTROL PRE-PROCESSING
with open("docs/flood_control.json") as f:
    data = json.load(f)

flood_records = [f["attributes"] for f in data["features"]]
df_flood_control = pd.DataFrame(flood_records)

# --- rename to camelCase ---
df_flood_control = df_flood_control.rename(columns={
    "InfraYear": "infraYear",
    "Region": "region",
    "Province": "province",
    "Municipality": "municipality",
    "ImplementingOffice": "implementingOffice",
    "ProjectID": "projectId",
    "ProjectDescription": "projectDescription",
    "ProjectComponentID": "projectComponentId",
    "ProjectComponentDescription": "projectComponentDescription",
    "Program": "program",
    "TypeofWork": "typeOfWork",
    "infra_type": "infraType",
    "Longitude": "longitude",
    "Latitude": "latitude",
    "ContractID": "contractId",
    "ABC": "abc",
    "ContractCost": "contractCost",
    "CompletionDateOriginal": "completionDateOriginal",
    "CompletionYear": "completionYear",
    "Contractor": "contractor",
    "ObjectId": "objectId",
    "CreationDate": "creationDate",
    "Creator": "creator",
    "EditDate": "editDate",
    "Editor": "editor",
    "FundingYear": "fundingYear",
    "LegislativeDistrict": "legislativeDistrict",
    "DistrictEngineeringOffice": "districtEngineeringOffice",
    "GlobalID": "globalId",
    "ABC_String": "abcString",
    "ContractCost_String": "contractCostString",
    "CompletionDateActual": "completionDateActual",
    "StartDate": "startDate",
})
print(df_flood_control.info())
print(df_flood_control.iloc[0])
# --- strip whitespace on every object column first ---
for col in df_flood_control.select_dtypes(include="object").columns:
    df_flood_control[col] = df_flood_control[col].str.strip()

# --- plain identifiers / free text: string dtype, no case change ---
df_flood_control["projectId"] = df_flood_control["projectId"].astype("string")
df_flood_control["projectDescription"] = df_flood_control["projectDescription"].astype("string")
df_flood_control["projectComponentId"] = df_flood_control["projectComponentId"].astype("string")
df_flood_control["projectComponentDescription"] = df_flood_control["projectComponentDescription"].astype("string")
df_flood_control["contractId"] = df_flood_control["contractId"].astype("string")
df_flood_control["globalId"] = df_flood_control["globalId"].astype("string")  # already dashed format here, not bytes
df_flood_control["creator"] = df_flood_control["creator"].astype("string")
df_flood_control["editor"] = df_flood_control["editor"].astype("string")

# --- categorical / matching columns: string + lowercase, for consistent joins/filtering ---
df_flood_control["region"] = df_flood_control["region"].astype("string").str.lower()
df_flood_control["province"] = df_flood_control["province"].astype("string").str.lower()
df_flood_control["municipality"] = df_flood_control["municipality"].astype("string").str.lower()
df_flood_control["implementingOffice"] = df_flood_control["implementingOffice"].astype("string").str.lower()
df_flood_control["typeOfWork"] = df_flood_control["typeOfWork"].astype("string").str.lower()
df_flood_control["infraType"] = df_flood_control["infraType"].astype("string").str.lower()
df_flood_control["contractor"] = df_flood_control["contractor"].astype("string").str.lower()
df_flood_control["legislativeDistrict"] = df_flood_control["legislativeDistrict"].astype("string").str.lower()
df_flood_control["districtEngineeringOffice"] = df_flood_control["districtEngineeringOffice"].astype("string").str.lower()

# --- program: all-null, still type it properly rather than leave vague object ---
df_flood_control["program"] = df_flood_control["program"].astype("string")

# --- numeric-looking column stored as text ---
df_flood_control["fundingYear"] = pd.to_numeric(df_flood_control["fundingYear"], errors="coerce").astype("Int64")

# --- money columns: round to 2dp, drop the redundant *_String duplicates after verifying they match ---
df_flood_control["abc"] = df_flood_control["abc"].round(2)
df_flood_control["contractCost"] = df_flood_control["contractCost"].round(2)
# quick check before dropping: do abc/contractCost already match their string counterparts?
df_flood_control = df_flood_control.drop(columns=["abcString", "contractCostString"])

# --- dates: no meaningful time-of-day in source, so reduce to date-only ---
df_flood_control["completionDateOriginal"] = pd.to_datetime(
    df_flood_control["completionDateOriginal"], unit="ms", errors="coerce"
).dt.date
df_flood_control["completionDateActual"] = pd.to_datetime(
    df_flood_control["completionDateActual"], errors="coerce"
).dt.date
df_flood_control["startDate"] = pd.to_datetime(
    df_flood_control["startDate"], format="%m/%d/%Y", errors="coerce"
).dt.date

# --- creationDate/editDate DO have real time-of-day info (system audit timestamps) — keep full datetime ---
df_flood_control["creationDate"] = pd.to_datetime(df_flood_control["creationDate"], unit="ms", errors="coerce")
df_flood_control["editDate"] = pd.to_datetime(df_flood_control["editDate"], unit="ms", errors="coerce")

print(df_flood_control.info())
print(df_flood_control.iloc[0])

# Organizations Pre Processing
df_organizations = pd.read_parquet("docs/organizations.parquet")

df_organizations["id"] = df_organizations["id"].apply(lambda x: str(uuid.UUID(bytes=x)))
df_organizations["organization_name"] = df_organizations["organization_name"].astype("string").str.strip().str.lower()
df_organizations["total"] = df_organizations["total"].round(2)
df_organizations["start_date"] = df_organizations["start_date"].dt.date
df_organizations["end_date"] = df_organizations["end_date"].dt.date

print(df_organizations.info())
print(df_organizations.iloc[0])


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

print(df_philgeps.info())
print(df_philgeps.iloc[0])

