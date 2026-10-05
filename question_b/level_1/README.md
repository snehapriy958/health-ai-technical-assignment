# Question B — Level 1: Risk Prediction Application

## Overview

Level 1 serves a health risk classification model returning predicted probabilities and risk tier classifications via a FastAPI `/predict` endpoint and provides a lightweight single-page HTML frontend that presents the predicted risk in plain language.

**Personal Random Seed:** `S = 48`

---

## 1. Dataset Documentation

### Source & Variant
- **Repository:** UC Irvine Machine Learning Repository
- **Dataset:** Heart Disease Dataset (Cleveland Clinic variant)
- **Official URL:** `https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data`
- **Total records:** 303 patient records

### Original Columns
The raw Cleveland dataset contains 14 attributes:
1. `age`: Age in years
2. `sex`: Biological sex (1 = male, 0 = female)
3. `cp`: Chest pain type (1 = typical angina, 2 = atypical angina, 3 = non-anginal pain, 4 = asymptomatic)
4. `trestbps`: Resting blood pressure (mm Hg on admission)
5. `chol`: Serum cholesterol in mg/dL
6. `fbs`: Fasting blood sugar > 120 mg/dL (1 = true, 0 = false)
7. `restecg`: Resting electrocardiographic results (0 = normal, 1 = ST-T wave abnormality, 2 = left ventricular hypertrophy)
8. `thalach`: Maximum heart rate achieved during exercise (bpm)
9. `exang`: Exercise-induced angina (1 = yes, 0 = no)
10. `oldpeak`: ST depression induced by exercise relative to rest
11. `slope`: Slope of peak exercise ST segment (1 = upsloping, 2 = flat, 3 = downsloping)
12. `ca`: Number of major vessels (0–3) colored by fluoroscopy (contains missing values)
13. `thal`: Thallium heart scan (3 = normal, 6 = fixed defect, 7 = reversible defect; contains missing values)
14. `num`: Angiographic disease status (target)

### Target Mapping
- `num = 0`: Absence of significant coronary artery disease (< 50% diameter narrowing) $\rightarrow$ mapped to `0` (**Low Risk**).
- `num in {1, 2, 3, 4}`: Presence of significant coronary artery disease (> 50% diameter narrowing) $\rightarrow$ mapped to `1` (**High Risk**).

### Missing-Value Handling
- In the raw dataset, attributes `ca` (4 missing) and `thal` (2 missing) contain missing values encoded as `'?'`.
- The 5 selected features (`age`, `sex`, `trestbps`, `chol`, `thalach`) contain **zero missing values** across all 303 rows. No imputation is necessary for these features.

### Feature Selection Reasoning
We selected 5 core features:
1. `age`: Strong established demographic risk factor.
2. `sex`: Established epidemiological risk factor.
3. `resting_bp` (from `trestbps`): Standard vital sign measurable with a blood pressure cuff.
4. `cholesterol` (from `chol`): Standard lipid panel lab marker.
5. `max_hr` (from `thalach`): Cardiovascular fitness and autonomic indicator.

**Why these 5 were selected:**
- **Accessibility & Non-invasiveness:** Unlike invasive angiographic fluoroscopy (`ca`), nuclear medicine scans (`thal`), or specialized ECG interpretations (`restecg`, `oldpeak`, `slope`), these 5 markers represent standard vital signs and routine health metrics that an individual or wellness clinic can readily measure.
- **Walkthrough transparency:** A 5-input schema keeps the frontend clean, intuitive, and immediately explainable during a live technical walkthrough.
- **Strict feature ordering:** The model and API use identical ordering:
  `['age', 'sex', 'resting_bp', 'cholesterol', 'max_hr']`.

---

## 2. Model & Pipeline Architecture

- **Pipeline:** `sklearn.pipeline.Pipeline`
  1. `StandardScaler()`: Standardizes features to zero mean and unit variance.
  2. `LogisticRegression(random_state=48, max_iter=1000)`: Linear classification model.
- **Why Logistic Regression:**
  - Highly interpretable coefficients and odds ratios.
  - Native `predict_proba()` produces continuous probability estimates and risk tier classifications.
  - Bundling the scaler and classifier in a single pipeline guarantees zero train/test data leakage and prevents inference-time scaling discrepancies.
- **Reproducibility:** Seed `S = 48` is used for `train_test_split(..., random_state=48, stratify=y)` (80/20 train/test split) and inside `LogisticRegression(random_state=48)`.
- **Artifact:** Saved to `model.joblib` via `joblib.dump()`. This artifact is excluded from version control via `.gitignore`.

---

## 3. Actual Evaluation Results (Seed 48)

The following metrics were obtained by executing `python question_b/level_1/train.py`:

- **Dataset Split:**
  - Total records: 303
  - Training samples: 242 (131 Low Risk, 111 High Risk)
  - Test samples: 61 (33 Low Risk, 28 High Risk)

- **Test Metrics:**
  - **Accuracy:** `0.7377` (73.77%, 45 / 61 correct)
  - **Precision:** `0.7500` (75.00%)
  - **Recall:** `0.6429` (64.29%)
  - **F1-Score:** `0.6923`
  - **ROC-AUC:** `0.7955`

- **Learned Standardized Coefficients:**
  - `age`: `+0.1955` (increasing age increases risk)
  - `sex`: `+0.8751` (male sex increases risk in this cohort)
  - `resting_bp`: `+0.2986` (higher blood pressure increases risk)
  - `cholesterol`: `+0.3588` (higher cholesterol increases risk)
  - `max_hr`: `-0.8903` (lower max heart rate capacity increases risk)
  - `intercept`: `-0.2309`

---

## 4. API Endpoints

### `GET /`
Serves the lightweight HTML frontend.

### `GET /health`
Returns service status and whether `model.joblib` is loaded:
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### `POST /predict`
Validates input and returns the risk assessment.

**Input Validation Rules:**
- `age`: integer, `1 <= age <= 120`
- `sex`: integer, `0` (Female) or `1` (Male)
- `resting_bp`: float, `50.0 <= resting_bp <= 250.0` (mm Hg)
- `cholesterol`: float, `80.0 <= cholesterol <= 600.0` (mg/dL)
- `max_hr`: float, `50.0 <= max_hr <= 250.0` (bpm)

**Sample Request:**
```json
{
  "age": 58,
  "sex": 1,
  "resting_bp": 135.0,
  "cholesterol": 240.0,
  "max_hr": 140.0
}
```

**Sample Response:**
```json
{
  "prediction": 1,
  "risk_probability": 0.7014,
  "risk_label": "High",
  "summary": "Predicted risk: High",
  "estimated_probability": "Estimated model probability: 70.1%",
  "disclaimer": "This is a model prediction, not a medical diagnosis."
}
```

---

## 5. How to Run

### Step 1: Train Model
From repository root:
```bash
python question_b/level_1/train.py
```
This fetches the official dataset from UCI (cached to `data/processed.cleveland.data`), trains the pipeline using seed 48, reports all metrics, and saves `question_b/level_1/model.joblib`.

### Step 2: Start the Web Application
```bash
uvicorn question_b.level_1.app:app --host 127.0.0.1 --port 8000 --reload
```

### Step 3: Access Frontend
Open browser at:
```
http://127.0.0.1:8000
```
Enter values and click **"Assess Risk"** to see plain-language outputs.
