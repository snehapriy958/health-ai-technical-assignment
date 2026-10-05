"""
Automated Pytest Tests for Question B - Level 2
Ensures database isolation using temporary test SQLite databases.
"""

import os
import sqlite3
import pytest
from fastapi.testclient import TestClient

from question_b.level_2.db import init_db
from question_b.level_2.app import app


@pytest.fixture(autouse=True)
def isolate_test_db(tmp_path, monkeypatch):
    """
    Isolate test database using a temporary path for each test function.
    Guarantees the live application database is never touched.
    """
    test_db = str(tmp_path / "test_predictions.db")
    monkeypatch.setenv("PREDICTIONS_DB_PATH", test_db)
    init_db(test_db)
    yield test_db


@pytest.fixture
def client():
    """FastAPI TestClient context manager."""
    with TestClient(app) as test_client:
        yield test_client


def test_valid_low_risk_prediction(client, isolate_test_db):
    """Test valid prediction for a low-risk profile and check DB persistence."""
    payload = {
        "age": 30,
        "sex": 0,
        "resting_bp": 110.0,
        "cholesterol": 160.0,
        "max_hr": 180.0,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == 0
    assert data["risk_label"] == "Low"
    assert "Predicted risk: Low" in data["summary"]
    assert "This is a model prediction, not a medical diagnosis." in data["disclaimer"]

    # Verify DB persistence
    with sqlite3.connect(isolate_test_db) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM prediction_logs;")
        rows = cursor.fetchall()
        assert len(rows) == 1
        row = rows[0]
        assert row["status"] == "SUCCESS"
        assert row["age"] == 30.0
        assert row["sex"] == 0.0
        assert row["predicted_class"] == 0
        assert row["predicted_risk_probability"] == data["risk_probability"]
        assert row["error_message"] is None


def test_valid_high_risk_prediction(client, isolate_test_db):
    """Test valid prediction for a high-risk profile and check DB persistence."""
    payload = {
        "age": 65,
        "sex": 1,
        "resting_bp": 160.0,
        "cholesterol": 280.0,
        "max_hr": 110.0,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == 1
    assert data["risk_label"] == "High"
    assert "Predicted risk: High" in data["summary"]

    with sqlite3.connect(isolate_test_db) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM prediction_logs WHERE status = 'SUCCESS';")
        rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0]["predicted_class"] == 1
        assert rows[0]["risk_label"] == "High"


def test_bad_input_validation_error_logged(client, isolate_test_db):
    """Test that input validation failures return 422 and are recorded in DB."""
    # Bad age: 150 (greater than 120)
    bad_payload = {
        "age": 150,
        "sex": 1,
        "resting_bp": 130.0,
        "cholesterol": 220.0,
        "max_hr": 140.0,
    }
    response = client.post("/predict", json=bad_payload)
    assert response.status_code == 422
    err_body = response.json()
    assert "detail" in err_body
    assert any("120" in str(err) for err in err_body["detail"])

    # Verify failure is recorded in SQLite
    with sqlite3.connect(isolate_test_db) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM prediction_logs;")
        rows = cursor.fetchall()
        assert len(rows) == 1
        row = rows[0]
        assert row["status"] == "VALIDATION_ERROR"
        assert row["age"] == 150.0
        assert "less_than_equal" in row["error_message"] or "120" in row["error_message"]
        assert row["predicted_class"] is None
        assert row["predicted_risk_probability"] is None


def test_non_numeric_input_validation(client, isolate_test_db):
    """Test that string sent for numeric field returns 422 and logs to DB."""
    bad_payload = {
        "age": "invalid_age",
        "sex": 1,
        "resting_bp": 130.0,
        "cholesterol": 220.0,
        "max_hr": 140.0,
    }
    response = client.post("/predict", json=bad_payload)
    assert response.status_code == 422

    with sqlite3.connect(isolate_test_db) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM prediction_logs;")
        rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0]["status"] == "VALIDATION_ERROR"


def test_stats_endpoint_sql_aggregation(client, isolate_test_db):
    """
    Test /stats computation via hand-written SQL:
    Makes 2 successful requests (1 high risk, 1 low risk) and 1 invalid request,
    then verifies exact metrics.
    """
    # 1. High-risk profile
    client.post(
        "/predict",
        json={"age": 65, "sex": 1, "resting_bp": 160.0, "cholesterol": 280.0, "max_hr": 110.0},
    )
    # 2. Low-risk profile
    client.post(
        "/predict",
        json={"age": 30, "sex": 0, "resting_bp": 110.0, "cholesterol": 160.0, "max_hr": 180.0},
    )
    # 3. Invalid request (out of bounds)
    client.post(
        "/predict",
        json={"age": 150, "sex": 1, "resting_bp": 130.0, "cholesterol": 220.0, "max_hr": 140.0},
    )

    stats_resp = client.get("/stats")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()

    assert stats["total_requests"] == 3
    assert stats["successful_requests"] == 2
    assert stats["failed_requests"] == 1

    # Hand calculate expected average from DB rows
    with sqlite3.connect(isolate_test_db) as conn:
        cursor = conn.execute(
            "SELECT AVG(predicted_risk_probability) FROM prediction_logs WHERE status = 'SUCCESS';"
        )
        expected_avg = round(cursor.fetchone()[0], 4)

    assert stats["average_predicted_risk"] == expected_avg
    # Out of 2 successful, 1 is high risk -> 0.50
    assert stats["high_risk_share"] == 0.50
