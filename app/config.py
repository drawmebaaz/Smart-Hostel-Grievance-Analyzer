import os
from dotenv import load_dotenv

load_dotenv()

# Embedding Model Configuration
# Using a better model for Indic languages and Hinglish support[citation:2][citation:3]
EMBEDDING_MODEL_NAME = "sentence-transformers/distiluse-base-multilingual-cased-v2"
# Alternatives to consider:
# - "paraphrase-multilingual-MiniLM-L12-v2" (lighter, 384-dim)
# - "l3cube-pune/hindi-sentence-similarity-sbert" (Hindi-focused, 768-dim)[citation:2]
# - "paraphrase-multilingual-mpnet-base-v2" (heavier but more accurate)[citation:3]

# Service Configuration
SERVICE_NAME = "hostel-grievance-ai"
SERVICE_VERSION = "0.2.0"
API_PORT = int(os.getenv("API_PORT", "8000"))

# File Paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
INPUT_CSV = os.path.join(DATA_DIR, "hostel_complaints_multilingual_v1.csv")
OUTPUT_CSV = os.path.join(DATA_DIR, "hostel_complaints_with_embeddings.csv")