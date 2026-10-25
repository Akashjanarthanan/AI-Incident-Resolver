import os

from dotenv import load_dotenv


load_dotenv()


OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:3b"
)

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://127.0.0.1:11434"
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)

RERANKER_MODEL = os.getenv(
    "RERANKER_MODEL",
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

MAX_CONVERSATION_MESSAGES = int(
    os.getenv(
        "MAX_CONVERSATION_MESSAGES",
        "10"
    )
)

TOP_PREVIOUS_INCIDENTS = int(
    os.getenv(
        "TOP_PREVIOUS_INCIDENTS",
        "3"
    )
)