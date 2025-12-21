# 🏫 AI-Powered Hostel Complaint & Issue Aggregation System

An intelligent backend system that **classifies, prioritizes, aggregates, and deduplicates hostel complaints** using NLP and semantic similarity.

Designed for **high precision, explainability, and predictable behavior**, this system converts raw complaints into **actionable issues** for administration.

---

## 🚀 Project Status

- ✅ Day 1–2: Text preprocessing & embeddings
- ✅ Day 3: Category classification (semantic anchors)
- ✅ Day 4: Urgency detection (4 levels)
- ✅ Day 5: Issue aggregation & duplicate detection (**stable**)
- ✅ Day 6: Persistence & enhanced intelligence (**production-ready**)

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

# 🎯 Day 6 - Persistence & Enhanced Intelligence

## What's New in Day 6

Day 6 adds **production-ready persistence** and **session-aware intelligence** to the complaint system.

### Key Features

1. **Database Persistence (SQLite + SQLAlchemy)**
   - Complaints stored permanently
   - Issues tracked across sessions
   - Full audit trail

2. **Issue Lifecycle Management**
   - Status transitions: OPEN → IN_PROGRESS → RESOLVED → REOPENED
   - Admin controls
   - Timestamp tracking

3. **Session Management**
   - Anonymous user sessions (no auth required)
   - Session-based complaint tracking
   - Automatic expiry (30 minutes)
   - Rate limiting (10 complaints/session)

4. **Heuristic Intelligence**
   - **Follow-up detection**: Same user, same issue
   - **Escalation detection**: Urgency increases
   - **Noise detection**: Rapid repetitive submissions

5. **System Metrics**
   - Complaint statistics
   - Session statistics
   - Heuristic triggers
   - Performance metrics
   - Error tracking

---

## 📁 New File Structure

```
app/
├── core/                      # Day 6 core logic
│   ├── session.py            # Session management
│   └── heuristics.py         # Heuristic engine
├── db/                        # Database layer
│   ├── base.py               # SQLAlchemy base
│   ├── session.py            # DB session management
│   └── models/
│       ├── issue.py          # Issue model
│       └── complaint.py      # Complaint model
├── repositories/              # Data access layer
│   ├── issue_repository.py
│   └── complaint_repository.py
├── services/
│   └── issue_service_day6.py # Enhanced service
├── api/
│   └── admin.py              # Admin endpoints
├── metrics/
│   └── system_metrics.py     # Metrics collector
└── config/
    └── constants.py          # System constants

scripts/
├── init_db.py                # Database initialization
└── test_day6.py              # Day 6 tests
```

---

## � Setup & Installation

### 1. Install Dependencies

```bash
pip install -r requirements_day6.txt
```

### 2. Initialize Database

```bash
python scripts/init_db.py
```

This creates `data/hostel_grievance.db` with the required tables.

### 3. Run Tests

```bash
python scripts/test_day6.py
```

### 4. Start Server

```bash
python -m app.main
```

---

## 📊 Database Schema

### Issues Table

```sql
CREATE TABLE issues (
    id VARCHAR PRIMARY KEY,
    hostel VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    urgency_max VARCHAR NOT NULL,
    urgency_avg FLOAT NOT NULL,
    complaint_count INTEGER NOT NULL,
    unique_complaint_count INTEGER NOT NULL,
    duplicate_count INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    last_updated DATETIME NOT NULL,
    resolved_at DATETIME
);
```

### Complaints Table

```sql
CREATE TABLE complaints (
    id VARCHAR PRIMARY KEY,
    issue_id VARCHAR NOT NULL,
    text TEXT NOT NULL,
    category VARCHAR NOT NULL,
    urgency VARCHAR NOT NULL,
    hostel VARCHAR NOT NULL,
    similarity_score FLOAT,
    is_duplicate BOOLEAN NOT NULL,
    duplicate_of VARCHAR,
    session_id VARCHAR,
    metadata JSON,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (issue_id) REFERENCES issues(id)
);
```

---

## 🔌 API Changes

### New Endpoints

#### Admin Endpoints

```
PUT /admin/issues/{issue_id}/status
GET /admin/issues/by-status/{status}
GET /admin/metrics
POST /admin/metrics/reset
```

### Enhanced Complaint Submission

```json
POST /complaints/
{
  "text": "No water in BH-3",
  "hostel": "BH-3",
  "session_id": "SES-abc123"
}
```

**Response includes:**

