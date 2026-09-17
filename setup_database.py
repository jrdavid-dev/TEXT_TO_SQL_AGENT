from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from data_preprocessing import (
    load_philgeps,
    load_awardees,
    load_organizations,
    load_area_of_deliveries,
    load_business_categories,
    load_dpwh_transparency_data,
    load_clean_flood_control,
    load_component_category_table
)

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def get_engine():
    """Create a SQLAlchemy engine for the Postgres database."""
    url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)

def run_schema(engine, schema_path: str = "schema.sql") -> None:
    """Execute the DDL in schema.sql against the database."""
    with open(schema_path) as f:
        ddl = f.read()

    with engine.connect() as conn:
        for statement in ddl.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
        conn.commit()

def load_dataframe_to_table(df, table_name: str, engine) -> None:
    """Insert a cleaned DataFrame into an existing Postgres table."""
    df.to_sql(table_name, engine, if_exists="append", index=False)

def main():
    engine = get_engine()
    run_schema(engine)
    # Load PhilGEPS dimension tables
    load_dataframe_to_table(load_area_of_deliveries("clean"), "area_of_deliveries", engine)
    load_dataframe_to_table(load_awardees("clean"), "awardees", engine)
    load_dataframe_to_table(load_business_categories("clean"), "business_categories", engine)
    load_dataframe_to_table(load_organizations("clean"), "organizations", engine)

    # Load PhilGEPS fact table
    load_dataframe_to_table(load_philgeps("clean"), "philgeps", engine)

    # Load DPWH tables
    load_dataframe_to_table(load_dpwh_transparency_data("clean"), "dpwh_transparency_data", engine)
    load_dataframe_to_table(load_component_category_table("clean"), "component_category_table", engine)

    # Load Flood Control table
    load_dataframe_to_table(load_clean_flood_control("clean"), "flood_control", engine)  

if __name__ == "__main__":
    main()