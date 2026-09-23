import requests
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/chat"

SYSTEM_PROMPT = ""
DATA_DICTIONARY = ""
system_path = os.path.join("prompts", "system_prompt.md")
data_path = os.path.join("docs", "data_dictionary.md")

logger.info(f"Loading system prompt from {system_path}")
with open(system_path, "r", encoding="utf-8") as file:
    SYSTEM_PROMPT = file.read()

logger.info(f"Loading data dictionary from {data_path}")
with open(data_path, "r", encoding="utf-8") as file:
    DATA_DICTIONARY = file.read()

SYSTEM_PROMPT = SYSTEM_PROMPT.replace(
    "{data_dictionary_content}",
    DATA_DICTIONARY
)
logger.info(f"System prompt built ({len(SYSTEM_PROMPT)} characters)")


def clean_sql_response(raw_response: str) -> str:
    """Strip markdown code fences from an LLM's SQL response, if present."""
    cleaned = raw_response.strip()

    if cleaned.startswith("```sql"):
        cleaned = cleaned.removeprefix("```sql")
        logger.debug("Stripped '```sql' fence from response")
    elif cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```")
        logger.debug("Stripped '```' fence from response")

    if cleaned.endswith("```"):
        cleaned = cleaned.removesuffix("```")

    return cleaned.strip()


def generate_sql(question: str, model: str = "qwen2.5-coder:7b") -> str:
    logger.info(f"Generating SQL for question: {question!r}")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ],
        "options": {
            "temperature": 0.0
        },
        "stream": False,
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama request failed: {e}")
        logger.error(f"Response body: {response.text}")  # add this line
        raise   

    data = response.json()
    raw_output = data["message"]["content"]
    logger.debug(f"Raw model output: {raw_output!r}")

    cleaned_sql = clean_sql_response(raw_output)
    logger.info(f"Generated SQL: {cleaned_sql}")

    return cleaned_sql