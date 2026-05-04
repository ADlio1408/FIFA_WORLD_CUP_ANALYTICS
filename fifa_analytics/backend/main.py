"""
FIFA World Cup Analytics Platform — FastAPI Backend
Deliverable 3: REST API Endpoints & Documentation
Deliverable 4: Database Schema & Cache Implementation

Run: uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import sqlite3
import json
import os
import time
from typing import Optional
from contextlib import contextmanager
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DB_PATH    = os.path.join(BASE_DIR, "fifa.db")
FRONTEND   = os.path.join(BASE_DIR, "..", "frontend")

# In-memory cache (Redis substitute for local deployment)
_cache: dict = {}
CACHE_TTL = 300  # 5 minutes

# ── APP ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="FIFA World Cup Analytics API",
    description="""
## FIFA World Cup Analytics Platform
**Mahindra University — Software Engineering Project 2026**

### Available Endpoints
- `/api/kpis` — Dashboard KPIs
- `/api/tournaments` — All tournaments
- `/api/matches` — Match explorer with filters
- `/api/players` — Player stats & top scorers
- `/api/teams` — Team performance stats
- `/api/analytics` — Advanced analytics & trends
- `/api/search` — Global search

### Caching
All endpoints use in-memory caching (TTL: 5 min) to minimize DB calls.
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ── DATABASE ──────────────────────────────────────────────────────────────────
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
    finally:
        conn.close()

def rows_to_list(rows) -> list:
    return [dict(r) for r in rows]

# ── CACHE ─────────────────────────────────────────────────────────────────────
def cache_get(key: str):
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < CACHE_TTL:
        return entry["data"]
    return None

def cache_set(key: str, data):
    _cache[key] = {"data": data, "ts": time.time()}
    return data

# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
def root():
    return {"message": "FIFA Analytics API", "docs": "/docs", "version": "1.0.0"}


# ── KPIs ──────────────────────────────────────────────────────────────────────
@app.get("/api/kpis", tags=["Dashboard"], summary="Dashboard KPI summary")
def get_kpis(year: Optional[int] = Query(None, description="Filter by year")):
    cache_key = f"kpis_{year}"
    if cached := cache_get(cache_key):
        return cached

    with get_db() as db:
        if year:
            t = db.execute("SELECT * FROM tournaments WHERE year=?", (year,)).fetchone()
            if not t:
                raise HTTPException(404, f"Tournament {year} not found")
            result = {
                "year": year,
                "host": t["host"],
                "winner": t["winner"],
                "teams": t["teams"],
                "matches": t["matches"],
                "goals": t["goals"],
                "goals_per_match": t["goals_per_match"],
                "notes": t["notes"],
            }
        else:
            totals = db.execute("""
                SELECT COUNT(*) AS tournaments,
                       SUM(matches) AS total_matches,
                       SUM(goals)   AS total_goals,
                       ROUND(AVG(goals_per_match),2) AS avg_goals_per_match
                FROM tournaments
            """).fetchone()
            nations = db.execute("SELECT COUNT(*) AS n FROM teams").fetchone()
            top_scorer = db.execute(
                "SELECT name, country, goals FROM players ORDER BY goals DESC LIMIT 1"
            ).fetchone()
            result = {
                "tournaments": totals["tournaments"],
                "total_matches": totals["total_matches"],
                "total_goals": totals["total_goals"],
                "avg_goals_per_match": totals["avg_goals_per_match"],
                "nations": nations["n"],
                "top_scorer": dict(top_scorer) if top_scorer else None,
                "cached_at": datetime.now().isoformat(),
            }

    return cache_set(cache_key, result)


# ── TOURNAMENTS ───────────────────────────────────────────────────────────────
@app.get("/api/tournaments", tags=["Tournaments"], summary="All World Cup tournaments")
def get_tournaments(
    limit: int = Query(50, ge=1, le=50),
    offset: int = Query(0, ge=0),
    order: str = Query("desc", pattern="^(asc|desc)$"),
):
    cache_key = f"tournaments_{limit}_{offset}_{order}"
    if cached := cache_get(cache_key):
        return cached

    with get_db() as db:
        direction = "DESC" if order == "desc" else "ASC"
        rows = db.execute(f"""
            SELECT t.*,
                   COUNT(m.id) AS db_match_count
            FROM tournaments t
            LEFT JOIN matches m ON m.year = t.year
            GROUP BY t.year
            ORDER BY t.year {direction}
            LIMIT ? OFFSET ?
        """, (limit, offset)).fetchall()
        total = db.execute("SELECT COUNT(*) FROM tournaments").fetchone()[0]

    result = {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": rows_to_list(rows),
    }
    return cache_set(cache_key, result)


