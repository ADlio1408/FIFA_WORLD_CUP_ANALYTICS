# ⚽ FIFA World Cup Analytics Platform
**Mahindra University — Software Engineering Project 2026**

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FULL STACK ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────┤
│  FRONTEND (HTML5 + CSS3 + Vanilla JS)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │login.html│ │dashboard │ │ matches  │ │   players    │  │
│  │          │ │  .html   │ │  .html   │ │   .html      │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │
│                      api.js (shared client)                  │
├─────────────────────────────────────────────────────────────┤
│  BACKEND (FastAPI + Python)     PORT: 8000                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  REST API Endpoints:                                 │   │
│  │  GET /api/kpis                  Dashboard KPIs       │   │
│  │  GET /api/tournaments           All tournaments      │   │
│  │  GET /api/matches?year=&stage=  Match explorer       │   │
│  │  GET /api/players/top?n=        Top scorers          │   │
│  │  GET /api/teams                 Country stats        │   │
│  │  GET /api/analytics/goals-trend Goal trends          │   │
│  │  GET /api/analytics/winners     Title breakdown      │   │
│  │  GET /api/search?q=             Global search        │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  IN-MEMORY CACHE (TTL: 5 min)    [Redis substitute]        │
│  ┌────────────────────────────────────────────────────┐    │
│  │  kpis_{year}  │  matches_{filters}  │  top_scorers │    │
│  └────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  DATABASE (SQLite with WAL mode)                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐   │
│  │ tournaments  │ │   matches    │ │     players      │   │
│  │ (22 rows)    │ │  (67+ rows)  │ │   (30 rows)      │   │
│  └──────────────┘ └──────────────┘ └──────────────────┘   │
│  ┌──────────────┐ ┌──────────────────────────────────┐    │
│  │    teams     │ │          kpi_cache               │    │
│  │  (20 rows)   │ │   (precomputed aggregates)       │    │
│  └──────────────┘ └──────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
fifa_analytics/
├── start.py                    ← ONE-CLICK STARTUP SCRIPT
├── README.md
├── backend/
│   ├── main.py                 ← FastAPI application (all API endpoints)
│   ├── seed_db.py              ← Database creation & seeding script
│   ├── requirements.txt        ← Python dependencies
│   └── fifa.db                 ← SQLite database (auto-created)
└── frontend/
    ├── api.js                  ← Shared API client (fetch wrapper)
    ├── dashboard.css           ← Main stylesheet (shared)
    ├── login.css               ← Login page styles
    ├── login.html              ← Login / entry page
    ├── dashboard.html          ← Main dashboard with KPIs & charts
    ├── matches.html            ← Match explorer with filters
    ├── players.html            ← Player stats & top scorers
    └── timeline.html           ← Historical tournament timeline
```

## Running the Project

### Option A: One-Click Start (Recommended)
```bash
python start.py
```

### Option B: Manual
```bash
# Step 1 — Install
cd backend
pip install fastapi uvicorn[standard] aiofiles

# Step 2 — Seed database
python seed_db.py

# Step 3 — Start server
uvicorn main:app --reload --port 8000

# Step 4 — Open frontend
open frontend/dashboard.html   # or double-click in Explorer
```

### Access Points
| URL | Description |
|-----|-------------|
| `http://localhost:8000` | API root |
| `http://localhost:8000/docs` | Swagger UI — interactive API docs |
| `http://localhost:8000/redoc` | ReDoc — beautiful API reference |
| `frontend/login.html` | Start here (open in browser) |

## API Endpoints — Deliverable 3

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/kpis` | Dashboard summary KPIs |
| GET | `/api/kpis?year=2022` | Year-specific KPIs |
| GET | `/api/tournaments` | All 22 tournaments |
| GET | `/api/tournaments/2022` | Single tournament detail |
| GET | `/api/matches` | All matches (filterable) |
| GET | `/api/matches?year=2022&stage=Final` | Filtered matches |
| GET | `/api/matches?team=Germany&min_goals=3` | High-scoring Germany games |
| GET | `/api/players` | All players |
| GET | `/api/players/top?n=10` | Top N goal scorers |
| GET | `/api/teams` | All team stats |
| GET | `/api/teams/Brazil` | Single team with history |
| GET | `/api/analytics/goals-trend` | Goals per tournament over time |
| GET | `/api/analytics/stage-breakdown` | Avg goals by stage |
| GET | `/api/analytics/country-performance` | Full team rankings |
| GET | `/api/analytics/highest-scoring?n=10` | Top N goal-fest matches |
| GET | `/api/analytics/winners-breakdown` | Title breakdown by country |
| GET | `/api/search?q=Germany` | Global search |
| GET | `/api/cache/stats` | Cache status |
| DELETE | `/api/cache/flush` | Flush cache |

## Database Schema — Deliverable 4

### tournaments
| Column | Type | Notes |
|--------|------|-------|
| year | INTEGER | Primary key (unique) |
| host | TEXT | Host country |
| winner | TEXT | Champion |
| teams | INTEGER | Teams participated |
| matches | INTEGER | Matches played |
| goals | INTEGER | Total goals |
| goals_per_match | REAL | **Computed column** |

### matches
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER | Auto-increment PK |
| year | INTEGER | FK → tournaments |
| stage | TEXT | Final/Semi/Quarter/R16/Group |
| team1, team2 | TEXT | Teams |
| score1, score2 | INTEGER | Goals |
| extra | TEXT | AET/Penalties |
| attendance | INTEGER | Stadium attendance |
| winner | TEXT | Match winner |
| total_goals | INTEGER | **Computed column** |

### Indexes
- `idx_matches_year` — fast year filtering
- `idx_matches_stage` — fast stage filtering
- `idx_matches_team1/2` — fast team search
- `idx_players_goals` — top scorer ranking
- `idx_teams_titles` — leaderboard sorting

## Caching Strategy — Deliverable 4

In-memory dict cache (Redis substitute for local deployment):
- **TTL**: 5 minutes per key
- **Key format**: `endpoint_param1_param2`
- **Endpoints with caching**: All `/api/*` endpoints
- **Cache flush**: `DELETE /api/cache/flush`

In production, replace with:
```python
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
r.setex(cache_key, CACHE_TTL, json.dumps(data))
```

## Deliverables Mapping

| Deliverable | Status | Location |
|-------------|--------|----------|
| D1: Cleaned Dataset + Validation | ✅ | `backend/seed_db.py` |
| D2: Analytics Tables + KPIs | ✅ | `/api/analytics/*` endpoints |
| D3: REST API + Documentation | ✅ | `backend/main.py` + `/docs` |
| D4: Database + Cache | ✅ | SQLite + in-memory cache |
| D5: Interactive Dashboards | ✅ | `frontend/*.html` |

## Team
Mahindra University — Software Engineering Course 2026
Team of 7 students
