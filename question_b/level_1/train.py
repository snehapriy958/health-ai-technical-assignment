"""
Model Training Script for Question B - Level 1
Personal Seed: S = 48

Dataset: UCI Heart Disease (Cleveland clinic)
URL: https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data
"""

import os
import urllib.request
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
)
import joblib

# Deterministic seed as specified by the assignment
SEED = 48

# Canonical feature names and ordering
FEATURE_NAMES = ["age", "sex", "resting_bp", "cholesterol", "max_hr"]

# Original columns in processed.cleveland.data
RAW_COLUMNS = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
    "num",
]

UCI_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"


def load_data(data_path: str = None) -> pd.DataFrame:
    """Load or download the official UCI Cleveland heart disease dataset."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    if data_path is None:
        data_path = os.path.join(data_dir, "processed.cleveland.data")

    if not os.path.exists(data_path):
        print(f"Downloading official dataset from {UCI_URL} ...")
        urllib.request.urlretrieve(UCI_URL, data_path)
        print(f"Downloaded dataset to {data_path}")

    # The dataset uses '?' for missing values
    df = pd.read_csv(data_path, names=RAW_COLUMNS, na_values="?")

    # Rename columns to human-readable names matching the API
    rename_dict = {
        "trestbps": "resting_bp",
        "chol": "cholesterol",
        "thalach": "max_hr",
    }
    df = df.rename(columns=rename_dict)
    return df


def train_and_evaluate(data_path: str = None, model_output_path: str = None):
    """
    Train a Logistic Regression pipeline with StandardScaler using SEED=48
    and save the pipeline to disk.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if model_output_path is None:
        model_output_path = os.path.join(base_dir, "model.joblib")

    df = load_data(data_path)

    # Validate missing values in selected features
    missing_counts = df[FEATURE_NAMES].isna().sum()
    print("Missing values in selected features:")
    for feat in FEATURE_NAMES:
        print(f"  {feat}: {missing_counts[feat]}")

    # Target: 0 = absence of disease, 1-4 = presence of disease (mapped to binary 0/1)
    X = df[FEATURE_NAMES].copy()
    y = (df["num"] > 0).astype(int)

    # Train / test split using SEED=48
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=SEED,
        stratify=y,
    )

    print(f"\nDataset size: {len(df)} records")
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set:     {len(X_test)} samples")
    print(f"Class distribution (train): {np.bincount(y_train)}")
    print(f"Class distribution (test):  {np.bincount(y_test)}")

    # Pipeline: StandardScaler + LogisticRegression
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(random_state=SEED, max_iter=1000)),
        ]
    )

    # Fit pipeline
    pipeline.fit(X_train, y_train)

    # Predictions
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    # Metrics
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)

    print("\n" + "=" * 50)
    print("ACTUAL EVALUATION METRICS ON TEST SET (SEED = 48)")
    print("=" * 50)
    print(f"Accuracy:  {acc:.4f} ({acc * 100:.2f}%)")
    print(f"Precision: {prec:.4f} ({prec * 100:.2f}%)")
    print(f"Recall:    {rec:.4f} ({rec * 100:.2f}%)")
    print(f"F1-Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Low Risk (0)", "High Risk (1)"]))

    # Model coefficients
    clf = pipeline.named_steps["classifier"]
    print("Learned Model Coefficients (Standardized):")
    for feat, coef in zip(FEATURE_NAMES, clf.coef_[0]):
        print(f"  {feat:15s}: {coef:+.4f}")
    print(f"  {'intercept':15s}: {clf.intercept_[0]:+.4f}")

    # Save pipeline
    joblib.dump(pipeline, model_output_path)
    print(f"\nModel pipeline successfully saved to: {model_output_path}")

    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "roc_auc": roc_auc,
        "pipeline": pipeline,
    }


if __name__ == "__main__":
    train_and_evaluate()
