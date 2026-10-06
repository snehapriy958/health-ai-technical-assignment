# Question B — Level 3 Final Predictions

**Seed**: `S = 48`
**Evaluation cycle**: FINAL PREDICTION-BEFORE-TEST CYCLE

> [!IMPORTANT]
> **Chronology Statement**:
> "These predictions are frozen and committed to GitHub before the final Level 3 evaluation is executed. They represent my pre-test reasoning, not conclusions derived from the evaluation results."

---

### TEST 1 — Missing Model Artifact (`model.joblib`)

- **Test/Scenario**: Removing or renaming the trained model artifact (`model.joblib`) during application operation.
- **My Prediction**:
  - `GET /health` should indicate a degraded / unavailable model state (`"status": "degraded"`, `"model_loaded": false`).
  - `POST /predict` should return a controlled **HTTP 503 Service Unavailable** rather than an unhandled 500 or process crash.
  - The API process should remain alive and responsive.
  - Restoring the model file should recover normal prediction behavior without requiring an application restart.
- **My Reasoning**:
  The application uses a FastAPI lifespan handler and lazy model loader that catches `FileNotFoundError` gracefully, isolating missing file dependencies from process lifetime.

---

### TEST 2 — Invalid / Non-Numeric Input (`age = "fifty"`)

- **Test/Scenario**: Submitting non-numeric string data to a numerical clinical feature (`POST /predict` with `age = "fifty"`).
- **My Prediction**:
  - Invalid input such as a string where a numeric field is required should be rejected by Pydantic before model execution.
  - The API should return **HTTP 422 Unprocessable Entity**.
  - The invalid input should not reach the machine learning model (preventing Scikit-learn `ValueError`).
  - The validation failure should be recorded in SQLite with `status = 'VALIDATION_ERROR'` via the custom exception handler.
- **My Reasoning**:
  FastAPI schema validation operates at the ASGI deserialization boundary before route execution. The custom `RequestValidationError` handler intercepts the rejection to persist audit logs to SQLite.

---

### TEST 3 — 100 Concurrent Requests Load Test

- **Test/Scenario**: 100 simultaneous concurrent asynchronous requests dispatched to `POST /predict`.
- **My Prediction**:
  - 100 concurrent requests should complete without uncontrolled application crashes or data corruption.
  - SQLite Write-Ahead Logging (WAL) and short transactions with busy timeouts should be adequate for this bounded evaluation (100% success rate expected).
  - Average and tail latencies will exhibit queuing delays due to serialized SQLite file writes.
  - Higher continuous write concurrency in production would justify PostgreSQL or another dedicated client-server database.
- **My Reasoning**:
  SQLite WAL mode allows concurrent readers alongside a single writer. For 100 burst requests, short transaction scopes allow requests to serialize cleanly without timeout deadlocks, but write serialization creates measurable tail latency.
