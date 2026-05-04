"""
FIFA Analytics Platform — Load & Performance Testing
Deliverable 6: Load Testing Engine
Simulates concurrent users hitting all API endpoints

Run:
    python tests/load_test.py
    python tests/load_test.py --users 50 --duration 30
"""

import asyncio
import time
import statistics
import argparse
import json
from urllib.request import urlopen
from urllib.error import URLError
import threading
import sys

BASE_URL = "http://localhost:8000"

ENDPOINTS = [
    ("/api/kpis",                         "KPIs"),
    ("/api/kpis?year=2022",               "KPIs filtered"),
    ("/api/tournaments",                  "Tournaments"),
    ("/api/tournaments/2018",             "Tournament detail"),
    ("/api/matches?limit=20",             "Matches"),
    ("/api/matches?year=2022&stage=Final","Matches filtered"),
    ("/api/matches?team=Germany",         "Matches by team"),
    ("/api/players",                      "Players"),
    ("/api/players/top?n=10",            "Top scorers"),
    ("/api/teams",                        "Teams"),
    ("/api/teams/Brazil",                 "Team detail"),
    ("/api/analytics/goals-trend",        "Goals trend"),
    ("/api/analytics/stage-breakdown",    "Stage breakdown"),
    ("/api/analytics/winners-breakdown",  "Winners"),
    ("/api/search?q=Germany",             "Search"),
]

results = {ep[1]: [] for ep in ENDPOINTS}
errors  = {ep[1]: 0    for ep in ENDPOINTS}
lock = threading.Lock()

def fetch(url, label):
    try:
        t0 = time.perf_counter()
        resp = urlopen(BASE_URL + url, timeout=10)
        resp.read()
        elapsed = (time.perf_counter() - t0) * 1000  # ms
        with lock:
            results[label].append(elapsed)
    except Exception as e:
        with lock:
            errors[label] += 1

def worker(duration_s):
    end = time.time() + duration_s
    while time.time() < end:
        for url, label in ENDPOINTS:
            fetch(url, label)

def run_load_test(num_users=10, duration=20):
    print("\n" + "═"*58)
    print("  ⚽  FIFA Analytics — Load Test")
    print(f"  Users: {num_users}   Duration: {duration}s")
    print("═"*58)

    # Verify server is up
    try:
        urlopen(BASE_URL + "/", timeout=3)
    except URLError:
        print("\n❌ ERROR: Server not running at", BASE_URL)
        print("   Run:  python start.py")
        sys.exit(1)

    print(f"\n🔄 Starting {num_users} concurrent users for {duration}s…\n")
    t_start = time.time()

    threads = [threading.Thread(target=worker, args=(duration,), daemon=True)
               for _ in range(num_users)]
    for t in threads: t.start()
    for t in threads: t.join()

    elapsed = time.time() - t_start

    # ── Summary ────────────────────────────────────────────────────────────
    total_req  = sum(len(v) for v in results.values())
    total_err  = sum(errors.values())
    rps        = total_req / elapsed

    print("─"*58)
    print(f"  {'Endpoint':<26} {'Req':>5} {'Err':>4} {'Avg':>7} {'P95':>7} {'Max':>7}")
    print("─"*58)

    all_times = []
    for _, label in ENDPOINTS:
        times = results[label]
        errs  = errors[label]
        if times:
            avg = statistics.mean(times)
            p95 = sorted(times)[int(len(times)*0.95)]
            mx  = max(times)
            all_times.extend(times)
            status = "✅" if avg < 200 else ("⚠️" if avg < 500 else "❌")
            print(f"  {status} {label:<24} {len(times):>5} {errs:>4} {avg:>6.1f}ms {p95:>6.1f}ms {mx:>6.1f}ms")
        else:
            print(f"  ⚠️  {label:<24} {'0':>5} {errs:>4}   N/A     N/A     N/A")

    print("─"*58)
    overall_avg = statistics.mean(all_times) if all_times else 0
    overall_p95 = sorted(all_times)[int(len(all_times)*0.95)] if all_times else 0
    print(f"\n  📊 SUMMARY")
    print(f"     Total requests   : {total_req}")
    print(f"     Total errors     : {total_err}")
    print(f"     Duration         : {elapsed:.1f}s")
    print(f"     Throughput       : {rps:.1f} req/s")
    print(f"     Overall avg      : {overall_avg:.1f}ms")
    print(f"     Overall P95      : {overall_p95:.1f}ms")
    print(f"     Error rate       : {total_err/(total_req+total_err)*100:.2f}%")

    grade = "EXCELLENT" if overall_p95 < 100 else ("GOOD" if overall_p95 < 300 else "NEEDS WORK")
    print(f"\n  🏆 Performance Grade: {grade}")
    print("═"*58 + "\n")

    # Save JSON report
    report = {
        "test_config": {"users": num_users, "duration": duration},
        "summary": {
            "total_requests": total_req,
            "total_errors": total_err,
            "duration_s": round(elapsed, 2),
            "throughput_rps": round(rps, 2),
            "avg_latency_ms": round(overall_avg, 2),
            "p95_latency_ms": round(overall_p95, 2),
            "error_rate_pct": round(total_err/(total_req+total_err)*100, 2) if (total_req+total_err) > 0 else 0,
        },
        "endpoints": {
            label: {
                "requests": len(results[label]),
                "errors": errors[label],
                "avg_ms": round(statistics.mean(results[label]), 2) if results[label] else None,
                "p95_ms": round(sorted(results[label])[int(len(results[label])*0.95)], 2) if results[label] else None,
            }
            for _, label in ENDPOINTS
        }
    }
    with open("load_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("  📄 Report saved: load_test_report.json\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FIFA Analytics Load Tester")
    parser.add_argument("--users",    type=int, default=10, help="Concurrent users (default 10)")
    parser.add_argument("--duration", type=int, default=20, help="Duration in seconds (default 20)")
    args = parser.parse_args()
    run_load_test(args.users, args.duration)
