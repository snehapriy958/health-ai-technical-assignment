"""
Model Loading and Inference Schemas for Question B - Level 1
Personal Seed: S = 48
"""

import os
import joblib
import pandas as pd
from pydantic import BaseModel, Field

# Canonical feature ordering: must exactly match training feature order
FEATURE_NAMES = ["age", "sex", "resting_bp", "cholesterol", "max_hr"]

DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "model.joblib"
)


class PredictionInput(BaseModel):
    age: int = Field(
        ...,
        ge=1,
        le=120,
        description="Patient age in years (1 to 120)",
        examples=[58],
    )
    sex: int = Field(
        ...,
        ge=0,
        le=1,
        description="Biological sex: 0 = Female, 1 = Male",
        examples=[1],
    )
    resting_bp: float = Field(
        ...,
        ge=50.0,
        le=250.0,
        description="Resting blood pressure in mm Hg (50 to 250)",
        examples=[135.0],
    )
    cholesterol: float = Field(
        ...,
        ge=80.0,
        le=600.0,
        description="Serum cholesterol in mg/dL (80 to 600)",
        examples=[240.0],
    )
    max_hr: float = Field(
        ...,
        ge=50.0,
        le=250.0,
        description="Maximum heart rate achieved in bpm (50 to 250)",
        examples=[140.0],
    )


class PredictionOutput(BaseModel):
    prediction: int = Field(..., description="Binary classification (0 = Low Risk, 1 = High Risk)")
    risk_probability: float = Field(..., description="Estimated model risk probability between 0.0 and 1.0")
    risk_label: str = Field(..., description="Human-readable category: 'High' or 'Low'")
    summary: str = Field(..., description="Plain-language summary sentence")
    estimated_probability: str = Field(..., description="Formatted probability percentage")
    disclaimer: str = Field(..., description="Medical disclaimer")


def load_model(model_path: str = None):
    """Load the trained scikit-learn pipeline from disk."""
    if model_path is None:
        model_path = DEFAULT_MODEL_PATH

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Trained model not found at {model_path}. "
            f"Please run train.py first to generate model.joblib."
        )
    return joblib.load(model_path)


def predict(model, input_data: PredictionInput) -> PredictionOutput:
    """
    Run model prediction on validated input data.
    Ensures input features are in the exact order expected by the pipeline.
    """
    input_df = pd.DataFrame(
        [
            [
                input_data.age,
                input_data.sex,
                input_data.resting_bp,
                input_data.cholesterol,
                input_data.max_hr,
            ]
        ],
        columns=FEATURE_NAMES,
    )

    pred = int(model.predict(input_df)[0])
    prob = float(model.predict_proba(input_df)[0, 1])

    risk_label = "High" if pred == 1 else "Low"
    prob_percentage = round(prob * 100, 1)

    return PredictionOutput(
        prediction=pred,
        risk_probability=round(prob, 4),
        risk_label=risk_label,
        summary=f"Predicted risk: {risk_label}",
        estimated_probability=f"Estimated model probability: {prob_percentage:.1f}%",
        disclaimer="This is a model prediction, not a medical diagnosis.",
    )
