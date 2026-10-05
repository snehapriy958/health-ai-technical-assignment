"""
Failure Demonstration Script for Question B - Level 3

Demonstrates:
1. Missing model artifact: behavior before fix (unhandled 500/crash) vs after fix (HTTP 503 + degraded health).
2. Wrong input type: scikit-learn failure vs safe HTTP 422 validation intercept and DB logging.
"""

import os
import sys
import json
import sqlite3

# Ensure repository root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import pandas as pd
from fastapi.testclient import TestClient

from question_b.level_1.model import load_model, DEFAULT_MODEL_PATH
from question_b.level_2.app import app, ml_models
from question_b.level_2.db import get_db_path


def run_failure_1_demo():
    print("=" * 60)
    print("FAILURE 1 DEMONSTRATION: Missing Model Artifact")
    print("=" * 60)

    model_path = DEFAULT_MODEL_PATH
    backup_path = model_path + ".bak"

    # Step 1: Temporarily simulate missing model artifact
    if os.path.exists(model_path):
        os.rename(model_path, backup_path)
        print(f"[1] Renamed '{model_path}' to '{backup_path}'")

    try:
        # Clear in-memory cached model
        ml_models.clear()

        with TestClient(app) as client:
            # Check health endpoint
            r_health = client.get("/health")
            print(f"[2] GET /health response: status={r_health.status_code}, body={r_health.json()}")

            # Attempt prediction
            payload = {"age": 55, "sex": 1, "resting_bp": 130.0, "cholesterol": 230.0, "max_hr": 145.0}
            r_pred = client.post("/predict", json=payload)
            print(f"[3] POST /predict response: status={r_pred.status_code}, body={r_pred.json()}")

    finally:
        # Step 2: Restore model artifact
        if os.path.exists(backup_path):
            os.rename(backup_path, model_path)
            print(f"[4] Restored '{model_path}'")

    # Step 3: Verify restored state
    ml_models.clear()
    with TestClient(app) as client:
        r_health_restored = client.get("/health")
        print(f"[5] Restored GET /health: status={r_health_restored.status_code}, body={r_health_restored.json()}")
        r_pred_restored = client.post("/predict", json=payload)
        print(f"[6] Restored POST /predict: status={r_pred_restored.status_code}, body={r_pred_restored.json()}")


def run_failure_2_demo():
    print("\n" + "=" * 60)
    print("FAILURE 2 DEMONSTRATION: Incompatible Input Type")
    print("=" * 60)

    # 1. Unvalidated pipeline behavior
    print("[1] Simulating unvalidated input directly passed to scikit-learn pipeline:")
    model = load_model()
    raw_bad_input = pd.DataFrame([["fifty", 1, 130.0, 230.0, 145.0]], columns=["age", "sex", "resting_bp", "cholesterol", "max_hr"])
    try:
        model.predict(raw_bad_input)
    except Exception as exc:
        print(f"    Direct scikit-learn failure: {type(exc).__name__}: {str(exc)}")

    # 2. Hardened FastAPI + Pydantic behavior
    print("\n[2] Testing request through FastAPI + Pydantic validation layer:")
    with TestClient(app) as client:
        bad_payload = {"age": "fifty", "sex": 1, "resting_bp": 130.0, "cholesterol": 230.0, "max_hr": 145.0}
        resp = client.post("/predict", json=bad_payload)
        print(f"    HTTP Status: {resp.status_code}")
        print(f"    HTTP Response Body: {resp.json()}")

    # 3. Check SQLite failure logging
    print("\n[3] Checking failure persistence in SQLite:")
    with sqlite3.connect(get_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id, timestamp, age, status, error_message FROM prediction_logs WHERE status = 'VALIDATION_ERROR' ORDER BY id DESC LIMIT 1;"
        ).fetchone()
        if row:
            print(f"    Logged Row: id={row['id']}, status='{row['status']}', error='{row['error_message']}'")


if __name__ == "__main__":
    run_failure_1_demo()
    run_failure_2_demo()
