from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from generator import generate_sql
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

load_dotenv()

AGENT_DB_USER = os.getenv("AGENT_DB_USER")
AGENT_DB_PASSWORD = os.getenv("AGENT_DB_PASSWORD")
AGENT_DB_HOST = os.getenv("AGENT_DB_HOST")
AGENT_DB_PORT = os.getenv("AGENT_DB_PORT")
AGENT_DB_NAME = os.getenv("AGENT_DB_NAME")


def get_readonly_engine():
    logger.info(f"Creating read-only engine for '{AGENT_DB_NAME}' as user '{AGENT_DB_USER}'")
    url = f"postgresql+psycopg2://{AGENT_DB_USER}:{AGENT_DB_PASSWORD}@{AGENT_DB_HOST}:{AGENT_DB_PORT}/{AGENT_DB_NAME}"
    return create_engine(url)


def run_query(sql: str):
    logger.info(f"Executing query: {sql}")
    engine = get_readonly_engine()

    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = [dict(row._mapping) for row in result]
    except SQLAlchemyError as e:
        logger.error(f"Query failed: {e}")
        raise

    logger.info(f"Query returned {len(rows)} row(s)")
    return rows