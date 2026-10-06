# Question B — Level 3: Failure Comparison & Concurrency Analysis

**Seed**: `S = 48`
**Purpose**: Document intentional failure modes before and after engineering hardening, and analyze concurrency requirements.

---

## 1. Intentional Failure Comparisons

### Failure Experiment 1: Missing Model Artifact (`model.joblib`)

| Aspect | BEFORE Hardening | AFTER Hardening |
|---|---|---|
| **Mechanism** | Model loaded at top-level module import or inside route without existence verification. | Lifespan context manager catches `FileNotFoundError` gracefully; lazy reload on request. |
| **Startup Behavior** | Process crashes immediately with `FileNotFoundError`, aborting server startup. | Application starts cleanly, logging a warning while keeping HTTP server operational. |
| **Health Check (`GET /health`)** | Either unavailable (process crashed) or reports unverified `"healthy"`. | Returns HTTP 200 with explicit degraded state: `{"status": "degraded", "model_loaded": false}`. |
| **Inference (`POST /predict`)** | Triggers unhandled `FileNotFoundError`, returning HTTP 500 with raw server stack trace. | Returns controlled **HTTP 503 Service Unavailable** with structured JSON diagnostic message. |
| **Recovery** | Server requires manual restart after file restoration. | **Self-healing**: Next request automatically re-attempts artifact load without process reboot. |
| **Reliability Improvement** | Prevents total service outages; decouples server process availability from model artifact deployment state. |

---

### Failure Experiment 2: Incompatible Input Type (`age = "fifty"`)

| Aspect | BEFORE Hardening | AFTER Hardening |
|---|---|---|
| **Mechanism** | Unvalidated input dictionaries passed directly into scikit-learn pipeline. | Strict Pydantic v2 `BaseModel` schema with runtime type enforcement (`int`, `float`) and bounds. |
| **Pipeline Behavior** | `StandardScaler` / NumPy raises `ValueError: could not convert string to float: 'fifty'`. | Malformed payload is intercepted at the ASGI serialization boundary before reaching inference. |
| **HTTP Response** | Unhandled HTTP 500 Internal Server Error with exposed Python traceback. | Structured **HTTP 422 Unprocessable Entity** detailing exact field (`body.age`) and error reason. |
| **Audit Persistence** | Native FastAPI drops rejected requests, leaving zero persistence record in SQLite. | Custom `RequestValidationError` handler intercepts error and logs `status = 'VALIDATION_ERROR'` to SQLite. |
| **Reliability Improvement** | Shields machine learning estimators from illegal inputs, preserves transaction auditability, and provides clear client guidance. |

---

## 2. Concurrency Evaluation: 100 Concurrent Requests

> [!IMPORTANT]
> **Production Scope Clarification**:
> We evaluated 100 concurrent requests under the assignment test using an asynchronous HTTP benchmark script (`load_test.py`). We do **not** claim the current single-process SQLite implementation is a production-ready system for arbitrary multi-user workloads.

### Empirical Evaluation Summary
- **Workload**: 100 concurrent asynchronous clients issuing simultaneous `POST /predict` requests.
- **Measured Outcome**: 100/100 HTTP 200 responses (100.0% success rate, 0 errors), 100/100 rows persisted to SQLite.
- **Performance Metrics**:
  - Total Duration: 2.356 s (Throughput: 42.44 req/s)
  - Min Latency: 563.54 ms
  - Median (p50) Latency: 1429.29 ms
  - Mean Latency: 1613.39 ms
  - 95th Percentile (p95) Latency: 2145.26 ms
  - Max Latency: 2147.51 ms
- **Observed Behavior**: Write-Ahead Logging (WAL) and `timeout=10.0` prevented database lock crashes. However, because SQLite serializes all writes through a single write lock, queued requests experienced serialization latency rising up to ~2147 ms.

### Path to True Production Concurrency (100+ Concurrent Users)

To transition from this prototype to an enterprise-grade service handling sustained multi-user loads safely, the following architectural measures are required:

1. **Stateless API & Horizontal Scaling**:
   - The FastAPI service is completely stateless and can run across multiple container replicas (e.g., Kubernetes pods or Cloud Run instances) behind an Application Load Balancer / NGINX reverse proxy.
2. **Client-Server Relational Database (PostgreSQL)**:
   - Replace file-based SQLite with PostgreSQL, enabling Multi-Version Concurrency Control (MVCC) and non-blocking multi-writer transactions.
3. **Dedicated Connection Pooling**:
   - Deploy connection poolers (e.g., PgBouncer or SQLAlchemy async connection pools) to prevent socket exhaustion under high concurrency.
4. **Short Transactions & Scoped Lifetimes**:
   - Keep database transactions strictly bounded to single write operations, committing immediately to prevent idle-in-transaction locks.
5. **Proper Busy Timeouts & Backoff**:
   - Configure sensible connection and query timeouts with exponential backoff on retryable deadlocks.
6. **Asynchronous Write Queue / Buffering**:
   - Decouple user-facing prediction responses from persistence logging using an asynchronous message queue (e.g., Redis Streams, Celery, or background worker tasks), batching write queries.
7. **Input Validation Before Inference**:
   - Pydantic schema validation ensures CPU cycles are never wasted on malformed requests, shielding estimators from unnecessary computation.
8. **Rate Limiting & Abuse Prevention**:
   - Enforce IP-based and token bucket rate limiting at the reverse proxy (e.g., NGINX `limit_req_zone`).
9. **Observability & Monitoring**:
   - Track p50, p95, and p99 latency percentiles, error rates (HTTP 4xx / 5xx), database pool utilization, and CPU/memory metrics per worker.
10. **Automated Health Probes**:
    - Use `/health` endpoints for orchestrator liveness and readiness checks, automatically recycling unhealthy worker instances.
