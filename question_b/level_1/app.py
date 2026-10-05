"""
FastAPI Application for Question B - Level 1
Personal Seed: S = 48
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from question_b.level_1.model import (
    PredictionInput,
    PredictionOutput,
    load_model,
    predict,
    DEFAULT_MODEL_PATH,
)

# Application state container for loaded model
ml_models = {}

STATIC_INDEX_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "static", "index.html"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model pipeline on startup."""
    try:
        ml_models["pipeline"] = load_model()
    except FileNotFoundError as err:
        # Allow starting, but predict will return 503 if model is missing
        ml_models["pipeline"] = None
        print(f"Warning on startup: {err}")
    yield
    ml_models.clear()


app = FastAPI(
    title="Health Risk Prediction API - Level 1",
    description="Serves a Logistic Regression model (Seed: 48) on UCI Heart Disease features, returning predicted probabilities and risk tier classifications.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", response_class=FileResponse, summary="Serve Frontend UI")
async def serve_frontend():
    """Serves the minimal single-page HTML frontend."""
    if not os.path.exists(STATIC_INDEX_PATH):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frontend index.html not found.",
        )
    return FileResponse(STATIC_INDEX_PATH)


@app.get("/health", summary="Health Check")
async def health_check():
    """Returns application health and model readiness status."""
    if ml_models.get("pipeline") is None:
        try:
            ml_models["pipeline"] = load_model()
        except FileNotFoundError:
            pass
    is_ready = ml_models.get("pipeline") is not None
    return {
        "status": "healthy" if is_ready else "degraded",
        "model_loaded": is_ready,
    }


@app.post(
    "/predict",
    response_model=PredictionOutput,
    summary="Predict Health Risk",
    status_code=status.HTTP_200_OK,
)
async def predict_endpoint(payload: PredictionInput):
    """
    Accepts validated clinical features and returns:
    - predicted risk category ("High" or "Low")
    - predicted probabilities and risk tier classifications
    - plain-language summary and disclaimer
    """
    pipeline = ml_models.get("pipeline")
    if pipeline is None:
        # Attempt lazy reload in case model was trained after startup
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
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(exc)}",
        )
