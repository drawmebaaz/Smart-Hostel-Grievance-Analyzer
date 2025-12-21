# Smart Grievance Admin Frontend

> React-based admin dashboard for hostel complaint management with real-time monitoring, issue prioritization, and analytics.

**For complete system documentation, see the main [README.md](../README.md)**

## 🚀 Tech Stack

- **React 18** - Component-based UI framework
- **React Router v6** - Client-side routing
- **Axios** - HTTP client with interceptors
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Icon library
- **Recharts** - Data visualization
- **Vite** - Build tool

## 📁 Project Structure

```bash
src/
├── api/                                # API client configurations
│ └── dashboardApi.js                   # Axios clients with interceptors
├── components/                         # Reusable UI components
│ ├── BadgeComponents/                  # Status badges (Priority, Severity, etc.)
│ ├── cards/                            # Dashboard cards (StatCard, ResolvedIssues)
│ ├── charts/                           # Data visualization (HealthPieChart, SeverityBarChart)
│ ├── filters/                          # Excel-style filter component
│ ├── layout/                           # Layout components (Header)
│ ├── tables/                           # Data tables (IssueTable)
│ └── SkeletonLoaders.jsx               # Loading states
├── pages/                              # Page components
│ ├── Dashboard.jsx                     # Main dashboard page
│ └── IssueDetail.jsx                   # Issue detail page
├── utils/                              # Utilities
│ ├── formatters.js                     # Date/number formatting
│ └── colorMaps.js                      # Color schemes for badges/charts
├── App.jsx                             # Root app with routing
└── main.jsx                            # Entry point
```

## 🎨 UI Components

### 1. Dashboard Layout
- **Header**: Sticky header with refresh button and last updated timestamp
- **Stat Cards**: 4 key metrics with trends (Active Issues, Critical Issues, SLA Risk, Total Complaints)
- **Charts**: Health distribution pie chart + Severity bar chart
- **Priority Issues Table**: Main work queue with filtering and pagination
- **Resolved Issues Section**: Collapsible hostel-wise resolved issues

### 2. Issue Detail Page
- Complete issue lifecycle view
- Complaint timeline with duplicate detection
- Intelligence signals (Health, Severity, SLA, Priority scores)
- Status update functionality (OPEN, IN_PROGRESS, RESOLVED, REOPENED)

### 3. Reusable Components
- **BadgeComponents**: Color-coded badges for status, priority, severity, health, SLA
- **ExcelStyleFilters**: Advanced filtering with search and multi-select
- **SkeletonLoaders**: Progressive loading states

## 🔌 API Integration

### API Clients Configuration
```javascript
// dashboardApi.js - Main API client
const dashboardClient = axios.create({
  baseURL: '/admin/dashboard',
  timeout: 10000,
})

// issuesClient - Plain issue API
const issuesClient = axios.create({
  baseURL: '/issues',
  timeout: 10000,
})
```
### Available API Methods
```bash
// Get system health overview
dashboardApi.getHealth()
dashboardApi.getIssues(params = {})
dashboardApi.getSLATimers()
dashboardApi.getTrends(window = '24h')
dashboardApi.getIssueDetails(issueId)
issueApi.getIssue(issueId)
issueApi.updateStatus(issueId, status)
```

See main [README.md](../README.md) for complete API endpoint documentation.

## 🎯 Key Features

- ✅ Real-time dashboard with auto-refresh (30s)
- ✅ Advanced filtering (Priority, Severity, Health, Status)
- ✅ Interactive charts (Health pie, Severity bar)
- ✅ Pagination (20 items per page)
- ✅ Issue detail timeline view
- ✅ Status update modal (OPEN, IN_PROGRESS, RESOLVED, REOPENED)
- ✅ Resolved issues section (hostel-wise grouping)
- ✅ Error boundaries and graceful error handling

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start dev server (proxies to http://localhost:8000)
npm run dev

# Production build
npm run build
```

**Frontend:** http://localhost:3000  
**Backend API:** http://localhost:8000

## 🎨 Design

- **Theme:** Dark mode with cyan/emerald accents
- **Colors:** Semantic color coding for status, priority, severity
- **Responsive:** Desktop, tablet, and mobile layouts
- **Icons:** Lucide React icons throughout

## � Component Architecture

| Component | Purpose |
|-----------|---------|
| `Dashboard.jsx` | Main dashboard page with KPIs and charts |
| `IssueDetail.jsx` | Issue timeline and detail view |
| `IssueTable.jsx` | Priority issues table with pagination |
| `IssueTableFilters.jsx` | Multi-select filtering UI |
| `HealthPieChart.jsx` | Health distribution visualization |
| `SeverityBarChart.jsx` | Severity level distribution |
| `ResolvedIssuesSection.jsx` | Resolved issues summary by hostel |
| `BadgeComponents.jsx` | Color-coded status badges |
| `ErrorBoundary.jsx` | React error handling |

See [main README](../README.md) for complete architecture and API reference.
````

    Image optimization with SVGs