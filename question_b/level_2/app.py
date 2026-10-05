"""
FastAPI Application for Question B - Level 2
Persistent SQLite Logging (No ORM) and /stats Endpoint
Personal Seed: S = 48
"""

import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field

from question_b.level_1.model import (
    PredictionInput,
    PredictionOutput,
    load_model,
    predict,
    DEFAULT_MODEL_PATH,
)
from question_b.level_2.db import init_db, log_prediction, get_stats, get_db_path

STATIC_INDEX_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "level_1", "static", "index.html"
)

ml_models = {}


class StatsResponse(BaseModel):
    total_requests: int = Field(..., description="Total requests logged including failed attempts")
    successful_requests: int = Field(..., description="Total successful prediction requests")
    failed_requests: int = Field(..., description="Total failed or invalid prediction requests")
    average_predicted_risk: float = Field(..., description="Average predicted risk probability across successful predictions")
    high_risk_share: float = Field(..., description="Proportion of successful predictions classified as High Risk")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB and load trained model pipeline on startup."""
    init_db()
    try:
        ml_models["pipeline"] = load_model()
    except FileNotFoundError as err:
        ml_models["pipeline"] = None
        print(f"Warning on Level 2 startup: {err}")
    yield
    ml_models.clear()


app = FastAPI(
    title="Health Risk Prediction API - Level 2",
    description="Persistent SQLite Logging (No ORM), /stats Endpoint, Seed: 48",
    version="2.0.0",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Capture invalid prediction requests, log them to SQLite with failure details,
    and return standard 422 response.
    """
    raw_body = None
    parsed_json = {}
    try:
        body_bytes = await request.body()
        if body_bytes:
            raw_body = body_bytes.decode("utf-8")
            parsed_json = json.loads(raw_body)
    except Exception:
        pass

    errors_summary = "; ".join(
        f"{'.'.join(str(loc) for loc in err.get('loc', []))}: {err.get('msg')}"
        for err in exc.errors()
    )

    # Safely extract any numeric feature values that were provided
    def safe_float(val):
        try:
            return float(val) if val is not None else None
        except (ValueError, TypeError):
            return None

    if request.url.path.endswith("/predict"):
        log_prediction(
            status="VALIDATION_ERROR",
            age=safe_float(parsed_json.get("age")),
            sex=safe_float(parsed_json.get("sex")),
            resting_bp=safe_float(parsed_json.get("resting_bp")),
            cholesterol=safe_float(parsed_json.get("cholesterol")),
            max_hr=safe_float(parsed_json.get("max_hr")),
            error_message=errors_summary,
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.get("/", response_class=FileResponse, summary="Serve Frontend UI")
async def serve_frontend():
    """Serves the minimal single-page HTML frontend from Level 1."""
    if not os.path.exists(STATIC_INDEX_PATH):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frontend index.html not found.",
        )
    return FileResponse(STATIC_INDEX_PATH)


@app.get("/health", summary="Health Check")
async def health_check():
    """Returns application, model, and database status."""
    if ml_models.get("pipeline") is None:
        try:
            ml_models["pipeline"] = load_model()
        except FileNotFoundError:
            pass
    is_ready = ml_models.get("pipeline") is not None
    return {
        "status": "healthy" if is_ready else "degraded",
        "model_loaded": is_ready,
        "database_path": get_db_path(),
    }


@app.post(
    "/predict",
    response_model=PredictionOutput,
    summary="Predict Health Risk and Log to SQLite",
    status_code=status.HTTP_200_OK,
)
async def predict_endpoint(payload: PredictionInput):
    """
    Accepts validated clinical features, performs inference, logs request/result
    to SQLite, and returns structured prediction.
    """
    pipeline = ml_models.get("pipeline")
    if pipeline is None:
        try:
            pipeline = load_model()
            ml_models["pipeline"] = pipeline
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Trained model artifact not found. Please run train.py first.",
            )

    try:
        result = predict(pipeline, payload)

        # Log successful prediction to SQLite
        log_prediction(
            status="SUCCESS",
            age=float(payload.age),
            sex=float(payload.sex),
            resting_bp=float(payload.resting_bp),
            cholesterol=float(payload.cholesterol),
            max_hr=float(payload.max_hr),
            predicted_class=result.prediction,
            predicted_risk_probability=result.risk_probability,
            risk_label=result.risk_label,
            error_message=None,
        )

        return result
    except Exception as exc:
        # Log internal inference failure if any occurs
        log_prediction(
            status="INFERENCE_ERROR",
            age=float(payload.age),
            sex=float(payload.sex),
            resting_bp=float(payload.resting_bp),
            cholesterol=float(payload.cholesterol),
            max_hr=float(payload.max_hr),
            error_message=str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(exc)}",
        )


@app.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get Prediction Aggregations via Hand-Written SQL",
    status_code=status.HTTP_200_OK,
)
async def stats_endpoint():
    """
    Computes and returns request summary metrics using hand-written SQL.
    - total_requests: all logged requests (successful + failed)
    - average_predicted_risk: mean probability across successful predictions
    - high_risk_share: fraction of successful predictions classified as high risk
    """
    stats_data = get_stats()
    return StatsResponse(**stats_data)