```json
{
  "success": true,
  "complaint_id": "COMP-xyz789",
  "issue_aggregation": {
    "issue_id": "ISSUE-bh_3-water-abc",
    "is_duplicate": false,
    "complaint_count": 5
  },
  "session": {
    "session_id": "SES-abc123",
    "complaints_in_session": 2
  },
  "heuristics": {
    "is_follow_up": true,
    "is_escalation": false,
    "possible_noise": false,
    "details": {}
  }
}
```

---

## 🧠 Heuristics Engine

### Follow-up Detection

Detects when a user submits multiple complaints about the same issue.

**Conditions:**
- Same session
- Same issue_id
- Not a duplicate

### Escalation Detection

Detects when urgency increases for the same issue.

**Conditions:**
- Same session
- Same issue_id
- Current urgency > previous max urgency

### Noise Detection

Flags potentially low-value repetition.

**Conditions:**
- 4+ complaints in session
- Avg time between complaints < 30 seconds
- Avg similarity > 0.85

---

## 🎛️ Configuration

All tunable parameters are in `app/config/constants.py`:

```python
# Session
SESSION_TTL_SECONDS = 30 * 60
MAX_SESSION_COMPLAINTS = 10

# Heuristics
MIN_COMPLAINTS_FOR_NOISE = 4
MAX_AVG_TIME_DELTA_SEC = 30
MIN_AVG_SIMILARITY = 0.85

# Duplicate Detection
DUPLICATE_SIMILARITY_THRESHOLD = 0.88
```

---

## 📈 Metrics

Access system metrics:

```
GET /admin/metrics
```

Returns:

```json
{
  "complaints": {
    "total": 150,
    "success": 145,
    "rejected": 3,
    "failed": 2
  },
  "duplicates": {
    "detected": 45,
    "unique": 105
  },
  "heuristics": {
    "follow_ups": 12,
    "escalations": 3,
    "noise_flags": 1
  },
  "performance": {
    "avg_processing_time_ms": 245.3
  }
}
```

---

## 🔒 Data Persistence

### Session Storage

- **In-memory** (current implementation)
- Easy to swap with Redis later
- Auto-cleanup of expired sessions

### Database Storage

- **SQLite** for simplicity
- Can switch to PostgreSQL by changing `DATABASE_URL`
- All operations use SQLAlchemy ORM

---

## 🧪 Testing

### Test Session Management

```python
from app.core.session import get_session_manager

sm = get_session_manager()
session = sm.create_session()
assert session is not None
```

### Test Heuristics

```python
from app.core.heuristics import HeuristicEngine

result = HeuristicEngine.evaluate(
    session=session,
    current_issue_id="ISSUE-123",
    current_urgency="High",
    is_duplicate=False,
    similarity_score=0.75,
    timestamp=datetime.now()
)

assert "is_follow_up" in result
```

---

## 🔄 Migration from Day 5

Your Day 5 code **still works**. Day 6 adds:

- `get_issue_service_day6()` - enhanced version
- Original `get_issue_service()` - unchanged

To use Day 6 features:

```python
# Old (Day 5)
from app.services.issue_service import get_issue_service

# New (Day 6)
from app.services.issue_service_day6 import get_issue_service_day6
```

---

## 📊 System Statistics

```
GET /issues/stats/system
```

Now includes:

```json
{
  "day_6_complete": true,
  "issue_system": {
    "total_issues": 42,
    "status_distribution": {
      "OPEN": 25,
      "IN_PROGRESS": 10,
      "RESOLVED": 7
    }
  },
  "session_system": {
    "active_sessions": 8,
    "total_complaints_tracked": 156
  }
}
```

---

## 🎯 What Day 6 Achieves

✅ **Durability**: Complaints survive server restarts
✅ **Intelligence**: Detects follow-ups and escalations
✅ **Observability**: Comprehensive metrics
✅ **Admin Control**: Issue lifecycle management
✅ **Production-Ready**: Clean architecture, testable code

---

## 🔮 Next Steps (Day 7+)

Potential enhancements:

- **Authentication**: User accounts
- **Notifications**: Email/SMS for escalations
- **Dashboard**: Admin web UI
- **Analytics**: Trend detection
- **SLA Tracking**: Response time monitoring

---

## 📝 Notes

- Database file: `data/hostel_grievance.db`
- Sessions expire after 30 minutes
- Heuristics are **descriptive, not prescriptive** (they flag, not block)
- All metrics are **thread-safe**

---

## 🆘 Troubleshooting

### Database Locked

```bash
# Kill any running processes
# Delete database and recreate
rm data/hostel_grievance.db
python scripts/init_db.py
```

### Session Not Found

Sessions auto-expire. Client should create new session if retrieval fails.

### Heuristics Not Triggering

Check:
- Session has multiple entries
- Same issue_id
- Timing and similarity thresholds

---