from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from generator import generate_sql
import os

load_dotenv()

AGENT_DB_USER = os.getenv("AGENT_DB_USER")
AGENT_DB_PASSWORD = os.getenv("AGENT_DB_PASSWORD")
AGENT_DB_HOST = os.getenv("AGENT_DB_HOST")
AGENT_DB_PORT = os.getenv("AGENT_DB_PORT")
AGENT_DB_NAME = os.getenv("AGENT_DB_NAME")

def get_readonly_engine():
    url = f"postgresql+psycopg2://{AGENT_DB_USER}:{AGENT_DB_PASSWORD}@{AGENT_DB_HOST}:{AGENT_DB_PORT}/{AGENT_DB_NAME}"
    return create_engine(url)

def run_query(sql: str):
    engine = get_readonly_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        rows = [dict(row._mapping) for row in result]
    return rows
""" test
question = "Q1 Top 10 contractors in dpwh_transparency_data by total budget(solo projects). Add total projects"
sql = generate_sql(question)
result = run_query(sql)
print(sql)
print(result)
"""