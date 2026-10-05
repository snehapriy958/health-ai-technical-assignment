"""
Empirical Concurrency & Load Test Script for Question B - Level 3
Tests behavior under 100 concurrent requests against the FastAPI application.
"""

import os
import sys
import time
import asyncio
import statistics
import sqlite3

# Ensure repository root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import httpx
from question_b.level_2.db import get_db_path


async def worker(client: httpx.AsyncClient, url: str, payload: dict, latencies: list, results: list):
    start = time.perf_counter()
    try:
        resp = await client.post(url, json=payload, timeout=15.0)
        elapsed = (time.perf_counter() - start) * 1000.0  # ms
        latencies.append(elapsed)
        results.append((resp.status_code, None))
    except Exception as exc:
        elapsed = (time.perf_counter() - start) * 1000.0
        latencies.append(elapsed)
        results.append((0, str(exc)))


async def run_load_test(base_url: str = "http://127.0.0.1:8000", total_users: int = 100):
    print("=" * 60)
    print(f"EMPIRICAL CONCURRENCY BENCHMARK ({total_users} CONCURRENT REQUESTS)")
    print("=" * 60)

    url = f"{base_url}/predict"
    test_payload = {
        "age": 55,
        "sex": 1,
        "resting_bp": 135.0,
        "cholesterol": 240.0,
        "max_hr": 140.0,
    }

    # Count initial rows in SQLite
    db_path = get_db_path()
    initial_db_rows = 0
    if os.path.exists(db_path):
        with sqlite3.connect(db_path) as conn:
            initial_db_rows = conn.execute("SELECT COUNT(*) FROM prediction_logs;").fetchone()[0]

    latencies = []
    results = []

    # Configure connection limits to allow 100 simultaneous connections
    limits = httpx.Limits(max_connections=120, max_keepalive_connections=100)
    async with httpx.AsyncClient(limits=limits) as client:
        start_time = time.perf_counter()
        tasks = [
            worker(client, url, test_payload, latencies, results)
            for _ in range(total_users)
        ]
        await asyncio.gather(*tasks)
        total_duration = time.perf_counter() - start_time

    # Analyze results
    success_count = sum(1 for status, _ in results if status == 200)
    error_count = sum(1 for status, _ in results if status != 200)

    # Count post-test rows in SQLite
    final_db_rows = 0
    if os.path.exists(db_path):
        with sqlite3.connect(db_path) as conn:
            final_db_rows = conn.execute("SELECT COUNT(*) FROM prediction_logs;").fetchone()[0]

    db_rows_added = final_db_rows - initial_db_rows

    latencies.sort()
    min_lat = min(latencies)
    max_lat = max(latencies)
    mean_lat = statistics.mean(latencies)
    median_lat = statistics.median(latencies)
    p95_lat = latencies[int(len(latencies) * 0.95)]
    rps = total_users / total_duration if total_duration > 0 else 0

    print(f"Total Requests Dispatched:  {total_users}")
    print(f"Concurrent Workers:          {total_users}")
    print(f"Total Elapsed Time:          {total_duration:.3f} s")
    print(f"Throughput:                  {rps:.2f} req/s")
    print(f"Successful Requests (HTTP 200): {success_count} ({success_count / total_users * 100:.1f}%)")
    print(f"Failed Requests:             {error_count} ({error_count / total_users * 100:.1f}%)")
    print(f"SQLite Rows Persisted:       {db_rows_added} / {total_users}")
    print(f"Latency (Min):               {min_lat:.2f} ms")
    print(f"Latency (Median / p50):      {median_lat:.2f} ms")
    print(f"Latency (Mean):              {mean_lat:.2f} ms")
    print(f"Latency (95th Percentile):   {p95_lat:.2f} ms")
    print(f"Latency (Max):               {max_lat:.2f} ms")

    return {
        "total_users": total_users,
        "duration_s": round(total_duration, 3),
        "rps": round(rps, 2),
        "success_count": success_count,
        "error_count": error_count,
        "db_rows_added": db_rows_added,
        "min_lat_ms": round(min_lat, 2),
        "median_lat_ms": round(median_lat, 2),
        "mean_lat_ms": round(mean_lat, 2),
        "p95_lat_ms": round(p95_lat, 2),
        "max_lat_ms": round(max_lat, 2),
    }


if __name__ == "__main__":
    asyncio.run(run_load_test())
