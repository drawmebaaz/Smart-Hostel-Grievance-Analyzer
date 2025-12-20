# 🏫 AI-Powered Hostel Complaint & Issue Aggregation System

An intelligent backend system that **classifies, prioritizes, aggregates, and deduplicates hostel complaints** using NLP and semantic similarity.

Designed for **high precision, explainability, and predictable behavior**, this system converts raw complaints into **actionable issues** for administration.

---

## 🚀 Project Status

- ✅ Day 1–2: Text preprocessing & embeddings
- ✅ Day 3: Category classification (semantic anchors)
- ✅ Day 4: Urgency detection (4 levels)
- ✅ Day 5: Issue aggregation & duplicate detection (**stable**)

> **Current Scope:** English-only complaints (by design)

---

## 🎯 Core Capabilities

### 1️⃣ Complaint Classification
Each complaint is classified into:
- **Category** (Water, Electricity, Internet, Hygiene, Mess, Administration, etc.)
- **Urgency** (LOW, MEDIUM, HIGH, CRITICAL)
- **Expected response time**

Powered by **semantic anchor embeddings**, not keyword matching.

---

### 2️⃣ Issue Aggregation (Day 5)

Multiple complaints are intelligently grouped into a single **Issue** when:
- Hostel matches (hard rule)
- Category matches (hard rule)
- Semantic similarity is high enough

Each issue tracks:
- Total complaints
- Unique complaints
- Duplicate complaints
- Max & average urgency
- Last updated timestamp

---

### 3️⃣ Duplicate Detection (High Precision)

- Uses sentence embeddings + cosine similarity
- **Threshold: `0.88` (validated)**
- Duplicate ≠ Same issue  
  (A complaint can belong to the same issue but still be unique)

| Similarity Score | Meaning |
|------------------|--------|
| ≥ 0.88 | Strong duplicate |
| 0.70–0.87 | Same issue, different wording |
| < 0.70 | Related but unique |

---

## 🌐 Language Scope (Current Version)

### 🔤 English-Only Input (Intentional)

The system is **explicitly scoped to English** to guarantee reliable duplicate detection.

#### Why?
- Hinglish & multilingual text reduce embedding similarity (≈0.3–0.4)
- English-only ensures similarity > 0.6 for true semantic matches
- No silent translation errors
- Predictable aggregation behavior

---

### 🚫 What is rejected?
- Hindi (Devanagari) script
- Heavy Hinglish usage

#### Example (Rejected):
```json
❌ "Paani nahi aa raha BH-3 me"
```

#### Accepted:
```json
✅ "No water supply in BH-3 since morning"
```

---

## 🔍 English Scope Validation

Implemented via EnglishValidator:

- Rejects Hindi script
- Detects Hinglish patterns
- Requires minimum English content
- Allows hostel names & technical terms

### Future Roadmap

Includes:

- Explicit translation endpoint
- Hinglish normalization layer
- Multilingual routing

---

## 🧠 System Architecture (Simplified)

```
Complaint
   ↓
Language Validation
   ↓
Text Preprocessing
   ↓
Category Classification
   ↓
Urgency Detection
   ↓
Issue Aggregation
   ↓
Duplicate Detection
   ↓
Issue Statistics
```

---

---

## 📦 API Overview (Day 5)

### Submit Complaint

```
POST /complaints/
```

```json
{
  "text": "No water supply in BH-3 since morning",
  "hostel": "BH-3"
}
```

### Batch Submission

```
POST /complaints/batch
```

### System Stats

```
GET /issues/stats/system
```

### Scope Info

```
GET /scope
```

---

## 📊 Example System Statistics

```json
{
  "total_issues": 4,
  "total_complaints": 7,
  "unique_complaints": 5,
  "duplicate_rate": 0.28,
  "duplicate_threshold": 0.88,
  "consistency_checks": {
    "cross_hostel_attempts": 0,
    "cross_category_attempts": 0,
    "consistent": true
  }
}
```

---

## 🧪 Testing

All Day-5 functionality is covered by:

```bash
python scripts/test_day5.py
```

Includes:

- English scope validation
- Duplicate accuracy
- Issue aggregation
- Edge cases
- API health checks

---

## 🛠️ Tech Stack

- Python 3.10+
- FastAPI
- Sentence Transformers
- scikit-learn
- In-memory issue store (Day 5)
- Modular service architecture

---

## 📌 Design Philosophy

- Rules before ML
- Precision over recall
- Explainability > magic
- Deterministic behavior
- Production-safe defaults

---

## 🔮 Next Phase (Day 6)

- Issue lifecycle (open → resolved)
- Persistence layer (DB)
- Escalation rules
- SLA tracking