# Question B — Risk Prediction Application

## Objective

Build a small health-risk prediction application around a trained
machine-learning model.

## Level 1

Requirements:

1. Train a classification model.
2. Serve the model through FastAPI or Flask.
3. Implement a `/predict` endpoint.
4. Create a small frontend.
5. Display the predicted risk clearly to the user.

## Level 2

Requirements:

1. Store prediction requests and results in a database.
2. Implement `/stats`.
3. Use hand-written SQL rather than an ORM.
4. Return:
   - Total prediction requests
   - Average predicted risk
   - Share of high-risk predictions
5. Validate inputs.
6. Write at least three pytest tests, including invalid input.

## Level 3

Requirements:

1. Intentionally break the application in two different ways.
2. Demonstrate the failures.
3. Diagnose and fix them.
4. Explain the engineering decisions.
5. Discuss safety considerations for approximately 100 concurrent users.

## Personal Seed

`S = 48`

The same seed must be used wherever randomness is involved.

## Run Instructions

### 1. Train Model (Level 1)
```bash
python question_b/level_1/train.py
```
Trains Logistic Regression on 5 UCI Cleveland features (`age`, `sex`, `resting_bp`, `cholesterol`, `max_hr`) with `random_state=48`, evaluates on the test split, and saves `model.joblib`.

### 2. Run API Server (Level 2)
```bash
uvicorn question_b.level_2.app:app --host 127.0.0.1 --port 8000
```
Provides:
- `POST /predict`: Performs inference, returns predicted probabilities and risk tier classifications, and logs request/result to SQLite (`predictions.db`).
- `GET /stats`: Computes aggregations via hand-written SQL (zero ORM).
- `GET /`: Serves the single-page HTML frontend.

### 3. Run Automated Tests
```bash
pytest question_b/level_2/tests/test_api.py -v
```

### 4. Run Level 3 Failure Experiments & Concurrency Benchmark
```bash
python question_b/level_3/run_failure_experiments.py
python question_b/level_3/load_test.py
```

---

## Experimental Results

### Model Performance (Level 1, Seed 48)
- Test Accuracy: `73.77%` (45 / 61 correct)
- Test ROC-AUC: `0.7955`
- Outputs: Continuous predicted probabilities and risk tier classifications ("High" vs. "Low Risk").

### Persistent Logging & SQL (Level 2)
- Tested with mixed valid and invalid payloads.
- Hand-written SQL aggregations verified against expected values.

### Level 3 Intentional Failure Experiments
1. **Failure 1 — Missing Trained Model Artifact:**
   - Removing/renaming `model.joblib`.
   - `GET /health` reports `status = "degraded"` (`model_loaded: false`).
   - `POST /predict` returns HTTP 503 with a diagnostic error message.
   - Restoring the model file recovers normal prediction operation.
2. **Failure 2 — Wrong Input Type:**
   - Input payload containing `age="fifty"`.
   - Direct unvalidated model inference raises `ValueError: could not convert string to float: 'fifty'`.
   - FastAPI / Pydantic schema validation intercepts the malformed payload before inference.
   - The API returns HTTP 422 and records `status = 'VALIDATION_ERROR'` into SQLite.

### Separate 100-User Concurrency / Load Test
- Dispatched 100 concurrent asynchronous requests against `POST /predict`.
- Result: 100/100 HTTP 200 responses, 100 persisted SQLite records in WAL mode.
- Note: This concurrency benchmark is evaluated separately from the two intentional failure experiments above.
