import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

FORBIDDEN_KEYWORDS = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]


def is_safe_sql(sql: str) -> bool:

    if sql == "":
        logger.warning("Rejected SQL: empty string")
        return False

    if sql.split()[0].lower() != "select":
        logger.warning(f"Rejected SQL: does not start with SELECT (got {sql_list[0]!r})")
        return False

    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in sql.upper():
            logger.warning(f"Rejected SQL: contains forbidden keyword {keyword!r} -> {sql}")
            return False

    logger.info(f"SQL passed validation: {sql}")
    return True