# Question B — Level 2: Persistent Storage and Query Aggregations

## Overview

Level 2 extends the risk prediction service by persisting every prediction request and its outcome to an embedded **SQLite** database and exposing a `GET /stats` endpoint computed entirely with **hand-written SQL** (zero ORM).

**Personal Random Seed:** `S = 48`

---

## 1. Database Schema

The database utilizes a single table, `prediction_logs`, created in `predictions.db`:

```sql
CREATE TABLE IF NOT EXISTS prediction_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    age REAL,
    sex REAL,
    resting_bp REAL,
    cholesterol REAL,
    max_hr REAL,
    predicted_class INTEGER,
    predicted_risk_probability REAL,
    risk_label TEXT,
    status TEXT NOT NULL,
    error_message TEXT
);
```

### Column Descriptions
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `INTEGER PRIMARY KEY` | Auto-incrementing identifier |
| `timestamp` | `TEXT NOT NULL` | ISO 8601 UTC timestamp of the request |
| `age` | `REAL` | Patient age in years |
| `sex` | `REAL` | Biological sex (`0` = Female, `1` = Male) |
| `resting_bp` | `REAL` | Resting blood pressure (mm Hg) |
| `cholesterol` | `REAL` | Serum cholesterol (mg/dL) |
| `max_hr` | `REAL` | Maximum heart rate achieved (bpm) |
| `predicted_class` | `INTEGER` | Binary classification (`0` = Low Risk, `1` = High Risk; `NULL` on error) |
| `predicted_risk_probability` | `REAL` | Model output probability (`0.0`–`1.0`; `NULL` on error) |
| `risk_label` | `TEXT` | `'High'` or `'Low'` (`NULL` on error) |
| `status` | `TEXT NOT NULL` | `'SUCCESS'`, `'VALIDATION_ERROR'`, or `'INFERENCE_ERROR'` |
| `error_message` | `TEXT` | Error description if request failed (`NULL` on success) |

---

## 2. Why SQLite Was Selected

1. **Embedded & Zero Configuration:** SQLite runs in-process with the Python interpreter, requiring no external daemon, container, network port, or credentials.
2. **ACID Compliant:** Guarantees atomic writes and transactional consistency.
3. **Reproducibility & Portability:** The entire application and its state remain self-contained within the repository, making it ideal for evaluation and live walkthroughs.
4. **Standard Library Integration:** Python's standard `sqlite3` module avoids third-party dependencies, adhering strictly to the constraint: *"NO ORM, hand-written SQL"*.

---

## 3. How Requests and Results Are Persisted

- **Short-Lived Connections:** Each read and write operation uses a fresh connection inside a Python context manager (`with sqlite3.connect(...) as conn:`), committing explicitly and closing immediately to avoid connection leaks.
- **WAL Mode:** Write-Ahead Logging (`PRAGMA journal_mode = WAL;`) allows readers and writers to operate concurrently without blocking one another.
- **Capturing Both Successful and Failed Requests:**
  - **Successful predictions:** Captured in `POST /predict`, storing the input features, predicted class, probability, label, and `status = 'SUCCESS'`.
  - **Failed validation requests:** Captured via a custom FastAPI `RequestValidationError` exception handler. The handler records any provided feature values along with the Pydantic validation error string and `status = 'VALIDATION_ERROR'`.

---

## 4. Exact SQL / Statistics Logic

The `GET /stats` endpoint executes the following single hand-written SQL query:

```sql
SELECT
    COUNT(*) AS total_requests,
    COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) AS successful_requests,
    COUNT(CASE WHEN status != 'SUCCESS' THEN 1 END) AS failed_requests,
    AVG(CASE WHEN status = 'SUCCESS' THEN predicted_risk_probability END) AS avg_risk,
    AVG(CASE WHEN status = 'SUCCESS' THEN (CASE WHEN predicted_class = 1 THEN 1.0 ELSE 0.0 END) END) AS high_risk_ratio
FROM prediction_logs;
```

### Metrics Computation
- `total_requests`: Total count of all logged requests (`COUNT(*)`), including failed requests.
- `average_predicted_risk`: Calculated strictly over `status = 'SUCCESS'` rows (`AVG(predicted_risk_probability)`). If no successful rows exist, returns `0.0`.
- `high_risk_share`: Calculated strictly over `status = 'SUCCESS'` rows (`COUNT(predicted_class = 1) / COUNT(successful)`). If no successful rows exist, returns `0.0`.
- **Definition of High Risk:** Consistent with Level 1 (`predicted_class = 1`, i.e., probability $\ge 0.5$).

---

## 5. Input Validation Behavior

