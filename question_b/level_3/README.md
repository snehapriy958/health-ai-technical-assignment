# Question B — Level 3: Failure Reasoning, Engineering Analysis, and Concurrency

## Overview

Level 3 documents the two intentional failure experiments, diagnoses, and hardening mechanisms for the health risk prediction application, and separately provides an empirical 100-user concurrency evaluation and production safety architecture.

**Personal Random Seed:** `S = 48`

### Summary of Intentional Failures & Concurrency Evaluation
- **Intentional Failure 1 — Missing Trained Model Artifact (`model.joblib`):**
  - Temporarily moving or renaming `model.joblib`.
  - `GET /health` reports `status = "degraded"` (`model_loaded: false`).
  - `POST /predict` returns HTTP 503 Service Unavailable with descriptive diagnostic details rather than an unhandled 500 or process crash.
  - Restoring the model artifact recovers normal prediction operation.
- **Intentional Failure 2 — Wrong Input Type (`age = "fifty"`):**
  - Submitting non-numeric string data to a numerical clinical feature.
  - Direct unvalidated scikit-learn inference raises `ValueError: could not convert string to float: 'fifty'`.
  - FastAPI / Pydantic schema validation intercepts the malformed payload before inference is attempted.
  - The API returns HTTP 422 Unprocessable Entity and records the attempt into SQLite with `status = 'VALIDATION_ERROR'`.
- **Separate Concurrency / Load Test (Not an Intentional Failure):**
  - 100 simultaneous concurrent asynchronous requests evaluated via `question_b/level_3/load_test.py`.
  - 100/100 HTTP 200 responses with 100 persisted SQLite records under Write-Ahead Logging (WAL) mode.

---

## 1. Baseline Architecture

The system built across Levels 1 and 2 consists of:
- **Inference Pipeline:** `StandardScaler` + `LogisticRegression(random_state=48)` trained on the UCI Cleveland Heart Disease dataset.
- **Web Framework:** FastAPI with Uvicorn (ASGI event loop).
- **Persistence Layer:** Embedded SQLite database (`predictions.db`) operated with raw parameterized SQL (zero ORM), WAL journal mode, and short-lived connection lifetimes.
- **Validation Layer:** Pydantic `BaseModel` schemas enforcing strict physiological feature boundaries (`ge`, `le`).

---

## 2. Failure Experiment 1: Missing Model Artifact

### Intentional Change
The trained model artifact (`question_b/level_1/model.joblib`) was temporarily moved/renamed to `model.joblib.bak` while starting the application and serving requests.

### Observed Failure
- **Startup:** If model loading is done strictly at import time without error handling, Python crashes immediately with `FileNotFoundError`, aborting the entire process before serving any HTTP traffic.
- **Runtime:** If an unhandled endpoint attempts `joblib.load()` on request, an uncaught exception triggers an HTTP `500 Internal Server Error`, exposing an unformatted traceback to the client.

### Diagnosis & Root Cause
- **Root Cause:** A missing external file dependency required for machine learning inference.
- **Diagnostic Evidence:**
  ```
  FileNotFoundError: Trained model not found at .../model.joblib. Please run train.py first to generate model.joblib.
  ```

### Engineering Fix
1. **Graceful Startup Handling:** In `app.py`, the `lifespan` context manager attempts to load the model on startup. If missing, it logs a clear warning without crashing the server process (`ml_models["pipeline"] = None`).
2. **Degraded Health Reporting:** The `GET /health` endpoint detects missing weights and reports:
   ```json
   {
     "status": "degraded",
     "model_loaded": false,
     "database_path": "..."
   }
   ```
3. **Controlled Service Unavailable Status:** When a client hits `POST /predict` without a model, the endpoint returns an HTTP `503 Service Unavailable` with a clear explanation:
   ```json
   {
     "detail": "Trained model artifact not found. Please run train.py first."
   }
   ```
4. **Lazy Self-Healing:** If the model file is restored or retrained while the server is running, subsequent requests automatically attempt to load the newly available artifact without requiring a server reboot.

