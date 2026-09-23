import requests
import os

OLLAMA_URL = "http://localhost:11434/api/chat"

SYSTEM_PROMPT = ""
DATA_DICTIONARY = ""
system_path = os.path.join("prompts", "system_prompt.md")
data_path = os.path.join("docs", "data_dictionary.md")

with open(system_path, "r", encoding="utf-8") as file:
    SYSTEM_PROMPT = file.read()

with open(data_path, "r", encoding="utf-8") as file:
    DATA_DICTIONARY = file.read()

SYSTEM_PROMPT = SYSTEM_PROMPT.replace(
    "{data_dictionary_content}",
    DATA_DICTIONARY
)


def clean_sql_response(raw_response: str) -> str:
    """Strip markdown code fences from an LLM's SQL response, if present."""
    cleaned = raw_response.strip()

    if cleaned.startswith("```sql"):
        cleaned = cleaned.removeprefix("```sql")
    elif cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```")

    if cleaned.endswith("```"):
        cleaned = cleaned.removesuffix("```")

    return cleaned.strip()

def generate_sql(question: str, model: str = "qwen2.5:7b") -> str:
    
    payload = {
        "model" : model,
        "messages" : [
            {   "role" : "system",
                "content" : SYSTEM_PROMPT},
             {
                 "role" : "user",
                 "content" : question
             }
        ],
        "options" : {
            "temperature" : 0.0
        },
        "stream" : False,
    }

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()

    data = response.json()
    raw_output = data["message"]["content"]

    cleaned_sql = clean_sql_response(raw_output)

    return cleaned_sql
