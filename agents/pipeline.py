import logging
from sqlalchemy.exc import SQLAlchemyError

from generator import generate_sql
from validator import is_safe_sql
from executor import run_query

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_pipeline(question: str, max_retries: int = 3):
    current_question = question

    for attempt in range(max_retries):
        logger.info(f"Attempt {attempt + 1}/{max_retries}")

        sql = generate_sql(current_question)

        if not is_safe_sql(sql):
            logger.warning("Generated SQL failed the safety check. Stopping.")
            return None

        try:
            result = run_query(sql)
            logger.info(f"Attempt {attempt + 1} succeeded")
            return result  # success — exit immediately with the answer

        except SQLAlchemyError as e:
            error_message = str(e)
            logger.warning(f"Attempt {attempt + 1} failed: {error_message}")
            current_question = (
                f"{question}\n\n"
                f"Your previous SQL was:\n{sql}\n\n"
                f"It failed with this error:\n{error_message}\n"
                f"Please fix the query."
            )

    logger.error(f"Failed to generate a working query after {max_retries} attempts.")
    return None


if __name__ == "__main__":
    question = "Q1 Top 10 contractors in dpwh_transparency_data by total budget(solo projects). Add total projects"
    run_pipeline(question)