### Verification After Fix
Executed via `question_b/level_3/run_failure_experiments.py`:
- `GET /health` with missing model: `HTTP 200`, `{"status": "degraded", "model_loaded": false}`
- `POST /predict` with missing model: `HTTP 503`, `{"detail": "Trained model artifact not found. Please run train.py first."}`
- Restored `model.joblib`:
- `GET /health`: `HTTP 200`, `{"status": "healthy", "model_loaded": true}`
- `POST /predict`: `HTTP 200`, `{"prediction": 1, "risk_probability": 0.6072, "risk_label": "High"}`

---

## 3. Failure Experiment 2: Incompatible Input Type

### Intentional Change
A request payload was submitted with an incompatible data type for a numeric clinical field (e.g., `{"age": "fifty", ...}`).

### Observed Failure
- **Direct Model Pipeline (Unvalidated):** When passing unvalidated inputs (`"fifty"`) directly into the scikit-learn pipeline, `StandardScaler` raises:
  ```
  ValueError: could not convert string to float: 'fifty'
  ```
- If this occurs in a naive web handler, it results in an unhandled server exception, partial transaction inconsistency, and an uninformative HTTP `500` server error.

### Diagnosis & Root Cause
- **Root Cause:** Scikit-learn pipelines require strictly numeric (float/int) matrices. String inputs break arithmetic operations during standardization and dot-product calculations.
- **Location of Validation:** Request deserialization at the FastAPI / Pydantic boundary, before application code or machine learning routines are executed.

### Engineering Fix
1. **Strict Type Coercion & Schema Validation:** Pydantic's `PredictionInput` schema validates that `age` is an integer and numeric vitals are floats within physiologically plausible ranges (`1 <= age <= 120`).
2. **Audit Logging of Failures:** Standard FastAPI drops rejected requests before route handler execution. We implemented a custom `RequestValidationError` handler in `question_b/level_2/app.py` that intercepts rejected requests, extracts any parseable fields, and persists the record into SQLite with `status = 'VALIDATION_ERROR'` and the exact validation error message.
3. **Clean Client Error:** Returns HTTP `422 Unprocessable Entity` with structured field-level diagnostic messages rather than crashing or returning an unhandled 500.

### Verification After Fix
Executed via `question_b/level_3/run_failure_experiments.py`:
- Direct Scikit-learn call: Raises `ValueError: could not convert string to float: 'fifty'`
- FastAPI endpoint response: `HTTP 422 Unprocessable Entity`
  ```json
  {
    "detail": [
      {
        "type": "int_parsing",
        "loc": ["body", "age"],
        "msg": "Input should be a valid integer, unable to parse string as an integer",
        "input": "fifty"
      }
    ]
  }
  ```
- SQLite persistence confirmed:
  ```
  id: 7, status: 'VALIDATION_ERROR', error: 'body.age: Input should be a valid integer, unable to parse string as an integer'
  ```

---

## 4. Engineering Analysis: Supporting 100 Concurrent Users

### 1. FastAPI & Uvicorn Request Handling
- Uvicorn runs an asynchronous event loop (based on `uvloop`/`asyncio`). In a single-threaded process, it can handle thousands of concurrent I/O-bound socket connections efficiently.
- However, Scikit-learn inference (`predict_proba`) and SQLite database writes are synchronous CPU and file I/O operations. If CPU-bound prediction tasks block the event loop, request latency degrades.

### 2. SQLite Concurrency Limitations
- SQLite is a serverless, file-based database. While it supports multiple simultaneous read operations, **it only permits a single writer at any given moment**.
- Under high concurrent write loads (e.g., 100 concurrent clients executing `POST /predict`), multiple threads/processes attempting to acquire the write lock simultaneously can encounter lock contention, leading to `sqlite3.OperationalError: database is locked`.

### 3. Short-Lived Connections & Short Transactions
- To minimize write lock contention, connections must never be held open globally.
- Each operation uses a scoped context manager:
  ```python
  with sqlite3.connect(db_path, timeout=10.0) as conn:
      conn.execute(...)
      conn.commit()
  ```
