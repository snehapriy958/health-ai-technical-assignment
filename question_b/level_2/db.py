"""
SQLite Database Layer for Question B - Level 2
Hand-written SQL queries only. NO ORM (No SQLAlchemy, No SQLModel).
"""

import os
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any, Optional

DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "predictions.db"
)


def get_db_path() -> str:
    """Return configured database path (allows override for testing)."""
    return os.environ.get("PREDICTIONS_DB_PATH", DEFAULT_DB_PATH)


def init_db(db_path: Optional[str] = None) -> None:
    """
    Initialize SQLite database schema with WAL mode and table creation.
    Short-lived connection.
    """
    target_path = db_path or get_db_path()
    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)

    with sqlite3.connect(target_path, timeout=10.0) as conn:
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute(
            """
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
            """
        )
        conn.commit()


def log_prediction(
    status: str,
    age: Optional[float] = None,
    sex: Optional[float] = None,
    resting_bp: Optional[float] = None,
    cholesterol: Optional[float] = None,
    max_hr: Optional[float] = None,
    predicted_class: Optional[int] = None,
    predicted_risk_probability: Optional[float] = None,
    risk_label: Optional[str] = None,
    error_message: Optional[str] = None,
    db_path: Optional[str] = None,
) -> int:
    """
    Insert a prediction record (successful or failed validation) into SQLite
    using parameterized SQL.
    """
    target_path = db_path or get_db_path()
    now_utc = datetime.now(timezone.utc).isoformat()

    query = """
        INSERT INTO prediction_logs (
            timestamp,
            age,
            sex,
            resting_bp,
            cholesterol,
            max_hr,
            predicted_class,
            predicted_risk_probability,
            risk_label,
            status,
            error_message
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    params = (
        now_utc,
        age,
        sex,
        resting_bp,
        cholesterol,
        max_hr,
        predicted_class,
        predicted_risk_probability,
        risk_label,
        status,
        error_message,
    )

    with sqlite3.connect(target_path, timeout=10.0) as conn:
        cursor = conn.execute(query, params)
        conn.commit()
        return cursor.lastrowid


def get_stats(db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Compute aggregate prediction statistics using hand-written SQL.
    Distinguishes successful predictions from failed attempts.
    """
    target_path = db_path or get_db_path()

    query = """
        SELECT
            COUNT(*) AS total_requests,
            COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) AS successful_requests,
            COUNT(CASE WHEN status != 'SUCCESS' THEN 1 END) AS failed_requests,
            AVG(CASE WHEN status = 'SUCCESS' THEN predicted_risk_probability END) AS avg_risk,
            AVG(CASE WHEN status = 'SUCCESS' THEN (CASE WHEN predicted_class = 1 THEN 1.0 ELSE 0.0 END) END) AS high_risk_ratio
        FROM prediction_logs;
    """

    with sqlite3.connect(target_path, timeout=10.0) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(query)
        row = cursor.fetchone()

    total_requests = int(row["total_requests"]) if row and row["total_requests"] is not None else 0
    successful_requests = int(row["successful_requests"]) if row and row["successful_requests"] is not None else 0
    failed_requests = int(row["failed_requests"]) if row and row["failed_requests"] is not None else 0

    avg_risk = float(row["avg_risk"]) if row and row["avg_risk"] is not None else 0.0
    high_risk_share = float(row["high_risk_ratio"]) if row and row["high_risk_ratio"] is not None else 0.0

    return {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "average_predicted_risk": round(avg_risk, 4),
        "high_risk_share": round(high_risk_share, 4),
    }
