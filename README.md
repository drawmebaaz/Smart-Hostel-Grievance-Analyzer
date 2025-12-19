# Smart Hostel Grievance Analyzer — Day 2
## Multilingual Text Processing & Embedding Service

## 📌 Purpose

This service forms the AI foundation of the Smart Hostel Grievance Analyzer. Its responsibility is to convert hostel complaints written in English, Hindi, and Hinglish into a shared semantic vector representation, which is later used for classification, similarity detection, and trend analysis.

## 🧠 Key Design Decisions

### 1. No Translation-Based Pipeline
- Complaints are **not** translated to a single language
- Translation introduces semantic drift and fails for Hinglish
- Instead, multilingual embeddings are used to preserve meaning

### 2. Multilingual Semantic Embeddings
- All complaints are mapped into a single vector space
- Complaints with similar meaning lie close together, regardless of language

**Example:**
- `"No water supply in hostel"`
- `"Paani nahi aa raha hostel me"`

→ produce nearby embeddings.

### 3. Minimal & Controlled Preprocessing
Preprocessing is intentionally lightweight:
- Lowercasing
- Whitespace normalization
- Small Hinglish normalization dictionary

Aggressive NLP steps (stemming, stopwords, grammar correction) are avoided to preserve meaning in code-mixed text.

## 📁 Project Structure
```bash
ai-service/
│
├── app/
│   ├── main.py                # FastAPI entry point
│   ├── config.py              # Model & service config
│   │
│   ├── preprocessing/
│   │   └── text_cleaner.py    # Text normalization logic
│   │
│   ├── embeddings/
│   │   └── embedder.py        # Multilingual embedding model
│   │
│   ├── services/
│   │   └── embedding_service.py
│   │
│   └── utils/
│       └── logger.py
│
├── scripts/
│   └── generate_embeddings.py # Batch embedding generator
│
├── data/                      # Dataset folder (create this)
│   └── hostel_complaints_multilingual_v1.csv
│
├── requirements.txt
└── README.md
```

## ⚙️ Setup Instructions

### 1. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Prepare dataset
```bash
# Create data folder and place your CSV there
mkdir data
# Copy your dataset to: ai-service/data/hostel_complaints_multilingual_v1.csv
```

## ▶️ Running Day 2 Pipeline

### Option A: Batch Processing (Recommended)
```bash
python scripts/generate_embeddings.py
```

### Option B: Start API Service
```bash
python -m app.main
```

## Output

After running the batch script, a new file is created:

```bash
data/hostel_complaints_with_embeddings.csv
```

Each complaint now contains a semantic embedding vector (512 dimensions).

## 🔧 API Usage

Note: API endpoints are provided for early integration testing. Core Day 2 validation is done via batch embedding.

Once the service is running, you can generate embeddings via HTTP:

### Single Text Embedding
```bash
curl -X POST "http://localhost:8000/embed" \
  -H "Content-Type: application/json" \
  -d '{"text": "No water supply in hostel", "normalize_hinglish": true}'
```

### Batch Embedding
```bash
curl -X POST "http://localhost:8000/embed/batch" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["No water supply", "Paani nahi aa raha"], "batch_size": 32}'
```

### Check Service Health
```bash
curl http://localhost:8000/health
```

## 🚀 Features

    Multilingual Support: Handle English, Hindi, and Hinglish text seamlessly

    Semantic Preservation: Maintain original meaning across languages

    Scalable: Batch processing for large datasets

    Lightweight: Minimal preprocessing for fast operation

    API-Ready: REST endpoints for integration with Node.js backend

## 📊 Model Details

    Current Model: sentence-transformers/distiluse-base-multilingual-cased-v2

    Chosen for stronger multilingual robustness over lighter MiniLM.

    Embedding Dimension: 512-dimensional vectors

    Language Support: 50+ languages including Hindi-English code-mixing

    Alternative Models (configurable):

        paraphrase-multilingual-MiniLM-L12-v2 (384-dim, lighter)

        l3cube-pune/hindi-sentence-similarity-sbert (Hindi-focused)