- Connections are opened immediately before the query and closed immediately after `commit()`, keeping transaction durations under a few milliseconds.
- The `timeout=10.0` parameter instructs SQLite's internal busy handler to wait up to 10 seconds for locks to clear before failing.

### 4. Write-Ahead Logging (WAL) Mode
- We enabled `PRAGMA journal_mode = WAL;`.
- **What WAL solves:** Readers do not block writers, and writers do not block readers. A long-running `GET /stats` query reading aggregate metrics does not prevent incoming `POST /predict` requests from appending to the log.
- **What WAL does NOT solve:** WAL does **not** allow multiple concurrent writers. Only one transaction can write to the `-wal` file at a time. High concurrent write throughput will still serialize at the write barrier.

### 5. SQLite vs. PostgreSQL for Production
- **SQLite:** Excellent for embedded, zero-configuration deployments, prototypes, and low-to-medium write loads. It avoids database server management and external network overhead.
- **PostgreSQL (Production Recommendation):** For high-concurrency production systems, PostgreSQL is strongly preferred. It provides row-level locking (MVCC), dedicated connection pooling (e.g., PgBouncer), true multi-writer concurrency across distributed instances, and horizontal scaling capabilities.

### 6. Multiple Uvicorn Worker Processes
- In production, Uvicorn should be launched with multiple worker processes behind a process manager (e.g., Gunicorn or container orchestrator):
  ```bash
  uvicorn question_b.level_2.app:app --host 0.0.0.0 --port 8000 --workers 4
  ```
- Having 4 worker processes allows utilizing multiple CPU cores, parallelizing model inference across processes. Note: with SQLite, multiple processes increase write lock contention unless a dedicated write queue or client-server RDBMS is used.

### 7. Stateless API Design
- The FastAPI application is completely stateless. No session state or prediction context is stored in application memory.
- All persistent state resides in the database. This allows running multiple application replicas behind a load balancer (e.g., NGINX, AWS ALB).

### 8. Model Loading Strategy
- **Correct Strategy:** The model pipeline is loaded once into memory during application startup (in `lifespan`) and stored in a shared application dictionary (`ml_models["pipeline"]`).
- **Anti-Pattern Avoided:** Loading the `.joblib` file from disk on every incoming request would introduce disk I/O latency, excessive memory allocations, and garbage collection pauses. Scikit-learn estimators are thread-safe for read-only `predict()` / `predict_proba()` calls.

### 9. Database Connection Handling
- In the current implementation, connections are opened per request with a 10-second busy timeout.
- For 100 concurrent users writing continuously, an asynchronous worker queue (e.g., Celery, Redis queue, or an in-memory `asyncio.Queue`) that consumes and batch-inserts prediction logs into SQLite would eliminate all lock contention.

### 10. Request Validation Before Inference
- Validating inputs via Pydantic prior to running inference ensures that CPU cycles are never wasted on malformed requests, shielding the Scikit-learn estimator from unexpected memory faults or type coercion errors.

### 11. Monitoring Metrics Under 100 Concurrent Users
Under sustained 100-user load, the following metrics should be tracked:
- **Latency Distribution:** p50, p95, and p99 response times (target: p95 < 200 ms).
- **Error Rate:** HTTP 5xx responses (target: 0.0%) and HTTP 422 rates.
- **Database Lock Contention:** Count of `sqlite3.OperationalError` (busy/locked events).
- **System Resources:** CPU utilization percentage per core and memory consumption per worker.
- **Throughput:** Requests per second (RPS) handled successfully.

### 12. Recommended Production Architecture
```
[ 100 Concurrent Clients ]
            │
            ▼
   [ NGINX / Reverse Proxy ] (SSL Termination, Rate Limiting)
            │
            ▼
[ Uvicorn ASGI Cluster (4 Workers) ] ── (In-Memory Scikit-learn Pipeline)
            │
            ▼
[ Asynchronous Logging Queue / Redis ]
            │
            ▼
[ PostgreSQL Database (Connection Pooled via PgBouncer) ]
```

