
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()


# ===================== FILE PATHS =====================
ROOT = Path(__file__).parent.parent
DOCS_DIR = ROOT / "docs"
URL_LOGS = ROOT / "URL_LOGS"
VECTOR_DIR = ROOT / "Vector_DB_Folder"


# ===================== INGESTION CONFIG VARIABLES =====================
# Downloading
LANGUAGE = "EN"
FILE_TYPE = "PDF"
CELEX_LIST = {
        "GDPR": "32016R0679",
        "DORA": "32022R2554",
        "Data Governance Act": "32022R0868",
        "Data Act": "32023R2854",
        "NIS2": "32022L2555",
        "AI Act": "32024R1689",
        "Open Data Directive": "32019L1024",
}
# Splitting
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
SEPARATORS = ["Article", r"\(\d+\)"]
# Embedding
COLLECTION_NAME = "pdf_rag_collection"
N_RESULTS = 5
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
FETCH_K = 20
LAMBDA_MULT = 0.6


# ===================== LLM CONFIG VARIABLES =====================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ONLINE_AI_ENDPOINT = os.getenv("ENDPOINT")
LOCAL_AI_MODEL= os.getenv("MODEL")

# something
TEMPERATURE = 0.5