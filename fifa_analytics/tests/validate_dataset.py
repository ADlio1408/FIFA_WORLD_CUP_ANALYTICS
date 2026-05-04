"""
FIFA Analytics Platform — Dataset Validation Report
Deliverable 1: Cleaned FIFA Dataset & Validation Report

Run:  python tests/validate_dataset.py
"""

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "fifa.db")

def validate():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    report = {"checks": [], "passed": 0, "failed": 0}

    def check(name, query, expected_fn, fix=None):
        try:
            result = c.execute(query).fetchone()
            val = result[0] if result else None
            ok = expected_fn(val)
            status = "✅ PASS" if ok else "❌ FAIL"
            report["checks"].append({"check": name, "value": val, "passed": ok})
            if ok: report["passed"] += 1
            else:  report["failed"] += 1
            print(f"  {status}  {name:<45} → {val}")
        except Exception as e:
            print(f"  ❌ ERROR  {name:<45} → {e}")
            report["failed"] += 1

    print("\n" + "═"*65)
    print("  ⚽  FIFA Analytics — Dataset Validation Report")
    print("  Deliverable 1: Cleaned FIFA Dataset")
    print("═"*65)

    print("\n  [1] COMPLETENESS CHECKS")
    print("  " + "─"*60)
    check("Total tournaments present",      "SELECT COUNT(*) FROM tournaments", lambda v: v >= 22)
    check("Total matches present",          "SELECT COUNT(*) FROM matches",     lambda v: v >= 60)
    check("Total players present",          "SELECT COUNT(*) FROM players",     lambda v: v >= 20)
    check("Total teams present",            "SELECT COUNT(*) FROM teams",       lambda v: v >= 15)
    check("Tournaments cover 1930-2022",    "SELECT MAX(year)-MIN(year) FROM tournaments", lambda v: v >= 92)

    print("\n  [2] NULL / INTEGRITY CHECKS")
    print("  " + "─"*60)
    check("No NULL tournament years",       "SELECT COUNT(*) FROM tournaments WHERE year IS NULL",     lambda v: v == 0)
    check("No NULL tournament winners",     "SELECT COUNT(*) FROM tournaments WHERE winner IS NULL",   lambda v: v == 0)
    check("No NULL match teams",            "SELECT COUNT(*) FROM matches WHERE team1 IS NULL OR team2 IS NULL", lambda v: v == 0)
    check("No negative scores",             "SELECT COUNT(*) FROM matches WHERE score1 < 0 OR score2 < 0", lambda v: v == 0)
    check("No NULL player names",           "SELECT COUNT(*) FROM players WHERE name IS NULL",         lambda v: v == 0)
    check("No NULL player goals",           "SELECT COUNT(*) FROM players WHERE goals IS NULL",        lambda v: v == 0)

    print("\n  [3] RANGE / SANITY CHECKS")
    print("  " + "─"*60)
    check("Goals per tournament > 0",       "SELECT MIN(goals) FROM tournaments",               lambda v: v and v > 0)
    check("Goals per tournament < 250",     "SELECT MAX(goals) FROM tournaments",               lambda v: v and v < 250)
    check("Matches per tournament > 10",    "SELECT MIN(matches) FROM tournaments",             lambda v: v and v > 10)
    check("All-time top scorer >= 14 goals","SELECT MAX(goals) FROM players",                   lambda v: v and v >= 14)
    check("Attendance values positive",     "SELECT MIN(attendance) FROM matches WHERE attendance IS NOT NULL", lambda v: v and v > 0)
    check("Teams have appearances",         "SELECT MIN(appearances) FROM teams",               lambda v: v and v > 0)

    print("\n  [4] REFERENTIAL INTEGRITY")
    print("  " + "─"*60)
    check("No orphan match years",
          "SELECT COUNT(*) FROM matches WHERE year NOT IN (SELECT year FROM tournaments)",
          lambda v: v == 0)
    check("Stage values valid",
          "SELECT COUNT(*) FROM matches WHERE stage NOT IN ('Final','Semi-Final','Quarter-Final','Round of 16','Group Stage')",
          lambda v: v == 0)

    print("\n  [5] COMPUTED COLUMNS")
    print("  " + "─"*60)
    check("goals_per_match computed correctly",
          "SELECT ABS(goals_per_match - ROUND(CAST(goals AS REAL)/matches,2)) < 0.01 FROM tournaments LIMIT 1",
          lambda v: bool(v))
    check("total_goals computed in matches",
          "SELECT COUNT(*) FROM matches WHERE total_goals != score1 + score2",
          lambda v: v == 0)
    check("goals_per_match in players correct",
          "SELECT COUNT(*) FROM players WHERE matches > 0 AND ABS(goals_per_match - ROUND(CAST(goals AS REAL)/matches,2)) > 0.01",
          lambda v: v == 0)

    print("\n  [6] ANALYTICS INTEGRITY")
    print("  " + "─"*60)
    check("Brazil has 5 titles (teams table)",   "SELECT titles FROM teams WHERE name='Brazil'",   lambda v: v == 5)
    check("Germany has 4 titles (teams table)",  "SELECT titles FROM teams WHERE name='Germany'",  lambda v: v == 4)
    check("Klose is all-time top scorer",         "SELECT name FROM players ORDER BY goals DESC LIMIT 1", lambda v: v == "Miroslav Klose")
    check("2022 Qatar final recorded",            "SELECT COUNT(*) FROM matches WHERE year=2022 AND stage='Final'", lambda v: v >= 1)
    check("KPI cache populated",                  "SELECT COUNT(*) FROM kpi_cache",                lambda v: v and v > 0)

    conn.close()

    # ── Final summary ──────────────────────────────────────────────────────
    total = report["passed"] + report["failed"]
    pct = report["passed"] / total * 100 if total else 0
    print("\n" + "═"*65)
    print(f"  VALIDATION COMPLETE: {report['passed']}/{total} checks passed ({pct:.0f}%)")
    grade = "EXCELLENT" if pct == 100 else ("GOOD" if pct >= 90 else "NEEDS ATTENTION")
    print(f"  Quality Score: {grade}")
    print("═"*65 + "\n")

    # Save report
    out_path = os.path.join(os.path.dirname(__file__), "validation_report.json")
    with open(out_path, "w") as f:
        json.dump({**report, "quality_score_pct": round(pct, 1), "grade": grade}, f, indent=2)
    print(f"  📄 Report saved: tests/validation_report.json\n")

if __name__ == "__main__":
    validate()
