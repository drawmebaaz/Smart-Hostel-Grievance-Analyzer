# Smart Hostel Grievance Analyzer

> A production-grade AI-powered system for hostel complaint management with intelligent issue aggregation, SLA tracking, and real-time admin dashboard.

**Status:** ✅ Production Ready | **Version:** 8.4.0 | **Last Updated:** December 2025

---

## 🎯 Project Overview

This system automates hostel grievance management through intelligent complaint classification, automatic issue aggregation, and real-time analytics. It handles the complete lifecycle from complaint submission to resolution with built-in intelligence for priority scoring, SLA risk detection, and health degradation monitoring.

### Key Features

- **Intelligent Classification:** Multi-category complaint classification with urgency detection (Low, Medium, High, Critical)
- **Automatic Aggregation:** Groups related complaints into issues by hostel + category
- **SLA Management:** Tracks SLA timers and breach predictions based on severity
- **Health Scoring:** Real-time issue health assessment (HEALTHY, MONITOR, WARNING, CRITICAL, EMERGENCY)
- **Priority Queue:** Issues sorted by priority, severity, and SLA risk
- **Admin Dashboard:** Real-time React UI with filtering, pagination, and intelligence signals
- **Observability:** Structured logging, metrics collection, and request tracing
- **Transaction Safety:** Row-locking and atomic operations for data consistency
- **Demo Mode:** Deterministic demo data seeding with realistic scenarios

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SMART GRIEVANCE SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FRONTEND (React + Vite) - Port 3000                     │  │
│  │  ├─ Dashboard (KPIs, Charts, Issue Table)               │  │
│  │  ├─ Issue Detail (Timeline, Complaints, Admin Actions)  │  │
│  │  ├─ Filters (Priority, Severity, Health, Status)        │  │
│  │  └─ Resolved Issues Section                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          ↑                                        │
│                       (HTTP)                                      │
│                          ↓                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API GATEWAY & ROUTING (FastAPI)                         │  │
│  │  ├─ CORS Middleware                                      │  │
│  │  ├─ Request Context (Tracing)                            │  │
│  │  └─ Error Handling                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          ↓                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API ROUTERS                                              │  │
│  │  ├─ /complaints       → Complaint submission & retrieval │  │
│  │  ├─ /issues           → Issue aggregation & details      │  │
│  │  ├─ /admin/dashboard  → Dashboard data & priority queue  │  │
│  │  ├─ /admin/*          → Admin operations (status update) │  │
│  │  ├─ /observability/*  → Metrics & health checks          │  │
│  │  ├─ /classify         → Classification endpoints         │  │
│  │  ├─ /analyze          → Complete analysis pipeline       │  │
│  │  └─ /embed            → Embedding endpoints              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          ↓                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SERVICE LAYER                                            │  │
│  │  ├─ IssueServiceDay7A → Core complaint processing        │  │
│  │  ├─ AdminQueueService → Priority queue building          │  │
│  │  ├─ ClassificationService → Category & urgency           │  │
│  │  ├─ EmbeddingService → Vector embeddings                 │  │
│  │  └─ HeuristicEngine → Pattern detection                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          ↓                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  INTELLIGENCE MODULES                                     │  │
│  │  ├─ Issue Health Scorer                                   │  │
│  │  ├─ Severity Engine                                       │  │
│  │  ├─ SLA Risk Engine                                       │  │
│  │  ├─ Priority Calculator                                   │  │
│  │  └─ Heuristic Pattern Detector                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          ↓                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  REPOSITORY LAYER (Data Access)                          │  │
│  │  ├─ IssueRepository                                       │  │
│  │  └─ ComplaintRepository                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          ↓                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DATABASE (PostgreSQL)                                    │  │
│  │  ├─ issues table (Unique: hostel + category)            │  │
│  │  └─ complaints table (FK → issues)                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  CROSS-CUTTING CONCERNS:                                         │
│  ├─ Structured Logging (with correlation IDs)                  │
│  ├─ Metrics Collection (counters, gauges, histograms)          │
│  ├─ Distributed Tracing                                         │
│  └─ Transaction Management (atomic, row-locking)               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📡 API Endpoints Reference

### Core Complaint Management

#### `POST /complaints/`
Submit a single complaint for processing.

**Request:**
```json
{
  "text": "Water supply problem in my room",
  "hostel": "Block A",
  "category": "Water/Sanitation"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "complaint_id": "COMP-abc123",
  "issue_id": "ISS-001",
  "status": "new_issue_created",
  "classification": {
    "category": "Water/Sanitation",
    "urgency": "High",
    "response_time_hours": 12
  },
  "issue_aggregation": {
    "complaint_count": 5,
    "unique_complaint_count": 4,
    "urgency_max": "High",
    "is_duplicate": false
  }
}
```

#### `POST /complaints/batch`
Submit multiple complaints in batch.

**Request:**
```json
{
  "complaints": [
    {"text": "...", "hostel": "Block A", "category": "Water/Sanitation"},
    {"text": "...", "hostel": "Block B", "category": "Electricity"}
  ]
}
```

**Response:** Array of complaint responses

---

### Issue Management

#### `GET /issues/`
List all issues with optional filtering and pagination.

**Query Parameters:**
- `limit` (int, default: 50, max: 200): Number of issues
- `include_complaints` (bool, default: false): Include full complaint details
- `category` (string, optional): Filter by category
- `hostel` (string, optional): Filter by hostel

**Response:**
```json
{
  "issues": [
    {
      "issue_id": "ISS-001",
      "hostel": "Block A",
      "category": "Water/Sanitation",
      "status": "OPEN",
      "complaint_count": 5,
      "unique_complaint_count": 4,
      "urgency_max": "High"
    }
  ],
  "count": 1
}
```

#### `GET /issues/{issue_id}`
Get detailed information about a specific issue.

**Response:**
```json
{
  "issue_id": "ISS-001",
  "hostel": "Block A",
  "category": "Water/Sanitation",
  "status": "OPEN",
  "created_at": "2025-12-01T10:00:00Z",
  "last_updated": "2025-12-22T15:30:00Z",
  "complaints": [
    {
      "complaint_id": "COMP-123",
      "text": "No water supply",
      "urgency": "High",
      "is_duplicate": false,
      "created_at": "2025-12-01T10:00:00Z"
    }
  ],
  "statistics": {
    "total_complaints": 5,
    "unique_complaints": 4,
    "duplicates": 1
  }
}
```

---

### Dashboard APIs (Admin UI)

#### `GET /admin/dashboard/priority-issues`
Get priority-sorted issue queue with intelligence signals.

**Query Parameters:**
- `limit` (int, default: 50, max: 200): Number of issues
- `status` (string, optional): Filter by status (OPEN, IN_PROGRESS, RESOLVED, REOPENED)

**Response:**
```json
{
  "generated_at": "2025-12-22T15:30:00Z",
  "count": 15,
  "issues": [
    {
      "issue_id": "ISS-001",
      "hostel": "Block A",
      "category": "Water/Sanitation",
      "status": "OPEN",
      "priority": {
        "score": 92.5,
        "label": "CRITICAL",
        "reason": "SLA at risk + health degrading"
      },
      "severity": {
        "severity": "SEV-1",
        "numeric": 4
      },
      "health": {
        "label": "CRITICAL",
        "score": 15
      },
      "sla": {
        "risk": "BREACHING",
        "time_remaining_minutes": -45
      },
      "complaint_count": 8
    }
  ]
}
```

#### `GET /admin/dashboard/health-summary`
Get system-wide health distribution (excludes RESOLVED issues).

**Response:**
```json
{
  "total_issues": 42,
  "health_distribution": {
    "HEALTHY": 15,
    "MONITOR": 12,
    "WARNING": 10,
    "CRITICAL": 5,
    "EMERGENCY": 0
  },
  "severity_distribution": {
    "SEV-1": 3,
    "SEV-2": 8,
    "SEV-3": 18,
    "SEV-4": 13
  },
  "sla_risk_distribution": {
    "OK": 30,
    "WARNING": 8,
    "BREACHING": 4
  }
}
```

#### `GET /admin/dashboard/sla-timers`
Get issues at SLA risk.

**Response:**
```json
{
  "breaching": [
    {
      "issue_id": "ISS-001",
      "hostel": "Block A",
      "category": "Water/Sanitation",
      "severity": "SEV-1",
      "minutes_overdue": 120
    }
  ],
  "warning": [
    {
      "issue_id": "ISS-002",
      "hostel": "Block B",
      "category": "Electricity",
      "severity": "SEV-2",
      "minutes_remaining": 45
    }
  ]
}
```

#### `GET /admin/dashboard/trends`
Get complaint and issue trends.

**Query Parameters:**
- `window` (string, default: "24h"): Time window (1h, 6h, 24h, 7d)

**Response:**
```json
{
  "window": "24h",
  "complaints": {
    "total": 145,
    "unique": 98,
    "duplicates": 47
  },
  "issues": {
    "created": 12,
    "updated": 28,
    "resolved": 5
  }
}
```

---

### Admin Operations

#### `PUT /admin/issues/{issue_id}/status`
Update issue status (admin action).

**Request:**
```json
{
  "status": "RESOLVED"
}
```

**Valid Statuses:** OPEN, IN_PROGRESS, RESOLVED, REOPENED

**Response:**
```json
{
  "issue_id": "ISS-001",
  "status": "RESOLVED",
  "updated_at": "2025-12-22T15:30:00Z"
}
```

#### `GET /admin/metrics`
Get system metrics and statistics.

**Response:**
```json
{
  "success": true,
  "metrics": {
    "counters": {
      "complaints_received_total": 1250,
      "issues_created_total": 280,
      "complaint_processed_total": 1200
    },
    "gauges": {
      "active_issues": 28,
      "sla_breaching": 6
    },
    "histograms": {
      "complaint_processing_duration_ms": {
        "min": 10,
        "max": 150,
        "avg": 45
      }
    }
  }
}
```

#### `POST /admin/metrics/reset`
Reset all metrics (development only).

⚠️ **WARNING:** Development-only endpoint. Clears all metrics.

---

### Classification & Analysis

#### `GET /categories`
List all available complaint categories.

**Response:**
```json
{
  "categories": [
    "Water/Sanitation",
    "Electricity",
    "Food Quality",
    "Maintenance",
    "Internet",
    "Security",
    "Cleanliness"
  ]
}
```

#### `POST /classify`
Classify a complaint text into a category.

**Request:**
```json
{
  "text": "Water supply problem in my room",
  "return_confidence": true
}
```

**Response:**
```json
{
  "category": "Water/Sanitation",
  "confidence": 0.95,
  "alternatives": [
    {"category": "Maintenance", "confidence": 0.03},
    {"category": "Cleanliness", "confidence": 0.02}
  ]
}
```

#### `POST /analyze`
Complete analysis pipeline: classification + urgency + embedding.

**Request:**
```json
{
  "text": "Water supply problem"
}
```

**Response:**
```json
{
  "text": "Water supply problem",
  "classification": {
    "category": "Water/Sanitation",
    "confidence": 0.95
  },
  "urgency": {
    "level": "High",
    "score": 3
  },
  "embedding": {
    "dimension": 384,
    "vector": [0.1, 0.2, ...]
  }
}
```

#### `POST /analyze/batch`
Batch analysis of multiple complaints.

**Request:**
```json
{
  "texts": [
    "Water supply problem",
    "Electricity not working"
  ]
}
```

**Response:** Array of analysis objects

---

### Health & Status

#### `GET /`
Root endpoint with service information.

**Response:**
```json
{
  "service": "Smart Hostel Grievance Analyzer",
  "version": "8.4.0",
  "status": "running",
  "endpoints": {
    "complaints": "/complaints",
    "issues": "/issues",
    "classify": "/classify",
    "analyze": "/analyze"
  }
}
```

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-22T15:30:00Z"
}
```

#### `GET /scope`
System scope and constraints.

**Response:**
```json
{
  "scope": "ENGLISH-ONLY",
  "languages": ["English"],
  "optimization": "English-optimized classification and urgency detection"
}
```

#### `GET /observability/health`
Health check with metrics.

**Response:**
```json
{
  "status": "healthy",
  "error_rate_percent": 2.1,
  "avg_latency_ms": 45.3,
  "total_requests": 5420,
  "uptime_seconds": 86400
}
```

#### `GET /observability/metrics`
Detailed metrics snapshot.

---

## 🛠️ Backend Technology Stack

### Core Framework
- **FastAPI** - Modern async Python web framework
- **SQLAlchemy** - ORM with transaction management
- **PostgreSQL** - Relational database with constraints

### AI & Processing
- **Sentence Transformers** - Embedding generation (384-dim vectors)
- **Scikit-learn** - Similarity computation
- **TextProcessing** - Text cleaning and normalization

### Observability
- **Structured Logging** - JSON logs with correlation IDs
- **Metrics Registry** - Counters, gauges, histograms
- **Distributed Tracing** - Request tracking across components

### Services Architecture
```
Services/
├── IssueServiceDay7A        → Core complaint processing pipeline
├── AdminQueueService        → Priority queue building
├── ClassificationService    → Text classification
├── EmbeddingService         → Vector embeddings
├── HeuristicEngine          → Pattern detection
└── SessionManager           → User session tracking

Intelligence/
├── IssueHealthScorer        → Health assessment
├── SeverityEngine           → Severity computation
├── SLARiskEngine            → SLA breach prediction
├── PriorityCalculator       → Priority scoring
└── Heuristics               → Follow-ups, escalations, noise

Repositories/
├── IssueRepository          → Issue CRUD + queries
└── ComplaintRepository      → Complaint CRUD + queries

Models/
├── IssueModel               → Issue database schema
└── ComplaintModel           → Complaint database schema
```

---

## 💻 Frontend Technology Stack

### Framework & Build
- **React 18** - UI library
- **Vite** - Lightning-fast build tool
- **React Router** - Client-side routing
- **TailwindCSS** - Utility-first CSS

### Charts & Visualization
- **Recharts** - React chart library
- **Lucide Icons** - Icon library

### State & API
- **Axios** - HTTP client with interceptors
- **React Hooks** - State management

### Components Structure
```
Components/
├── pages/
│   ├── Dashboard           → Main dashboard with KPIs & charts
│   └── IssueDetail         → Issue details with timeline
├── cards/
│   ├── StatCard            → KPI cards
│   └── ResolvedIssuesSection → Resolved issues summary
├── charts/
│   ├── HealthPieChart      → Health distribution
│   └── SeverityBarChart    → Severity distribution
├── tables/
│   ├── IssueTable          → Priority issues table (20 per page)
│   └── IssueTableFilters   → Multi-select filters
├── layout/
│   └── Header              → App header with refresh
└── utilities/
    ├── BadgeComponents     → Status/priority badges
    ├── SkeletonLoaders     → Loading states
    └── ErrorBoundary       → Error handling
```

---

## 🗄️ Database Schema

### Issues Table
```sql
CREATE TABLE issues (
  id VARCHAR PRIMARY KEY,
  hostel VARCHAR NOT NULL,
  category VARCHAR NOT NULL,
  status VARCHAR DEFAULT 'OPEN',
  
  urgency_max VARCHAR DEFAULT 'Low',
  urgency_avg FLOAT DEFAULT 1.0,
  
  complaint_count INT DEFAULT 0,
  unique_complaint_count INT DEFAULT 0,
  duplicate_count INT DEFAULT 0,
  
  created_at DATETIME NOT NULL,
  last_updated DATETIME NOT NULL,
  resolved_at DATETIME NULL,
  
  UNIQUE(hostel, category),
  CHECK(complaint_count >= 0),
  INDEX(status),
  INDEX(created_at),
  INDEX(hostel),
  INDEX(category)
)
```

### Complaints Table
```sql
CREATE TABLE complaints (
  id VARCHAR PRIMARY KEY,
  issue_id VARCHAR FOREIGN KEY REFERENCES issues(id),
  text TEXT NOT NULL,
  category VARCHAR NOT NULL,
  urgency VARCHAR NOT NULL,
  hostel VARCHAR NOT NULL,
  
  is_duplicate BOOLEAN DEFAULT FALSE,
  similarity_score FLOAT NULL,
  embedding VECTOR(384) NULL,
  
  created_at DATETIME NOT NULL,
  INDEX(issue_id),
  INDEX(created_at),
  INDEX(is_duplicate)
)
```

---

## 🚀 Quick Start

### Backend Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with database credentials
   ```

3. **Initialize database:**
   ```bash
   python scripts/init_db.py
   ```

4. **Seed demo data (optional):**
   ```bash
   python scripts/seed_demo_data.py --demo
   ```

5. **Start backend server:**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

**Backend running at:** `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend:**
   ```bash
   cd admin-ui
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

**Frontend running at:** `http://localhost:3000`

### Access Points

- **Admin Dashboard:** http://localhost:3000/dashboard
- **API Docs:** http://localhost:8000/docs (Swagger UI)
- **API Schema:** http://localhost:8000/openapi.json

---

## 📊 Key Intelligence Features

### 1. Issue Health Scoring
Computes health from complaint velocity and status:
- **HEALTHY** (score > 70): Stable, under control
- **MONITOR** (score 50-70): Watching closely
- **WARNING** (score 25-50): Degrading, needs attention
- **CRITICAL** (score 10-25): Serious, urgent action needed
- **EMERGENCY** (score < 10): Emergency state, immediate escalation

### 2. Severity Classification
Based on category and complaint characteristics:
- **SEV-1** (Highest): Critical infrastructure impact
- **SEV-2**: Significant impact on daily life
- **SEV-3**: Moderate impact
- **SEV-4** (Lowest): Minor/cosmetic issues

### 3. SLA Risk Assessment
Predicts SLA breaches based on severity and age:
- **OK**: Within SLA
- **WARNING**: < 2 hours remaining
- **BREACHING**: SLA violated

### 4. Priority Scoring
Multi-factor priority calculation:
- Health degradation (40% weight)
- SLA risk (35% weight)
- Severity level (15% weight)
- Recency (10% weight)

### 5. Duplicate Detection
Groups similar complaints automatically:
- Uses embedding similarity (cosine distance)
- Threshold: > 0.88 similarity
- Prevents duplicate work

### 6. Heuristic Pattern Detection
Identifies common patterns:
- **Follow-ups:** Same hostel + category within 24h
- **Escalations:** Severity increase on same issue
- **Noise:** Repetitive trivial complaints

---

## 📈 System Statistics

View comprehensive system statistics:

```bash
curl http://localhost:8000/issues/stats/system
```

Returns:
- Total complaints received
- Unique vs duplicate count
- Issues created
- Category distribution
- Average processing latency
- Error rates
- System uptime

---

## 🔍 Observability

### Structured Logging
All operations logged with correlation IDs for request tracing:
```json
{
  "timestamp": "2025-12-22T15:30:00Z",
  "request_id": "req-abc123",
  "level": "INFO",
  "message": "complaint_processed_successfully",
  "complaint_id": "COMP-123",
  "issue_id": "ISS-001",
  "duration_ms": 45.2
}
```

### Metrics Collection
Real-time metrics exposed via `/observability/metrics`:
- Request counts by endpoint
- Latency histograms (min, max, avg, p95, p99)
- Error rates by type
- System resource usage

### Health Checks
- `/health` - Simple health check
- `/observability/health` - Health with metrics
- `/scope` - System constraints

---

## 🧪 Testing

### Run unit tests:
```bash
pytest scripts/test_*.py -v
```

### Run specific test:
```bash
pytest scripts/test_day5.py::test_api_endpoints -v
```

### Manual API testing (via curl):
```bash
# Submit complaint
curl -X POST http://localhost:8000/complaints/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Water problem", "hostel": "Block A", "category": "Water/Sanitation"}'

# Get issues
curl http://localhost:8000/issues/

# Get dashboard data
curl http://localhost:8000/admin/dashboard/priority-issues?limit=20

# Get metrics
curl http://localhost:8000/observability/metrics
```

---

## 🔐 Security Considerations

- ✅ **Transaction Isolation:** Row-locking prevents race conditions
- ✅ **Input Validation:** Pydantic schemas enforce request structure
- ✅ **Error Handling:** No sensitive data in error responses
- ✅ **CORS Enabled:** Configured for development (restrict in production)
- ✅ **SQL Injection Prevention:** SQLAlchemy parameterized queries
- ⚠️ **Note:** No authentication implemented (add in production)

---

## 📝 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/grievance_db

# Service
SERVICE_NAME="Smart Hostel Grievance Analyzer"
SERVICE_VERSION="8.4.0"
API_PORT=8000
ENV=development  # development | production

# Logging
LOG_LEVEL=INFO

# Observability
ENABLE_METRICS=true
ENABLE_TRACING=true
```

---

## 🚨 Common Issues & Solutions

### Issue: "Database connection failed"
**Solution:** Ensure PostgreSQL is running and DATABASE_URL is correct.

### Issue: "Port 8000 already in use"
**Solution:** Use different port: `uvicorn app.main:app --port 8001`

### Issue: "Frontend can't reach backend"
**Solution:** Check vite.config.js proxy settings point to correct backend URL.

### Issue: "Charts not rendering"
**Solution:** Ensure active issues count > 0. Resolved issues are excluded from health/severity charts.

---

## 📚 Additional Resources

### Code Organization
- `app/main.py` - FastAPI application entry point
- `app/api/` - API routers (complaints, issues, dashboard, admin)
- `app/services/` - Business logic (issue service, classification, embedding)
- `app/intelligence/` - Scoring engines (health, severity, SLA, priority)
- `app/db/` - Database models and repositories
- `app/observability/` - Logging, metrics, tracing
- `scripts/` - Utility scripts (seeding, testing, migration)

### Frontend Organization
- `admin-ui/src/pages/` - Page components (Dashboard, IssueDetail)
- `admin-ui/src/components/` - Reusable components
- `admin-ui/src/api/` - API client (dashboardApi.js)
- `admin-ui/src/utils/` - Utilities (color maps, helpers)

---

## 🎓 Design Patterns & Principles

### Backend Patterns
- **Repository Pattern** → Abstracted data access
- **Service Layer** → Business logic separation
- **Transaction Management** → Atomic operations with row-locking
- **Graceful Degradation** → Continue on non-critical failures (embeddings, heuristics)
- **Observability First** → All operations instrumented with logs/metrics/traces

### Frontend Patterns
- **Component Composition** → Reusable, testable components
- **API Abstraction** → Centralized axios client with interceptors
- **Error Boundaries** → Graceful error handling UI
- **Skeleton Loaders** → Better perceived performance
- **Client-side Pagination** → 20 issues per page with Previous/Next

---

## 🤝 Contributing

When adding features:
1. Maintain service/repository separation
2. Add structured logging with correlation IDs
3. Instrument metrics for observability
4. Include transaction safety for DB operations
5. Write tests for critical paths

---

## 🙋 Support

For issues, questions, or contributions, refer to the codebase structure and architectural documentation above. All API endpoints are self-documented in the `/docs` Swagger UI.

**Generated:** December 2025 | **Status:** Production Ready ✅