---

## 5. Empirical 100-User Concurrency Benchmark

An empirical concurrency test was executed against the running application using `httpx.AsyncClient` with 100 simultaneous workers dispatched concurrently.

**Benchmark Script:** [`question_b/level_3/load_test.py`](file:///c:/Developers/Sneha/health-ai-technical-assignment/question_b/level_3/load_test.py)

### Actual Benchmark Results
| Metric | Value |
| :--- | :--- |
| **Total Requests Dispatched** | `100` |
| **Concurrent Workers** | `100` |
| **Total Elapsed Time** | `2.337 s` |
| **Measured Throughput** | `42.78 req/s` |
| **Successful Requests (HTTP 200)** | `100 / 100` (`100.0%`) |
| **Failed Requests** | `0` (`0.0%`) |
| **SQLite Rows Persisted** | `100 / 100` (`100.0%`) |
| **Latency (Minimum)** | `850.42 ms` |
| **Latency (Median / p50)** | `1996.40 ms` |
| **Latency (Mean)** | `1714.47 ms` |
| **Latency (95th Percentile)** | `2128.75 ms` |
| **Latency (Maximum)** | `2131.80 ms` |

**Key Findings:**
1. **Zero Database Lock Failures:** All 100 concurrent requests successfully acquired SQLite write locks and persisted their predictions. WAL mode combined with `timeout=10.0` prevented any `database is locked` errors.
2. **Latency Queuing Effect:** Because SQLite serializes writes and the single-process development server handles requests sequentially, latency increased from 850 ms for the first batch to ~2130 ms for the last batch as requests queued up behind preceding disk writes.

---

## 6. Personal Intelligence & Decision Evidence

### Decision 1: Custom Validation Exception Handler vs. Route-Level Try/Catch
- **Choice:** Implemented an `@app.exception_handler(RequestValidationError)` global handler.
- **Rejected Alternative:** Handling validation manually inside the route handler with raw dictionaries.
- **Why:** FastAPI evaluates Pydantic type signatures before invoking the route handler. Without a custom exception handler, invalid requests are rejected upstream and would never be recorded in SQLite, violating the assignment requirement to *"save every request and result"*.
- **Evidence:** Verified by Failure Experiment 2 and automated test `test_bad_input_validation_error_logged`: sending an out-of-range integer or string safely writes a row with `status = 'VALIDATION_ERROR'` and returns HTTP 422.

### Decision 2: Single-Query Hand-Written SQL Aggregation vs. Multi-Query / In-Memory Python Filtering
- **Choice:** Executed a single SQL query computing all metrics using conditional aggregations (`COUNT(CASE WHEN ...)` and `AVG(...)`).
- **Rejected Alternative:** Fetching all rows into Python using `SELECT *` and computing metrics in pandas/numpy.
- **Why:** Computing aggregations inside SQLite pushes calculation down to the database engine in $O(N)$ single-pass time without loading thousands of historical records into server RAM.
- **Evidence:** Implemented in `question_b/level_2/db.py:get_stats()`; verified via `test_stats_endpoint_sql_aggregation`.

---

## 7. Real AI Pitfall Identified & Manually Verified

- **Identified AI Mistake / Vulnerability:**
  When generating FastAPI applications with database logging, AI coding assistants routinely assume that invalid requests can be logged inside the `predict_endpoint` route:
  ```python
  @app.post("/predict")
  async def predict(payload: PredictionInput):
      # AI assumption: validation errors reach this line
      ...
  ```
  In reality, Pydantic validation errors trigger an immediate short-circuit by FastAPI's framework before the route body is ever entered. An application built with this naive assumption would silently fail to record all invalid prediction attempts in SQLite, directly violating the assignment specification.
- **Manual Verification:**
  We verified this behavior by testing requests against unhardened routes. We engineered the custom `RequestValidationError` handler to capture the raw request stream, parse any extractable feature data, and persist the failure to SQLite before delegating to the client response.
