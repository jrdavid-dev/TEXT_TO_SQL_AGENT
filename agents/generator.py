import requests

OLLAMA_URL = "http://localhost:11434/api/chat"


def generate_sql(question: str, model: str = "qwen2.5-coder:7b") -> str:
    ""