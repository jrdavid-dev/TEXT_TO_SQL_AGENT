import logging
import time
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_engine():
    """Create a SQLAlchemy engine for the Postgres database."""
    url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    logger.info(f"Connecting to database '{DB_NAME}' at {DB_HOST}:{DB_PORT}")
    return create_engine(url)


def run_schema(engine, schema_path: str = "schema.sql") -> None:
    """Execute the DDL in schema.sql against the database."""
    logger.info(f"Running schema from {schema_path}")
    with open(schema_path) as f:
        ddl = f.read()

    statements = [s.strip() for s in ddl.split(";") if s.strip()]
    with engine.connect() as conn:
        for i, statement in enumerate(statements, start=1):
            logger.debug(f"Executing statement {i}/{len(statements)}")
            conn.execute(text(statement))
        conn.commit()
    logger.info(f"Schema applied successfully ({len(statements)} statements)")


def load_dataframe_to_table(df, table_name: str, engine) -> None:
    """Insert a cleaned DataFrame into an existing Postgres table."""
    row_count = len(df)
    logger.info(f"Loading {row_count:,} rows into '{table_name}'...")
    start = time.perf_counter()

    df.to_sql(table_name, engine, if_exists="append", index=False)

    elapsed = time.perf_counter() - start
    logger.info(f"Loaded '{table_name}' ({row_count:,} rows) in {elapsed:.2f}s")


def main():
    overall_start = time.perf_counter()
    logger.info("Starting database setup")

    engine = get_engine()
    run_schema(engine)

    # Load PhilGEPS dimension tables
    logger.info("Loading PhilGEPS dimension tables")
    load_dataframe_to_table(load_area_of_deliveries("clean"), "area_of_deliveries", engine)
    load_dataframe_to_table(load_awardees("clean"), "awardees", engine)
    load_dataframe_to_table(load_business_categories("clean"), "business_categories", engine)
    load_dataframe_to_table(load_organizations("clean"), "organizations", engine)

    # Load PhilGEPS fact table
    logger.info("Loading PhilGEPS fact table")
    load_dataframe_to_table(load_philgeps("clean"), "philgeps", engine)

    # Load DPWH tables
    logger.info("Loading DPWH tables")
    load_dataframe_to_table(load_dpwh_transparency_data("clean"), "dpwh_transparency_data", engine)
    load_dataframe_to_table(load_component_category_table("clean"), "component_category_table", engine)

    # Load Flood Control table
    logger.info("Loading flood control table")
    load_dataframe_to_table(load_clean_flood_control("clean"), "flood_control", engine)

    overall_elapsed = time.perf_counter() - overall_start
    logger.info(f"Database setup complete in {overall_elapsed:.2f}s")


if __name__ == "__main__":
    main()