@app.get("/api/tournaments/{year}", tags=["Tournaments"])
def get_tournament(year: int):
    cache_key = f"tournament_{year}"
    if cached := cache_get(cache_key):
        return cached

    with get_db() as db:
        t = db.execute("SELECT * FROM tournaments WHERE year=?", (year,)).fetchone()
        if not t:
            raise HTTPException(404, f"Tournament {year} not found")
        finals = db.execute(
            "SELECT * FROM matches WHERE year=? AND stage='Final'", (year,)
        ).fetchall()
    result = {**dict(t), "finals": rows_to_list(finals)}
    return cache_set(cache_key, result)


# ── MATCHES ───────────────────────────────────────────────────────────────────
@app.get("/api/matches", tags=["Matches"], summary="Match explorer with filters")
def get_matches(
    year: Optional[int] = None,
    stage: Optional[str] = None,
    team: Optional[str] = Query(None, description="Search team name (partial match)"),
    min_goals: Optional[int] = Query(None, ge=0),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    order_by: str = Query("year", pattern="^(year|total_goals|attendance)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
):
    cache_key = f"matches_{year}_{stage}_{team}_{min_goals}_{limit}_{offset}_{order_by}_{order}"
    if cached := cache_get(cache_key):
        return cached

    conditions = []
    params: list = []

    if year:
        conditions.append("year = ?"); params.append(year)
    if stage:
        conditions.append("stage = ?"); params.append(stage)
    if team:
        conditions.append("(team1 LIKE ? OR team2 LIKE ?)"); params += [f"%{team}%", f"%{team}%"]
    if min_goals is not None:
        conditions.append("total_goals >= ?"); params.append(min_goals)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    direction = "DESC" if order == "desc" else "ASC"

    with get_db() as db:
        total = db.execute(f"SELECT COUNT(*) FROM matches {where}", params).fetchone()[0]
        rows = db.execute(f"""
            SELECT * FROM matches {where}
            ORDER BY {order_by} {direction}
            LIMIT ? OFFSET ?
        """, params + [limit, offset]).fetchall()

        goals_stats = db.execute(f"""
            SELECT SUM(total_goals) AS total_goals,
                   ROUND(AVG(total_goals),2) AS avg_goals,
                   MAX(total_goals) AS max_goals
            FROM matches {where}
        """, params).fetchone()

    result = {
        "total": total,
        "limit": limit,
        "offset": offset,
        "stats": dict(goals_stats),
        "data": rows_to_list(rows),
    }
    return cache_set(cache_key, result)


@app.get("/api/matches/{match_id}", tags=["Matches"])
def get_match(match_id: int):
    with get_db() as db:
        row = db.execute("SELECT * FROM matches WHERE id=?", (match_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Match not found")
    return dict(row)


# ── PLAYERS ───────────────────────────────────────────────────────────────────
@app.get("/api/players", tags=["Players"], summary="Player stats & rankings")
def get_players(
    position: Optional[str] = None,
    country: Optional[str] = None,
    min_goals: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    cache_key = f"players_{position}_{country}_{min_goals}_{limit}_{offset}"
    if cached := cache_get(cache_key):
        return cached

    conditions = ["goals >= ?"]
    params: list = [min_goals]
    if position:
        conditions.append("position = ?"); params.append(position)
    if country:
        conditions.append("country LIKE ?"); params.append(f"%{country}%")

    where = "WHERE " + " AND ".join(conditions)

    with get_db() as db:
        total = db.execute(f"SELECT COUNT(*) FROM players {where}", params).fetchone()[0]
        rows = db.execute(f"""
            SELECT *, RANK() OVER (ORDER BY goals DESC) AS rank
            FROM players {where}
            ORDER BY goals DESC
            LIMIT ? OFFSET ?
        """, params + [limit, offset]).fetchall()

    result = {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": rows_to_list(rows),
    }
    return cache_set(cache_key, result)


@app.get("/api/players/top", tags=["Players"], summary="Top N goal scorers")
def get_top_scorers(n: int = Query(10, ge=1, le=30)):
    cache_key = f"top_scorers_{n}"
    if cached := cache_get(cache_key):
        return cached

    with get_db() as db:
        rows = db.execute("""
            SELECT name, country, flag, goals, tournaments, matches, goals_per_match,
                   RANK() OVER (ORDER BY goals DESC) AS rank
            FROM players ORDER BY goals DESC LIMIT ?
        """, (n,)).fetchall()

    return cache_set(cache_key, rows_to_list(rows))


# ── TEAMS ─────────────────────────────────────────────────────────────────────
@app.get("/api/teams", tags=["Teams"], summary="All team performance stats")
def get_teams(
    sort_by: str = Query("titles", pattern="^(titles|wins|goals_scored|appearances|win_rate)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(20, ge=1, le=50),
):
    cache_key = f"teams_{sort_by}_{order}_{limit}"
    if cached := cache_get(cache_key):
        return cached

    direction = "DESC" if order == "desc" else "ASC"
    with get_db() as db:
        rows = db.execute(f"""
            SELECT *, (goals_scored - goals_conceded) AS goal_diff
            FROM teams ORDER BY {sort_by} {direction} LIMIT ?
        """, (limit,)).fetchall()

    return cache_set(cache_key, rows_to_list(rows))


@app.get("/api/teams/{name}", tags=["Teams"])
def get_team(name: str):
    with get_db() as db:
        team = db.execute("SELECT * FROM teams WHERE name LIKE ?", (f"%{name}%",)).fetchone()
        if not team:
            raise HTTPException(404, f"Team '{name}' not found")
        matches = db.execute("""
            SELECT * FROM matches WHERE team1 LIKE ? OR team2 LIKE ?
            ORDER BY year DESC LIMIT 20
        """, (f"%{name}%", f"%{name}%")).fetchall()
        players = db.execute("""
            SELECT name, goals, matches, goals_per_match FROM players
            WHERE country LIKE ? ORDER BY goals DESC LIMIT 10
        """, (f"%{name}%",)).fetchall()

    return {
        **dict(team),
        "recent_matches": rows_to_list(matches),
        "top_players": rows_to_list(players),
    }


# ── ANALYTICS ─────────────────────────────────────────────────────────────────
@app.get("/api/analytics/goals-trend", tags=["Analytics"], summary="Goals per tournament trend")
def goals_trend():
    cache_key = "analytics_goals_trend"
    if cached := cache_get(cache_key):
        return cached

    with get_db() as db:
        rows = db.execute("""
            SELECT year, host, winner, goals, matches, goals_per_match
            FROM tournaments ORDER BY year ASC
        """).fetchall()

    return cache_set(cache_key, rows_to_list(rows))


@app.get("/api/analytics/stage-breakdown", tags=["Analytics"], summary="Goals by stage")
def stage_breakdown(year: Optional[int] = None):
    cache_key = f"analytics_stage_{year}"
    if cached := cache_get(cache_key):
        return cached

    with get_db() as db:
        where = "WHERE year=?" if year else ""
        params = (year,) if year else ()
        rows = db.execute(f"""
            SELECT stage,
                   COUNT(*) AS match_count,
                   SUM(total_goals) AS total_goals,
                   ROUND(AVG(total_goals),2) AS avg_goals,
                   MAX(total_goals) AS max_goals
            FROM matches {where}
            GROUP BY stage
            ORDER BY match_count DESC
        """, params).fetchall()

    return cache_set(cache_key, rows_to_list(rows))


@app.get("/api/analytics/country-performance", tags=["Analytics"])
def country_performance():
    cache_key = "analytics_country"
    if cached := cache_get(cache_key):
        return cached

    with get_db() as db:
        rows = db.execute("""
            SELECT name, flag, titles, appearances, matches_played,
                   wins, draws, losses, goals_scored, goals_conceded,
                   win_rate, goal_difference
            FROM teams ORDER BY titles DESC, wins DESC
        """).fetchall()

    return cache_set(cache_key, rows_to_list(rows))


@app.get("/api/analytics/highest-scoring", tags=["Analytics"])
def highest_scoring_matches(n: int = Query(10, ge=1, le=50)):
    cache_key = f"analytics_high_scoring_{n}"
    if cached := cache_get(cache_key):
        return cached

    with get_db() as db:
        rows = db.execute("""
            SELECT * FROM matches
            ORDER BY total_goals DESC, attendance DESC
            LIMIT ?
        """, (n,)).fetchall()

    return cache_set(cache_key, rows_to_list(rows))


@app.get("/api/analytics/winners-breakdown", tags=["Analytics"])
def winners_breakdown():
    cache_key = "analytics_winners"
    if cached := cache_get(cache_key):
        return cached

    with get_db() as db:
        rows = db.execute("""
            SELECT winner AS country, COUNT(*) AS titles,
                   GROUP_CONCAT(year, ', ') AS winning_years
            FROM tournaments GROUP BY winner ORDER BY titles DESC
        """).fetchall()

    return cache_set(cache_key, rows_to_list(rows))


# ── SEARCH ────────────────────────────────────────────────────────────────────
@app.get("/api/search", tags=["Search"], summary="Global search across teams, players, tournaments")
def search(q: str = Query(..., min_length=2, description="Search query")):
    cache_key = f"search_{q.lower()}"
    if cached := cache_get(cache_key):
        return cached

    with get_db() as db:
        players = db.execute("""
            SELECT 'player' AS type, name AS label, country AS sub, goals AS score
            FROM players WHERE name LIKE ? OR country LIKE ?
            ORDER BY goals DESC LIMIT 5
        """, (f"%{q}%", f"%{q}%")).fetchall()

        teams = db.execute("""
            SELECT 'team' AS type, name AS label, flag AS sub, titles AS score
            FROM teams WHERE name LIKE ?
            ORDER BY titles DESC LIMIT 5
        """, (f"%{q}%",)).fetchall()

        tournaments = db.execute("""
            SELECT 'tournament' AS type, CAST(year AS TEXT) AS label, host AS sub, goals AS score
            FROM tournaments WHERE host LIKE ? OR winner LIKE ? OR CAST(year AS TEXT) LIKE ?
            ORDER BY year DESC LIMIT 5
        """, (f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()

        matches = db.execute("""
            SELECT 'match' AS type,
                   (team1 || ' vs ' || team2) AS label,
                   (CAST(year AS TEXT) || ' ' || stage) AS sub,
                   total_goals AS score
            FROM matches WHERE team1 LIKE ? OR team2 LIKE ?
            ORDER BY year DESC LIMIT 5
        """, (f"%{q}%", f"%{q}%")).fetchall()

    result = {
        "query": q,
        "results": {
            "players": rows_to_list(players),
            "teams": rows_to_list(teams),
            "tournaments": rows_to_list(tournaments),
            "matches": rows_to_list(matches),
        },
        "total": len(players) + len(teams) + len(tournaments) + len(matches),
    }
    return cache_set(cache_key, result)


# ── CACHE MANAGEMENT ──────────────────────────────────────────────────────────
@app.get("/api/cache/stats", tags=["Admin"])
def cache_stats():
    now = time.time()
    return {
        "entries": len(_cache),
        "ttl_seconds": CACHE_TTL,
        "keys": [
            {"key": k, "age_seconds": round(now - v["ts"], 1)}
            for k, v in _cache.items()
        ],
    }

@app.delete("/api/cache/flush", tags=["Admin"])
def flush_cache():
    _cache.clear()
    return {"message": "Cache flushed", "entries": 0}


# ── SERVE FRONTEND ────────────────────────────────────────────────────────────
if os.path.exists(FRONTEND):
    app.mount("/static", StaticFiles(directory=FRONTEND), name="static")

    @app.get("/app/{page}", include_in_schema=False)
    def serve_page(page: str):
        path = os.path.join(FRONTEND, page)
        if os.path.exists(path):
            return FileResponse(path)
        raise HTTPException(404, "Page not found")


# ── STARTUP ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
def startup():
    if not os.path.exists(DB_PATH):
        import subprocess
        subprocess.run(["python", os.path.join(BASE_DIR, "seed_db.py")])
    print("🚀 FIFA Analytics API ready — http://localhost:8000/docs")
