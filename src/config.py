from pathlib import Path


class Config:

    # === Base paths ===
    PROJECT_ROOT = Path(__file__).resolve().parent
    DATA_DIR = PROJECT_ROOT / "data"
    SAVED_ID_PATH = DATA_DIR / "saved_ids.csv"
    SAVED_DATA_PATH = DATA_DIR / "saved_data.txt"

    # === Vector DB ===
    VECTOR_PERSIST_DIRECTORY="/tmp/chroma_store"  # For normal scenario : "chroma_store"
    VECTOR_COLLECTION_NAME = "fashion_embeddings"

    # === Metadata ===
    METADATA_DIR = DATA_DIR / "metadata"
    STYLE_CSV = DATA_DIR / "styles.csv"
    IMAGE_CSV = DATA_DIR / "images.csv"

    # === Embedding ===
    EMBEDDING_MODEL_NAME = "BAAI/bge-base-en-v1.5"
    EMBEDDING_BATCH_SIZE = 20

    # === LLM ===
    LLM_MODEL_NAME = "llama-3.3-70b-versatile"   # "llama3-70b-8192"

    # === Result ===
    TOP_K = 20
    PER_CATEGORY_IMAGE = 4
    PAGINATION_IMAGE = 8

    # === Prompt path ===
    PROMPT_DIR = PROJECT_ROOT / "prompt"
    HTML_PROMPT = PROMPT_DIR / "html_prompt.txt"
    PARAGRAPH_PROMPT = PROMPT_DIR / "paragraph_prompt.txt"
    RERANK_PROMPT = PROMPT_DIR / "rerank_prompt.txt"