Input validation is enforced using Pydantic `PredictionInput` with explicit boundary constraints:
- `age`: integer, `1 <= age <= 120`
- `sex`: integer, `0` or `1`
- `resting_bp`: float, `50.0 <= resting_bp <= 250.0` (mm Hg)
- `cholesterol`: float, `80.0 <= cholesterol <= 600.0` (mg/dL)
- `max_hr`: float, `50.0 <= max_hr <= 250.0` (bpm)

When a validation constraint is violated (e.g., `age: 150` or non-numeric types):
1. The exception handler intercepts the request before FastAPI rejects it.
2. The attempt and validation error details are logged to SQLite (`status = 'VALIDATION_ERROR'`).
3. An HTTP `422 Unprocessable Entity` response is returned to the client with descriptive error messages.

---

## 6. Actual Test Execution & Live Run Results

### Live Execution Output
During the live verification run, 4 distinct requests were submitted to `POST /predict`:

1. **Request 1 (Low-Risk Profile):**
   - Input: `{"age": 32, "sex": 0, "resting_bp": 110.0, "cholesterol": 170.0, "max_hr": 175.0}`
   - HTTP Status: `200 OK`
   - Output: `prediction: 0`, `risk_probability: 0.0202`, `risk_label: "Low"`
2. **Request 2 (High-Risk Profile):**
   - Input: `{"age": 65, "sex": 1, "resting_bp": 160.0, "cholesterol": 280.0, "max_hr": 110.0}`
   - HTTP Status: `200 OK`
   - Output: `prediction: 1`, `risk_probability: 0.9478`, `risk_label: "High"`
3. **Request 3 (Additional Valid Profile):**
   - Input: `{"age": 52, "sex": 1, "resting_bp": 130.0, "cholesterol": 220.0, "max_hr": 150.0}`
   - HTTP Status: `200 OK`
   - Output: `prediction: 1`, `risk_probability: 0.5254`, `risk_label: "High"`
4. **Request 4 (Invalid Input - Age 150):**
   - Input: `{"age": 150, "sex": 1, "resting_bp": 140.0, "cholesterol": 210.0, "max_hr": 130.0}`
   - HTTP Status: `422 Unprocessable Entity`
   - Detail: `body.age: Input should be less than or equal to 120`

### Actual `GET /stats` Response
```json
{
  "total_requests": 4,
  "successful_requests": 3,
  "failed_requests": 1,
  "average_predicted_risk": 0.4978,
  "high_risk_share": 0.6667
}
```
*Mathematical verification:*
- `average_predicted_risk` = `(0.0202 + 0.9478 + 0.5254) / 3` = `0.4978`
- `high_risk_share` = `2 / 3` = `0.6667`

---

## 7. Automated Test Suite

Located at `question_b/level_2/tests/test_api.py`.

### Test Cases
1. `test_valid_low_risk_prediction`: Verifies low-risk prediction output and checks that SQLite has 1 row with `status = 'SUCCESS'`.
2. `test_valid_high_risk_prediction`: Verifies high-risk classification and DB row.
3. `test_bad_input_validation_error_logged`: Sends `age = 150`, verifies HTTP 422, and confirms SQLite records row with `status = 'VALIDATION_ERROR'`.
4. `test_non_numeric_input_validation`: Sends string `"invalid_age"` for numeric field, verifies HTTP 422, and checks failure logging.
5. `test_stats_endpoint_sql_aggregation`: Sends mixed valid and invalid payloads, queries `/stats`, and verifies that SQL metrics match hand-calculated values.

### Database Isolation
The pytest fixture `isolate_test_db` creates a unique temporary database file via `tmp_path` and overrides `PREDICTIONS_DB_PATH` for each test. The production database is completely isolated and never touched during test execution.

---

## 8. Engineering Decisions & Trade-offs

### One Engineering Decision
- **Custom Request Validation Exception Handler:** Rather than letting FastAPI reject invalid requests before they reach the route handler (which would silently drop failed request tracking), we added a custom `RequestValidationError` handler. This intercepts invalid payloads, extracts any parseable fields and error details, logs the attempt to SQLite as `VALIDATION_ERROR`, and then returns the standard 422 status.

### One Rejected Alternative
- **Rejected Alternative:** Using an ORM (e.g., SQLAlchemy or SQLModel).
- **Reason Rejected:** ORMs introduce heavy dependencies, query compilation overhead, and unnecessary abstraction layers. For an embedded logging and aggregation use case, standard library `sqlite3` with parameterized SQL is significantly faster, completely transparent to review during a live interview, and strictly satisfies the requirement: *"NO ORM"*.

### Remaining Limitations
- **File-Based Lock Contention under Heavy Concurrency:** While SQLite WAL mode supports concurrent readers alongside a single writer, it is not distributed. Under sustained concurrent write traffic (e.g., hundreds of simultaneous writes), file locks may lead to `sqlite3.OperationalError: database is locked`. Architectural mitigations for higher concurrency (e.g., connection pooling, background write queues, or dedicated RDBMS) are addressed in Level 3.
