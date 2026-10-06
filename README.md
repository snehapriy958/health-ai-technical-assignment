# AI for Personal Health and Wellness — Technical Assignment

**Candidate:** Sneha Kumari  
**Program:** B.E. Artificial Intelligence and Machine Learning  
**Personal Seed (S):** 48  
**Selected Questions:** B and C

## Overview

This repository contains my solutions for Questions B and C of the
Technical Assignment: AI for Personal Health and Wellness.

The assignment focuses on building practical AI systems and demonstrating
engineering decisions, implementation depth, testing, failure analysis,
and personal reasoning.

## Questions

### Question B — Risk Prediction Application

Levels covered:

- Level 1: Serve a trained ML model through an API and frontend.
- Level 2: Persist prediction requests/results, expose statistics through
  hand-written SQL, validate inputs, and write tests.
- Level 3: Intentionally introduce failures, debug them, and discuss
  safety considerations for concurrent users.

### Question C — Trusted Health QA Assistant

Levels covered:

- Level 1: Build a document-grounded RAG/LLM question-answering system.
- Level 2: Implement document chunking, TF-IDF retrieval, and cosine
  similarity manually using NumPy.
- Level 3: Evaluate the system using predicted failure cases and
  unanswerable questions.

## Personal Seed

The personal seed is:

`S = 48`

The seed is used consistently wherever randomness is involved in
data splitting, model training, or experiments.

## Repository Structure

```text
question_b/
├── README.md
├── level_1/
│   ├── app.py
│   ├── train.py
│   ├── model.joblib
│   └── static/index.html
├── level_2/
│   ├── app.py
│   ├── db.py
│   ├── static/index.html
│   └── tests/test_api.py
└── level_3/
    ├── README.md
    ├── predictions.md
    ├── failure_comparison.md
    ├── run_failure_experiments.py
    └── load_test.py

question_c/
├── README.md
├── documents/
│   ├── who_diabetes.txt
│   ├── who_hypertension.txt
│   ├── who_physical_activity.txt
│   ├── who_healthy_diet.txt
│   └── who_obesity.txt
├── level_1/
│   ├── app.py
│   ├── chunker.py
│   ├── retriever.py
│   ├── llm.py
│   ├── rag_pipeline.py
│   ├── static/index.html
│   └── tests/test_rag.py
├── level_2/
│   ├── custom_tfidf.py
│   ├── compare_retrievers.py
│   └── test_custom_retriever.py
└── level_3/
    ├── README.md
    ├── predictions.md
    ├── ai_prediction_review.md
    ├── run_evaluation.py
    ├── analyze_failure.py
    └── results.md

PERSONAL_INTELLIGENCE.md
```

## Quick Start & Verification

### Running All Automated Tests
```bash
pytest -v
```
(24 automated unit and integration tests covering API endpoints, RAG pipeline, and custom NumPy TF-IDF).

### Question B: Run Risk Prediction App
```bash
# Start FastAPI application with SQLite persistence (Level 2)
uvicorn question_b.level_2.app:app --host 127.0.0.1 --port 8000
```
Open `http://127.0.0.1:8000` for the web UI, or `http://127.0.0.1:8000/stats` for hand-written SQL statistics.

### Question C: Run Health Assistant App
```bash
# Start Document-grounded RAG Assistant (Level 1)
uvicorn question_c.level_1.app:app --host 127.0.0.1 --port 8012
```
Open `http://127.0.0.1:8012` for the question-answering interface with citation attribution.

## Key Reports & Reflections
- [PERSONAL_INTELLIGENCE.md](PERSONAL_INTELLIGENCE.md): Architectural decisions (chosen vs. rejected), Level 3 failure taxonomy, AI tool usage disclosure and weakness resolution.
- [question_b/level_3/failure_comparison.md](question_b/level_3/failure_comparison.md): Intentional failure hardening (missing model 503, invalid input 422) and 100 concurrent requests evaluation.
- [question_c/level_3/results.md](question_c/level_3/results.md): 10-query pre-registered evaluation results, 90% prediction accuracy, 80% QA correctness, and detailed retrieval vs. generation failure taxonomy.